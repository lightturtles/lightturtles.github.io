#!/usr/bin/env python3
"""
badgetool.py: back up, update, and restore the files on a MicroPython badge
by comparing them to a FOLDER of official firmware files (e.g. the `badge/`
folder from the badge's GitHub repo).

    python badgetool.py diff    FOLDER          What's different, and what each command would do
    python badgetool.py diff    FOLDER FILE     Line-by-line diff of one file (badge vs. FOLDER)
    python badgetool.py backup  FOLDER          Copy your files from the badge to backups/<date-time>/
    python badgetool.py update  FOLDER          Install a new FOLDER, keeping your files
    python badgetool.py restore FOLDER          Make the badge match FOLDER (keeps the badge's data)

Options:
    --port PORT     Which serial port (default: let mpremote find the badge)
    --base OLD      The folder the badge was last updated from; see "Base" below
    --to DIR        Where `backup` saves files (default: backups/<date-time>)
    --dry-run       Show what would happen; change nothing
    --yes           Don't ask; use the safe choice for every ASK
    --no-backup     Don't back up automatically before `update` or `restore`

Needs Python 3.8+ and mpremote (`pipx install mpremote` or `pip install mpremote`).

Base: to tell "a file you edited" from "an old version of a system file", the
tool needs the folder the badge was last updated from. `update` and `restore`
remember it in a small file on the badge (.badgetool.json). A badge straight
from the factory doesn't have that file yet, so for your first update, pass
the folder it came with: --base path/to/old/badge
"""
import argparse
import datetime
import difflib
import fnmatch
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

# ── Actions ───────────────────────────────────────────────────────────────
OVERWRITE = "overwrite"  # copy FOLDER's version onto the badge
KEEP = "keep"            # leave the badge's file alone
DELETE = "delete"        # remove the file from the badge
SAVE = "save"            # (backup) copy the badge's file to your laptop
SKIP = "skip"            # (backup) don't
ASK = "ask"              # show the file and ask what to do

# ── Policy: edit this table to change what each command does ──────────────
# Each row is a way a file on the badge can compare to FOLDER (and to BASE,
# the folder the badge was last updated from). Each column is a command.
# Allowed: backup → SAVE, SKIP, ASK; update/restore → OVERWRITE, KEEP, DELETE, ASK.
#
#                    backup  update     restore
POLICY = {
    "unchanged":    (SKIP,   KEEP,      KEEP),       # same as FOLDER
    "missing":      (SKIP,   OVERWRITE, OVERWRITE),  # in FOLDER, not on the badge
    "outdated":     (SKIP,   OVERWRITE, OVERWRITE),  # system file you never touched; FOLDER has a newer one
    "retired":      (SKIP,   DELETE,    DELETE),     # system file you never touched; FOLDER dropped it
    "yours-new":    (SAVE,   KEEP,      DELETE),     # only on the badge: a file you added
    "yours-edited": (SAVE,   KEEP,      OVERWRITE),  # you changed it; FOLDER didn't
    "conflict":     (SAVE,   ASK,       OVERWRITE),  # you changed it, and so did FOLDER
    "different":    (SAVE,   ASK,       OVERWRITE),  # differs from FOLDER; no BASE to say who changed it
    "state":        (SAVE,   KEEP,      KEEP),       # in a STATE_DIRS folder: data the badge made itself
}
COMMANDS = ("backup", "update", "restore")

# What ASK turns into with --yes.
SAFE_CHOICE = {"backup": SAVE, "update": KEEP, "restore": KEEP}

# Folders the badge writes to on its own (keys, saved settings). Files here
# are "state" unless they match FOLDER exactly.
STATE_DIRS = ["data/"]

# Never compared or copied, on either side. Matched against each part of a path.
IGNORE = ["__pycache__", "*.pyc", ".DS_Store", "Thumbs.db", ".git", ".badgetool.json"]

MANIFEST = ".badgetool.json"

DESCRIBE = {
    "unchanged": "same as the folder",
    "missing": "in the folder, not on the badge",
    "outdated": "the folder has a newer version; you never changed it",
    "retired": "the folder dropped it; you never changed it",
    "yours-new": "only on the badge (you added it)",
    "yours-edited": "you changed it; the folder didn't",
    "conflict": "you changed it, and so did the folder",
    "different": "differs from the folder (no base to say who changed it)",
    "state": "data the badge saved itself",
}


