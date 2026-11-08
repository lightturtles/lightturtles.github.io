---
id: start-fresh
title: Start fresh (make the badge match the official folder)
label: Start fresh
topic: setup
workshop: false
needs: [backup]
time: 15 min
touches:
  - lib/epd.py#EPaperDisplay.__init__   # reads /data/hwconf (made at the factory, not in the folder) to know which panel it drives
  - main.py#main                         # keeps load_counter in data/panel_config.json
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Put every system file back the way it came, so you're sure the badge works
again, and then bring back the things you made.

Use this when the badge is so broken you've lost track of what you changed.

## You need

- Your badge, connected and showing `>>>` (can't get there? See [[recover]] first)
- The official folder (see [[map-firmware]])
- A [[backup]], made *before* you start

## Steps

1. **Back up first.** Even a broken badge may hold work you want. Copy everything that
   isn't in the folder, or the whole badge (see [[backup]]).

2. **Delete everything except `{{ facts.firmware.state_dir }}/`.** In Thonny's bottom
   (badge) pane, select every top-level item **except** `{{ facts.firmware.state_dir }}/`,
   then right-click → **Delete**.

3. **Upload the folder.** In the top pane, go *inside* the official folder, select
   everything **except `{{ facts.firmware.state_dir }}/`**, and make sure the bottom pane is at the badge's top
   level (`/`). Right-click → **Upload to /**. (Uploading the folder's `{{ facts.firmware.state_dir }}/` would
   overwrite the badge's own settings in `{{ facts.config.file }}`.)

   <!-- TODO(verify): Thonny's multi-select upload of folders works on this badge; time it -->

4. Press **{{ facts.power.reset_button }}**. The badge should start just like it did out of
   the box, but with its settings still there (they live in `{{ facts.firmware.state_dir }}/`). Your name is
   gone from the name tag: it was in `{{ facts.name_badge.file }}`, which is a system file you
   changed. It's one of the things to bring back in step 5.

5. **Bring back your work**, one file at a time, from your backup. Restart after each one.
   If the badge breaks again, the last file you copied is the culprit.

**✅ Done when** the badge runs the stock firmware, and you've restored the files
you wanted back.

## What just happened

Every system file is now exactly what's in the folder, so if something's still wrong,
it's not those files. That's the real value of starting fresh: it shrinks the list of
suspects to "the files I put back," which you then test one at a time.

You kept `{{ facts.firmware.state_dir }}/` because the badge made much of it, not the folder. Deleting
it also deletes `{{ facts.firmware.state_dir }}/hwconf`, which was written at the factory and tells the
display driver which of two kinds of panel your badge has. Without it, the driver
guesses, and on some badges the picture comes out scrambled.

Starting fresh doesn't touch MicroPython itself. Flashing a whole new MicroPython is only
needed if `>>>` is gone for good, and that's a job for a helper at Supercon.

## Stuck?

| Symptom | Fix |
|---|---|
| Upload is very slow | It's only about 20 files outside `{{ facts.firmware.state_dir }}/`, but serial is slow; expect a minute or two. The command line is faster. |
| Badge still broken with *only* stock files | Ask a helper before deleting `{{ facts.firmware.state_dir }}/` too (back it up first, and keep `{{ facts.firmware.state_dir }}/hwconf`). Deleting just `{{ facts.config.file }}` is safe: the badge makes a new one. |
| You deleted `{{ facts.firmware.state_dir }}/` by accident | Copy it back from your backup. |

## Prefer the command line?

[badgetool.py](../badgetool.py) (see [[backup]] for setup) does steps 1–4:

```bash
python badgetool.py restore {{ facts.firmware.folder }} --dry-run   # see what it would do
python badgetool.py restore {{ facts.firmware.folder }}
```

It saves your files to `backups/<date-time>_before-restore/` first, only copies files
that are actually different, and leaves `{{ facts.firmware.state_dir }}/` alone. Want
it to keep your added files instead of deleting them? In its `POLICY` table, change the
`restore` column of the `yours-new` row from `DELETE` to `KEEP`.

## Have fun!

Start fresh, then use `python badgetool.py diff {{ facts.firmware.folder }}` to prove the
badge matches the folder.
