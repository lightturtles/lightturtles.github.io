---
id: mount-and-run
title: Run code from your laptop without copying it (mpremote mount)
label: Mount and run
tier: stretch
difficulty: 7
group: editing
icon: link
needs: [name-badge]
time: 20 min
touches: [main.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Edit files on your laptop in any editor you like, and run them on the badge
without uploading anything.

## You need

- `mpremote` (see [[repl]]); close Thonny/ViperIDE so the port is free
- A **copy** of the official folder to play in (don't edit the original, see [[map-firmware]])

## Steps

1. Make your playground:

   ```bash
   cp -r {{ facts.firmware.folder }} playground
   ```

2. Mount it and start the badge's program *from the laptop's copy*:

   ```bash
   mpremote mount playground + exec "exec(open('main.py').read())"
   ```

   The badge starts up as usual (more slowly; see below). The shell shows its output.

   <!-- TODO(verify): on the real badge; main.py may need `import main; main.main()` instead -->

3. In your laptop editor, change the line from [[name-badge]] in
   `playground/{{ facts.name_badge.file }}`. Save.

4. Back in the `mpremote` window, press **Ctrl+]** to quit, then run the same command
   again (**↑**, **Enter**). The badge starts from the laptop's files again, and your
   change is there. No upload, no Thonny.

5. **Ctrl+]** to quit. The badge's own files were never touched. Press
   **{{ facts.power.reset_button }}** to prove it.

**✅ Done when** a change you saved on your laptop shows up on the badge without copying
any files.

## What just happened

`mpremote mount` makes your laptop's folder look like a folder on the badge, called
`/remote`, and changes into it. When Python opens or imports a file, the read travels
over USB to your laptop. Files in `/remote` come first, so your playground copy wins
over the badge's own files.

The catch is speed: every import crosses the cable, so startup is slow. And files the
badge *writes* with a relative path land in your playground, not on the badge.
Use mount while you're iterating, then upload when you're happy (see [[name-badge]]).

<!-- TODO(diagram): badge flash `/` and laptop folder mounted at `/remote`; import arrow checking /remote first -->

## Stuck?

| Symptom | Fix |
|---|---|
| `could not enter raw repl` | Press **Ctrl+C** in another terminal with `mpremote`, or close Thonny. |
| Badge starts with the *old* code | Did you save in your editor? Did you restart the `mpremote mount` command? (**Ctrl+D** restarts from the badge's *own* `main.py`.) |
| Very slow, or times out | Normal for big folders. Mount only the folder you're changing, e.g. `mpremote mount playground/apps`. |
| `OSError` writing a file | Writes to `/remote` go to your laptop. Check the folder isn't read-only. |

## Have fun!

Time the startup with and without mount. Which files take longest to load?
