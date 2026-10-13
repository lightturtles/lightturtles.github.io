#!/usr/bin/env python3
"""
skilltree_layout.py — generate (or update) a hand-editable hex skill-tree
layout from the front matter of the skill pages, and render a preview.

Usage:
    python3 _scripts/skilltree_layout.py play/supercon26
    python3 _scripts/skilltree_layout.py play/supercon26 --preview tree.svg

The tree is a folder: TREE/index.md is the tree page and every TREE/<id>/index.md
is a skill (its id is the folder name). The layout lives in the tree page's
front matter, between the "Skill tree layout" and "end of layout" comment
lines; nothing else in the file is touched. If that block isn't there yet,
it's added at the end of the front matter.

If the block has no tiles, the whole layout is generated from scratch. If it
does, every tile stays where you put it: new skills are slotted in around
them, skills whose pages are gone are dropped (with a warning), and the block
is rewritten (comments inside it aren't kept). Delete the block to start over.

Front matter used: label (falls back to title), tier, difficulty, group, needs.

Layout rules: the start tile (no needs, lowest difficulty) sits alone in the
top row. Every other skill sits in a row below everything it needs. Skills
are placed core first, then developmental, then stretch, easiest first within
each tier; each one takes the free cell that best touches its prerequisites,
neighbors its group, and stays close to the start tile.

Layout block:
    palette:                   # tier -> color
      core: "#e4572e"
    grid: |                    # static, numbered slots; top row = start.
       1   2   3               # An INDENTED row is shifted right half a hex.
         4   5   6
    tiles:                     # slot number -> skill id. Change a number to
      2: repl                  # move a tile; swap two numbers to swap tiles.
"""
import argparse
import html
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

FRONT_MATTER = re.compile(r"---\s*\n(.*?)\n---\s*\n", re.S)
TIER_RANK = {"core": 0, "developmental": 1, "stretch": 2}
DEFAULT_PALETTE = {"core": "#e4572e", "developmental": "#f3a712", "stretch": "#7bb661"}

# placement weights (lower cost wins)
W_NEED = 6.0        # per prerequisite the cell does NOT touch
W_GROUP = 1.5       # bonus per neighbor in the same group
W_SIDE = 0.15       # per hex of sideways drift (keeps the tree symmetric)
W_ORDER = 50.0      # cell is not above a skill that needs this one (updates only)


def warn(msg):
    print(f"warning: {msg}", file=sys.stderr)


# ------------------------------------------------------------- hex geometry
# Cells are (row, x2): x2 is the column in half-hex units, so a hex's
# neighbors are (r, x2±2) and (r±1, x2±1). Rows grow downward.
def neighbors(c):
    r, x = c
    return [(r, x - 2), (r, x + 2), (r - 1, x - 1), (r - 1, x + 1), (r + 1, x - 1), (r + 1, x + 1)]