def check_policy():
    allowed = {"backup": {SAVE, SKIP, ASK}, "update": {OVERWRITE, KEEP, DELETE, ASK},
               "restore": {OVERWRITE, KEEP, DELETE, ASK}}
    for situation, actions in POLICY.items():
        if len(actions) != len(COMMANDS):
            sys.exit(f"POLICY[{situation!r}] needs {len(COMMANDS)} actions")
        for cmd, action in zip(COMMANDS, actions):
            if action not in allowed[cmd]:
                sys.exit(f"POLICY[{situation!r}]: {action!r} isn't allowed for {cmd}")
    if set(POLICY) != set(DESCRIBE):
        sys.exit(f"POLICY must have exactly these rows: {', '.join(DESCRIBE)}")


def action_for(cmd, situation):
    return POLICY[situation][COMMANDS.index(cmd)]


# ── Comparing ─────────────────────────────────────────────────────────────
def ignored(path):
    return any(fnmatch.fnmatch(part, pat) for part in PurePosixPath(path).parts for pat in IGNORE)


def is_state(path):
    return any(path.startswith(d) for d in STATE_DIRS)


def hash_folder(folder):
    files = {}
    for p in sorted(Path(folder).rglob("*")):
        rel = p.relative_to(folder).as_posix()
        if p.is_file() and not ignored(rel):
            files[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return files


def classify(path, badge, folder, base):
    """How the badge's copy of `path` compares to FOLDER and BASE (None = no base known)."""
    b, f = badge.get(path), folder.get(path)
    if b is None:
        return "missing"
    if b == f:
        return "unchanged"
    if is_state(path):
        return "state"
    o = base.get(path) if base is not None else None
    if f is None:  # only on the badge
        if o is None:
            return "yours-new"
        return "retired" if b == o else "conflict"
    if base is None:
        return "different"
    if o is None:  # FOLDER added it, and so did you
        return "conflict"
    if b == o:
        return "outdated"
    if f == o:
        return "yours-edited"
    return "conflict"


def compare(badge, folder, base):
    return {p: classify(p, badge, folder, base) for p in sorted(set(badge) | set(folder))}


# ── Talking to the badge (through mpremote) ───────────────────────────────
LIST_SCRIPT = r"""
import os, hashlib, binascii
def walk(d):
    for e in os.ilistdir(d):
        p = d + e[0]
        if e[1] == 0x4000:
            walk(p + "/")
        else:
            h = hashlib.sha256()
            with open(p, "rb") as f:
                while True:
                    b = f.read(1024)
                    if not b:
                        break
                    h.update(b)
            print("@@F\t" + p + "\t" + binascii.hexlify(h.digest()).decode())
walk("/")
try:
    with open("/%s") as f:
        print("@@M\t" + f.read().replace("\n", " "))
except OSError:
    pass
""" % MANIFEST


class Badge:
    def __init__(self, port=None):
        if shutil.which("mpremote"):
            self.cmd = ["mpremote"]
        else:
            try:
                import mpremote  # noqa: F401
                self.cmd = [sys.executable, "-m", "mpremote"]
            except ImportError:
                sys.exit("Can't find mpremote. Install it with: pipx install mpremote")
        if port:
            self.cmd += ["connect", port]

    def _run(self, args):
        r = subprocess.run(self.cmd + args, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"mpremote failed:\n{r.stdout}{r.stderr}")
        return r.stdout

    def _chain(self, commands, chunk=40):
        """Run many mpremote commands, a few dozen per connection."""
        for i in range(0, len(commands), chunk):
            args = []
            for c in commands[i:i + chunk]:
                args += (["+"] if args else []) + c
            self._run(args)

    def _exec(self, code):
        self._run(["exec", code])

    def list(self):
        """Return ({path: sha256}, manifest or None)."""
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(LIST_SCRIPT)
        try:
            out = self._run(["run", f.name])
        finally:
            Path(f.name).unlink()
        files, manifest = {}, None
        for line in out.splitlines():
            parts = line.rstrip("\r").split("\t")
            if parts[0] == "@@F" and len(parts) == 3:
                path = parts[1].lstrip("/")
                if not ignored(path):
                    files[path] = parts[2]
            elif parts[0] == "@@M":
                try:
                    manifest = json.loads(parts[1])
                except ValueError:
                    print(f"warning: ignoring a damaged {MANIFEST} on the badge")
        return files, manifest

    def fetch(self, paths, dest):
        for p in paths:
            (Path(dest) / p).parent.mkdir(parents=True, exist_ok=True)
        self._chain([["fs", "cp", ":/" + p, str(Path(dest) / p)] for p in paths])

    def push(self, pairs):
        """pairs: [(local file, badge path)]"""
        dirs = sorted({str(d) for _, p in pairs for d in PurePosixPath("/" + p).parents if str(d) != "/"},
                      key=lambda d: d.count("/"))
        if dirs:
            self._exec("import os\nfor d in %r:\n try: os.mkdir(d)\n except OSError: pass" % dirs)
        self._chain([["fs", "cp", str(local), ":/" + p] for local, p in pairs])

    def delete(self, paths):
        """Remove files, then any folders they leave empty."""
        dirs = sorted({str(d) for p in paths for d in PurePosixPath("/" + p).parents if str(d) != "/"},
                      key=lambda d: -d.count("/"))
        self._exec("import os\nfor p in %r:\n os.remove(p)\nfor d in %r:\n try: os.rmdir(d)\n except OSError: pass"
                   % (["/" + p for p in paths], dirs))

    def write_manifest(self, folder, hashes):
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp) / MANIFEST
            local.write_text(json.dumps({"folder": str(Path(folder).resolve()), "files": hashes}))
            self.push([(local, MANIFEST)])

    def reset(self):
        self._run(["reset"])


