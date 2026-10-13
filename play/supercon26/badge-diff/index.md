---
id: badge-diff
title: Find exactly what you changed (diff the badge against the folder)
label: What did I change?
tier: stretch
difficulty: 6
group: files
icon: code-compare
needs: [backup]
time: 15 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** List every file on the badge that's different from the official folder, and see
the changed lines in one of them.

## You need

- [badgetool.py](../badgetool.py) and `mpremote`, set up as in [[backup]]
- A badge with at least one edited file (e.g. from [[name-badge]])

## Steps

1. **Which files?**

   ```bash
   python badgetool.py diff {{ facts.firmware.folder }}
   ```

   Every file that's different gets a line. The columns say what `backup`, `update`, and
   `restore` would do with it; the note at the end says why.

2. **Which lines?** Pick a file from that list:

   ```bash
   python badgetool.py diff {{ facts.firmware.folder }} {{ facts.name_badge.file }}
   ```

3. **Read the output.** It's a *unified diff*, the same format Git and GitHub use:

   ```diff
   --- folder/{{ facts.name_badge.file }}
   +++ badge/{{ facts.name_badge.file }}
   @@ -40,7 +40,7 @@
            self.username = ...
   -        self.font = lvgl.{{ facts.name_badge.find }}
   +        self.font = lvgl.{{ facts.name_badge.replace }}
            self.all_fonts = {
   ```

   - `-` lines are the folder's version, `+` lines are the badge's.
   - `@@ -40,7 +40,7 @@` means "starting at line 40, 7 lines shown" on each side.
   - Unmarked lines are context, so you can find the spot.

**✅ Done when** you can point to the exact line you changed, without opening the file.

## What just happened

`badgetool.py` asks the badge for a **SHA-256 hash** of every file: a 64-character
fingerprint that changes completely if even one byte of the file changes. It compares those
with the folder's hashes, so only the fingerprints cross the USB cable, not whole files.
Only for a line-by-line diff does it copy the one file over.

This is also how it decides what's "yours" and what's a system file. The same idea is
built into Git, backup tools, and `mpremote cp` itself (which skips unchanged files).

## Stuck?

| Symptom | Fix |
|---|---|
| Every file is "different" | The folder is a different release from what's on the badge. |
| "has no main.py" | Point it at the folder that *contains* `main.py`, not the one above it. |
| `mpremote failed` | Close Thonny or ViperIDE (only one program can use the port), then try again. |

## Have fun!

- Save the diff to a file (`> my-change.diff`) and share it. That's a *patch*: someone
  else can apply your change to their own copy with `patch -p1`.
- Diff two of your own backups to see what changed between them: `diff -ru backups/A backups/B`
