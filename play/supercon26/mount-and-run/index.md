---
id: mount-and-run
title: Work from your laptop (git, mount, and copy)
label: Work from your laptop
topic: setup
workshop: false
needs: [backup]
time: 30 min
touches: [main.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Keep your code on your laptop, in git, edited in whatever editor you like,
and get it onto the badge in one command, or run it without copying at all.

## You need

- `mpremote` (see [[repl]]); close Thonny and ViperIDE so the port is free
- `git` on your laptop, and a [[backup]] of your badge

## Steps

1. **Make a project folder that matches the badge.** Clone the badge's repo, so the
   official files are already in it:

   ```bash
   git clone {{ facts.firmware.repo }} my-badge
   cd my-badge
   ```

   (No git? Unzip the official folder somewhere, then `git init` and commit it as-is.)

2. **Bring your work in.** Copy your files from your backup into the matching places
   under `{{ facts.firmware.folder }}/`, e.g. your app to
   `{{ facts.firmware.folder }}/{{ facts.firmware.user_app }}`. Then:

   ```bash
   git diff --stat             # exactly what you've changed from the official files
   git add -A
   git commit -m "My app, as it was on the badge"
   ```

3. **Edit on the laptop.** Open the folder in your editor (VS Code, vim, anything).
   Make a change to your app and save.

4. **Copy it over:** one file, then a soft reset to load it:

   ```bash
   mpremote cp {{ facts.firmware.folder }}/{{ facts.firmware.user_app }} :{{ facts.firmware.user_app }} + soft-reset + repl
   ```

   One line: copy, restart, and watch the output. **Ctrl+]** to leave. `mpremote cp`
   skips files that haven't changed, so it's quick.

5. **Or don't copy at all: mount.** Run the badge's program from the laptop's files:

   ```bash
   mpremote mount {{ facts.firmware.folder }} + exec "exec(open('main.py').read())"
   ```

   <!-- TODO(verify): on the real badge; main.py may need `import main; main.main()` instead -->

   The badge starts up (more slowly) using *your laptop's* copies of every file.
   Change something, **Ctrl+]**, run the same command again, and the change is there.
   The badge's own files were never touched: press **{{ facts.power.reset_button }}** to prove it.

6. **Run one script without copying it.** For a quick experiment that isn't part of the
   app, keep a scratch file on your laptop and run it on the badge as-is:

   ```bash
   mpremote run scratch.py
   ```

   The badge runs it and prints the output here; nothing is saved on the badge. It
   starts from a soft reset with nothing else running (see [[resets]]), so import what
   you need at the top.

   <!-- TODO(verify): whether mpremote run's soft reset skips main.py on this badge (it should: raw REPL) -->

7. **Commit when it works.** Small commits, each one working:

   ```bash
   git commit -am "Show temperature in big font"
   ```

**✅ Done when** your app lives in git on your laptop, and a change you saved there shows
up on the badge with one command.

## What just happened

**The laptop is now the source of truth,** and the badge is a copy. That flips the
risk around: a broken or wiped badge costs you nothing, and git remembers every
working version (`git log`, `git diff`, `git checkout`). Because the repo started as
the official files, `git diff` is always "what I changed," the same question
[[badge-diff]] answers by comparing hashes.

**Copy or mount?**

| | Copy (`mpremote cp`) | Mount (`mpremote mount`) |
|---|---|---|
| Badge's files | updated | untouched |
| Startup | normal speed | slow: every import crosses the USB cable |
| Works unplugged | yes | no |
| Good for | "this works; keep it" | trying many small changes quickly |

`mpremote run` is a third option for a single script: the file is sent over and run,
but never stored on the badge.

`mpremote mount` makes your laptop's folder appear on the badge as `/remote`, and
changes into it, so `import` finds your laptop's files first. Files the badge *writes*
with a relative path land on your laptop, too.

<!-- TODO(diagram): laptop repo (git) → cp → badge flash; and laptop folder mounted at /remote, import arrow checking /remote first -->

## Stuck?

| Symptom | Fix |
|---|---|
| `could not enter raw repl` | Something else has the port: close Thonny or ViperIDE. |
| Badge runs the *old* code | Did you save? Did the copy finish? After mount, **Ctrl+D** restarts from the badge's *own* files. |
| Mount is very slow or times out | Normal for many files. Mount only what you're changing, or copy instead. |
| `git diff` shows every line changed | Line endings. On Windows: `git config core.autocrlf input`, then re-copy. |

## Have fun!

- Make a script (or a `Makefile`) that copies only the files git says have changed.
- Push your repo to GitHub, and you've shared your app (see [[share-apps]]).
- Time startup with and without mount. Which files take longest to load?