# ── Showing differences ───────────────────────────────────────────────────
def show_diff(badge, folder, path):
    with tempfile.TemporaryDirectory() as tmp:
        ours = b""
        try:
            badge.fetch([path], tmp)
            ours = (Path(tmp) / path).read_bytes()
        except SystemExit:
            pass  # not on the badge
        theirs = (Path(folder) / path).read_bytes() if (Path(folder) / path).is_file() else b""
    if b"\0" in ours or b"\0" in theirs:
        print(f"  (binary file: badge {len(ours)} bytes, folder {len(theirs)} bytes)")
        return
    lines = difflib.unified_diff(
        theirs.decode(errors="replace").splitlines(), ours.decode(errors="replace").splitlines(),
        f"folder/{path}", f"badge/{path}", lineterm="")
    out = "\n".join(lines)
    print(out if out else "  (no differences)")


def ask(cmd, path, situation, badge, folder):
    if cmd == "backup":
        options = {"s": SAVE, "n": SKIP}
        prompt = "[s]ave to laptop, [n]o, [d]iff? "
    else:
        options = {"k": KEEP, "o": OVERWRITE, "r": DELETE}
        prompt = "[k]eep yours, [o]verwrite with the folder's, [r]emove from badge, [d]iff? "
    print(f"\n{path}: {DESCRIBE[situation]}")
    while True:
        a = input("  " + prompt).strip().lower()[:1]
        if a == "d":
            show_diff(badge, folder, path)
        elif a in options:
            return options[a]


# ── Commands ──────────────────────────────────────────────────────────────
def check_folder(folder):
    folder = Path(folder)
    if not folder.is_dir():
        sys.exit(f"{folder} isn't a folder")
    if not (folder / "main.py").exists():
        hint = [p.parent for p in folder.glob("*/main.py")]
        sys.exit(f"{folder} has no main.py, so it's probably not the badge's firmware folder."
                 + (f" Did you mean {hint[0]}?" if hint else ""))


def load(badge, args):
    print("Reading the badge…")
    on_badge, manifest = badge.list()
    folder = hash_folder(args.folder)
    if args.base:
        check_folder(args.base)
        base = hash_folder(args.base)
    elif manifest:
        base = manifest.get("files", {})
    else:
        base = None
    return on_badge, folder, base


def plan(cmd, situations, badge, args):
    chosen = {}
    for path, s in situations.items():
        a = action_for(cmd, s)
        if a == ASK:
            a = SAFE_CHOICE[cmd] if (args.yes or args.dry_run) else ask(cmd, path, s, badge, args.folder)
        chosen[path] = a
    return chosen