def dist(a, b):
    dr, dx = abs(a[0] - b[0]), abs(a[1] - b[1])
    return dr + max(0, (dx - dr) // 2)


# ------------------------------------------------------------------ skills
def load_skills(skills_dir):
    skills = {}
    for p in sorted(Path(skills_dir).glob("*/index.md")):
        m = FRONT_MATTER.match(p.read_text())
        if not m:
            warn(f"{p}: no front matter, skipped")
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        sid = p.parent.name
        if fm.get("id") and str(fm["id"]) != sid:
            warn(f"{p}: id {fm['id']!r} ignored; the site uses the folder name {sid!r}")
        tier = str(fm.get("tier") or "")
        if tier not in TIER_RANK:
            warn(f"{sid}: unknown tier {tier!r}")
        skills[sid] = {
            "label": str(fm.get("label") or fm.get("title") or sid),
            "tier": tier,
            "difficulty": float(fm.get("difficulty") or 0),
            "group": fm.get("group"),
            "needs": [str(n) for n in (fm.get("needs") or [])],
        }
    if not skills:
        sys.exit(f"error: no skill pages found in {skills_dir}/")
    for sid, s in skills.items():
        missing = [n for n in s["needs"] if n not in skills]
        if missing:
            warn(f"{sid} needs {', '.join(missing)}, which doesn't exist yet (ignored)")
        s["needs"] = [n for n in s["needs"] if n in skills]
    return skills


def find_start(skills):
    return min(skills, key=lambda k: (bool(skills[k]["needs"]), skills[k]["difficulty"],
                                      TIER_RANK.get(skills[k]["tier"], 9), k))


def depths(skills):
    memo, visiting = {}, set()

    def d(sid):
        if sid in memo:
            return memo[sid]
        if sid in visiting:          # cycle; reported during placement
            return 0
        visiting.add(sid)
        memo[sid] = 1 + max((d(n) for n in skills[sid]["needs"]), default=-1)
        visiting.discard(sid)
        return memo[sid]

    return {sid: d(sid) for sid in skills}


# --------------------------------------------------------------- placement
def place(skills, pos):
    """Add every skill missing from pos ({id: cell}) without moving the others."""
    start = find_start(skills)
    if not pos:
        pos[start] = (0, 0)
    origin = pos.get(start) or min(pos.values())
    parity = (origin[1] - origin[0]) % 2          # x2 ≡ row + parity on valid cells
    occupied = {c: sid for sid, c in pos.items()}
    dependents = defaultdict(list)
    for sid, s in skills.items():
        for n in s["needs"]:
            dependents[n].append(sid)
    depth = depths(skills)
    remaining = set(skills) - set(pos)

    def cost(sid, c):
        s = skills[sid]
        near = [occupied[n] for n in neighbors(c) if n in occupied]
        k = dist(c, origin) + W_SIDE * abs(c[1] - origin[1]) / 2
        k += W_NEED * sum(1 for n in s["needs"] if n not in near)
        if s["group"]:
            k -= W_GROUP * sum(1 for n in near if skills[n]["group"] == s["group"])
        below = [pos[d][0] for d in dependents[sid] if d in pos]
        if below and c[0] >= min(below):
            k += W_ORDER
        return k

    while remaining:
        ready = [s for s in remaining if all(n in pos for n in skills[s]["needs"])]
        if not ready:
            warn(f"dependency cycle among: {', '.join(sorted(remaining))}")
            ready = list(remaining)
        sid = min(ready, key=lambda k: (TIER_RANK.get(skills[k]["tier"], 9),
                                        skills[k]["difficulty"], depth[k], k))
        placed_needs = [pos[n][0] for n in skills[sid]["needs"] if n in pos]
        min_row = max(placed_needs, default=origin[0]) + 1
        cands = {n for c in occupied for n in neighbors(c)
                 if n not in occupied and n[0] >= min_row}
        if not cands:                              # shouldn't happen; scan a row
            r = min_row
            x = origin[1] + (r - origin[0]) % 2
            step = 0
            while (r, x + step) in occupied:
                step = -step if step > 0 else -step + 2
            cands = {(r, x + step)}
        cell = min(cands, key=lambda c: (cost(sid, c), c[0], abs(c[1] - origin[1]), c[1]))
        pos[sid] = cell
        occupied[cell] = sid
        remaining.discard(sid)
    return pos


def check_order(skills, pos):
    for sid, s in skills.items():
        for n in s["needs"]:
            if pos[n][0] >= pos[sid][0]:
                warn(f"{sid} is not below {n}, which it needs")


# -------------------------------------------------------------------- grid
def build_grid(cells):
    """Numbered slots covering cells, with a spare hex on each side and two rows below."""
    r0, r1 = min(c[0] for c in cells), max(c[0] for c in cells) + 2
    left, right = min(c[1] for c in cells) - 2, max(c[1] for c in cells) + 2
    parity = (cells[0][1] - cells[0][0]) % 2
    if (left - r0 - parity) % 2:                   # first row must be unindented
        left -= 1
    ncols = (right - left) // 2 + 1
    rows, n = [], 1
    for r in range(r0, r1 + 1):
        off = (left - r - parity) % 2
        rows.append((off, [(n + k, (r, left + off + 2 * k)) for k in range(ncols)]))
        n += ncols
    return rows


def grid_text(rows):
    w = max(len(str(num)) for _, row in rows for num, _ in row)
    sep = " " * (2 if w % 2 == 0 else 3)            # even pitch -> exact half-hex indent
    pitch = w + len(sep)
    return "\n".join((" " * (off * pitch // 2) + sep.join(str(num).ljust(w) for num, _ in row)).rstrip()
                     for off, row in rows)


def parse_grid(text):
    lines = [l for l in text.splitlines() if l.strip()]
    rows, seen = [], set()
    for r, line in enumerate(lines):
        off = 1 if line[:1].isspace() else 0
        if off != r % 2:
            sys.exit("error: grid rows must alternate unindented / indented, starting unindented")
        row = []
        for col, tok in enumerate(line.split()):
            if tok == ".":
                continue
            if not tok.isdigit():
                sys.exit(f"error: grid slot {tok!r} isn't a number")
            if int(tok) in seen:
                sys.exit(f"error: grid slot {tok} appears twice")
            seen.add(int(tok))
            row.append((int(tok), (r, 2 * col + off)))
        rows.append((off, row))
    return rows


# ------------------------------------------------------------- YAML in/out
class UniqueKeyLoader(yaml.BaseLoader):
    """BaseLoader (everything stays a string) that refuses duplicate keys."""
    def construct_mapping(self, node, deep=False):
        keys = [self.construct_object(k, deep) for k, _ in node.value]
        dupes = sorted({k for k in keys if keys.count(k) > 1})
        if dupes:
            sys.exit(f"error: line {node.start_mark.line + 1}: duplicate key(s) {', '.join(dupes)}")
        return super().construct_mapping(node, deep)


def split_front_matter(path):
    """(front matter text, rest of file) for the tree page."""
    text = Path(path).read_text()
    m = FRONT_MATTER.match(text)
    if not m:
        sys.exit(f"error: {path} has no front matter")
    return m.group(1), text[m.end():]


def load_layout(path, skills):
    """(data, rows, pos) from the tree page; rows is None when there are no tiles yet."""
    data = yaml.load(split_front_matter(path)[0], Loader=UniqueKeyLoader) or {}
    if not data.get("tiles"):
        return data, None, {}
    rows = parse_grid(data.get("grid") or "")
    slots = {num: cell for _, row in rows for num, cell in row}
    pos = {}
    for num, sid in (data.get("tiles") or {}).items():
        if not num.isdigit() or int(num) not in slots:
            sys.exit(f"error: tiles: {num} isn't a slot in the grid")
        if sid in pos:
            sys.exit(f"error: tiles: {sid} is placed twice")
        if sid not in skills:
            warn(f"{sid} has no skill page any more; removed from the layout")
            continue
        pos[sid] = slots[int(num)]
    return data, rows, pos


def q(s):
    return json.dumps(s, ensure_ascii=False)


BLOCK_START = "# ── Skill tree layout"
BLOCK_END = "# ── end of layout"
BLOCK = re.compile(r"^" + re.escape(BLOCK_START) + r".*?^" + re.escape(BLOCK_END) + r"[^\n]*\n?",
                   re.S | re.M)


def write_layout(path, data, rows, pos):
    num_of = {cell: num for _, row in rows for num, cell in row}
    out = [f"{BLOCK_START} (rewritten by _scripts/skilltree_layout.py) ─────────",
           "# Hand-edit freely: change a tile's number in `tiles:` to move it, or swap two",
           "# numbers to swap tiles. Re-running keeps your edits and only slots in new skills.",
           "palette:"]
    out += [f"  {k}: {q(v)}" for k, v in data["palette"].items()]
    out += ["", "# Slots, top row first. Indented rows sit half a hex to the right.", "grid: |"]
    out += ["  " + l for l in grid_text(rows).splitlines()]
    out += ["", "tiles:"]
    out += [f"  {num_of[c]}: {sid}" for sid, c in sorted(pos.items(), key=lambda kv: num_of[kv[1]])]
    out.append(BLOCK_END + " ─────────────────────────────────────────────────────────")
    block = "\n".join(out) + "\n"

    fm, rest = split_front_matter(path)
    fm += "\n"
    if BLOCK.search(fm):
        fm = BLOCK.sub(lambda _: block, fm, count=1)
    else:
        if re.search(r"^(palette|grid|tiles):", fm, re.M):
            sys.exit(f"error: {path} has palette/grid/tiles outside the layout block; "
                     "move them between the block's comment lines or delete them")
        fm = fm.rstrip("\n") + "\n\n" + block
    Path(path).write_text("---\n" + fm + "---\n" + rest)


# ----------------------------------------------------------------- preview
R = 70                          # hex circumradius (center to vertex), px
W = math.sqrt(3) * R            # pointy-top hex width
V = 1.5 * R                     # vertical distance between row centers
GAP = 4
MARGIN = 30
TITLE_H = 70
LEGEND_H = 40
FONT = "Helvetica, Arial, sans-serif"


def hex_points(cx, cy, r):
    pts = []
    for i in range(6):
        a = math.radians(60 * i - 90)
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


def wrap(text, max_chars):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(text, r):
    usable_w = math.sqrt(3) * r * 0.80
    usable_h = r * 1.25
    for size in (15, 14, 13, 12, 11, 10, 9, 8):
        char_w = size * 0.55
        lines = wrap(text, max(4, int(usable_w / char_w)))
        widest = max((len(l) for l in lines), default=0) * char_w
        if len(lines) * size * 1.15 <= usable_h and widest <= usable_w * 1.08:
            return size, lines
    return 8, wrap(text, int(usable_w / (8 * 0.55)))


def text_color(bg):
    bg = bg.strip()
    if bg.startswith("#") and len(bg) in (4, 7):
        h = bg[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        return "#111" if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.5 else "#fff"
    return "#111"


def render_svg(data, rows, pos, skills):
    palette = data["palette"]
    sid_at = {c: sid for sid, c in pos.items()}
    slots = [(num, cell) for _, row in rows for num, cell in row]
    r0 = min(c[0] for _, c in slots)
    x0 = min(c[1] for _, c in slots)
    grid_w = (max(c[1] for _, c in slots) - x0) * W / 2 + W
    grid_h = (max(c[0] for _, c in slots) - r0) * V + 2 * R
    used = [t for t in palette if any(s["tier"] == t for s in skills.values())]
    title, subtitle = data.get("title", ""), data.get("subtitle", "")
    top = MARGIN + (TITLE_H if title else 0)
    width = grid_w + 2 * MARGIN
    height = top + grid_h + (LEGEND_H if used else 0) + MARGIN

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
           f'width="{width:.0f}" height="{height:.0f}" font-family="{FONT}">',
           '<rect width="100%" height="100%" fill="#fff"/>']
    if title:
        out.append(f'<text x="{width / 2:.1f}" y="{MARGIN + 30}" text-anchor="middle" '
                   f'font-size="28" font-weight="bold" fill="#111">{html.escape(title)}</text>')
    if subtitle:
        out.append(f'<text x="{width / 2:.1f}" y="{MARGIN + 56}" text-anchor="middle" '
                   f'font-size="15" fill="#555">{html.escape(subtitle)}</text>')

    for num, cell in slots:
        cx = MARGIN + W / 2 + (cell[1] - x0) * W / 2
        cy = top + R + (cell[0] - r0) * V
        sid = sid_at.get(cell)
        if sid is None:
            out.append(f'<polygon points="{hex_points(cx, cy, R - GAP / 2)}" fill="none" '
                       f'stroke="#ccc" stroke-width="1.5" stroke-dasharray="6 5"/>')
            out.append(f'<text x="{cx:.1f}" y="{cy + 5:.1f}" text-anchor="middle" '
                       f'font-size="14" fill="#bbb">{num}</text>')
            continue
        s = skills[sid]
        fill = palette.get(s["tier"], "#ffffff")
        ink = text_color(fill)
        out.append(f'<polygon points="{hex_points(cx, cy, R - GAP / 2)}" fill="{html.escape(fill)}" '
                   f'stroke="#222" stroke-width="2"/>')
        size, lines = fit_text(s["label"], R - GAP / 2)
        lh = size * 1.15
        y = cy - (len(lines) - 1) * lh / 2 + size * 0.35
        for i, line in enumerate(lines):
            out.append(f'<text x="{cx:.1f}" y="{y + i * lh:.1f}" text-anchor="middle" '
                       f'font-size="{size}" fill="{ink}">{html.escape(line)}</text>')
        out.append(f'<text x="{cx:.1f}" y="{cy - R * 0.68:.1f}" text-anchor="middle" '
                   f'font-size="10" fill="{ink}" opacity="0.6">{num}</text>')

    if used:
        ly = top + grid_h + 26
        item_w = 140
        lx = width / 2 - item_w * len(used) / 2
        for i, name in enumerate(used):
            x = lx + i * item_w
            out.append(f'<polygon points="{hex_points(x + 10, ly - 5, 10)}" '
                       f'fill="{html.escape(palette[name])}" stroke="#222"/>')
            out.append(f'<text x="{x + 26}" y="{ly}" font-size="14" fill="#333">'
                       f'{html.escape(name)}</text>')
    out.append("</svg>")
    return "\n".join(out)


# -------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Generate or update a hex skill-tree layout YAML.")
    ap.add_argument("tree_dir", help="the tree's folder, e.g. play/supercon26")
    ap.add_argument("--preview", metavar="SVG", help="also write a preview SVG here")
    args = ap.parse_args()

    skills = load_skills(args.tree_dir)
    out = Path(args.tree_dir) / "index.md"
    if not out.exists():
        sys.exit(f"error: {out} doesn't exist; create the tree page first")
    data, rows, pos = load_layout(out, skills)
    before = set(pos)
    data["palette"] = data.get("palette") or dict(DEFAULT_PALETTE)
    for t in {s["tier"] for s in skills.values()} - set(data["palette"]):
        warn(f"palette has no color for tier {t!r}")

    place(skills, pos)
    check_order(skills, pos)
    slot_cells = {cell for _, row in rows or [] for _, cell in row}
    if rows is None or not set(pos.values()) <= slot_cells:
        if rows is not None:
            print("note: layout outgrew the grid; slots were renumbered", file=sys.stderr)
        rows = build_grid(list(pos.values()))

    write_layout(out, data, rows, pos)
    added = sorted(set(pos) - before)
    msg = f"updated the layout in {out}"
    if before:
        msg += f" (added: {', '.join(added) or 'nothing'})"
    if args.preview:
        Path(args.preview).write_text(render_svg(data, rows, pos, skills))
        msg += f", wrote {args.preview}"
    print(msg)


if __name__ == "__main__":
    main()