def summarize(chosen, situations, skip=(KEEP, SKIP)):
    todo = {p: a for p, a in chosen.items() if a not in skip}
    for p, a in todo.items():
        print(f"  {a:9} {p}  ({DESCRIBE[situations[p]]})")
    return todo


def confirm(args, question):
    if args.dry_run:
        print("Dry run: nothing changed.")
        return False
    if args.yes:
        return True
    return input(f"{question} [y/N] ").strip().lower().startswith("y")


def cmd_diff(badge, args):
    if args.file:
        show_diff(badge, args.folder, args.file.lstrip("/"))
        return
    on_badge, folder, base = load(badge, args)
    situations = compare(on_badge, folder, base)
    if base is None:
        print("(No base known, so files that differ show as 'different'. See --base.)")
    same = sum(1 for s in situations.values() if s == "unchanged")
    print(f"{same} files match the folder.")
    print(f"\n  {'backup':8} {'update':9} {'restore':9} file")
    for p, s in situations.items():
        if s != "unchanged":
            b, u, r = POLICY[s]
            print(f"  {b:8} {u:9} {r:9} {p}  ({DESCRIBE[s]})")


def do_backup(badge, args, on_badge, folder, base, dest):
    situations = {p: s for p, s in compare(on_badge, folder, base).items() if p in on_badge}
    chosen = plan("backup", situations, badge, args)
    todo = [p for p, a in chosen.items() if a == SAVE]
    if not todo:
        print("Nothing to back up: every file on the badge matches the folder.")
        return
    print(f"Backing up {len(todo)} files to {dest}:")
    for p in todo:
        print(f"  {p}  ({DESCRIBE[situations[p]]})")
    if args.dry_run:
        print("Dry run: nothing copied.")
        return
    badge.fetch(todo, dest)
    print(f"Done. Your files are in {dest}")


def default_backup_dir(suffix=""):
    return Path("backups") / (datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S") + suffix)


def cmd_backup(badge, args):
    on_badge, folder, base = load(badge, args)
    do_backup(badge, args, on_badge, folder, base, Path(args.to) if args.to else default_backup_dir())


def cmd_install(badge, args):
    """update and restore: same steps, different column of POLICY."""
    cmd = args.command
    on_badge, folder, base = load(badge, args)
    if cmd == "update" and base is None:
        print("No base known: every file that differs from the folder will be asked about.\n"
              "Tip: pass --base with the folder your badge came with.")
    if not args.no_backup:
        do_backup(badge, args, on_badge, folder, base, default_backup_dir(f"_before-{cmd}"))
        print()
    situations = compare(on_badge, folder, base)
    chosen = plan(cmd, situations, badge, args)
    print(f"\n{cmd.capitalize()} plan:")
    for p, a in chosen.items():
        if a == KEEP and action_for(cmd, situations[p]) == ASK:
            print(f"  {'keep':9} {p}  ({DESCRIBE[situations[p]]}; keeping yours)")
    todo = summarize(chosen, situations)
    if not todo:
        print("  Nothing to do; the badge already matches.")
        if not args.dry_run:
            badge.write_manifest(args.folder, folder)
        return
    if not confirm(args, "Go ahead?"):
        return
    writes = [(Path(args.folder) / p, p) for p, a in todo.items() if a == OVERWRITE and p in folder]
    deletes = [p for p, a in todo.items() if a == DELETE and p in on_badge]
    if deletes:
        badge.delete(deletes)
    if writes:
        badge.push(writes)
    badge.write_manifest(args.folder, folder)
    print(f"Copied {len(writes)}, deleted {len(deletes)}. Restarting the badge…")
    badge.reset()


def main():
    check_policy()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["diff", "backup", "update", "restore"])
    ap.add_argument("folder", help="the official firmware folder (the one with main.py in it)")
    ap.add_argument("file", nargs="?", help="(diff only) show line-by-line changes to this one file")
    ap.add_argument("--port")
    ap.add_argument("--base")
    ap.add_argument("--to")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--no-backup", action="store_true")
    args = ap.parse_args()
    check_folder(args.folder)
    badge = Badge(args.port)
    {"diff": cmd_diff, "backup": cmd_backup, "update": cmd_install, "restore": cmd_install}[args.command](badge, args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nStopped.")
