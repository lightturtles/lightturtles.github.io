---
id: update-firmware
title: Update the badge's firmware without losing your files
label: Update the firmware
topic: setup
workshop: true
needs: [backup]
time: 20 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Install the newest badge firmware and keep everything you've made.

## You need

- Your badge, connected (see [[repl]])
- A fresh [[backup]]
- The **old** official folder (the one from [[map-firmware]]) and the **new** one.
  Download the new one the same way, and unzip it somewhere else so you don't mix them up.

## Steps

1. **Find what changed.** Check the release notes, or the list of changed files on
   GitHub, for which files are new, changed, or removed.

   <!-- TODO(verify): link to release notes / the compare page once there's an update -->

2. **Sort each changed file** into one of these:

   | The update… | And you… | Do this |
   |---|---|---|
   | added a file | (couldn't have touched it) | Upload it |
   | changed a file | never edited it | Upload it (overwrite) |
   | changed a file | edited it too (e.g. {{ facts.name_badge.file }}) | **Conflict:** your choice, see below |
   | removed a file | never edited it | Delete it from the badge |
   | didn't touch a file | edited it | Leave it alone |

   Never upload over {{ facts.firmware.user_apps }} or `{{ facts.firmware.state_dir }}/`,
   unless the release notes tell you to.

3. **Copy the files.** In Thonny's top pane, browse into the new folder. For each file to
   upload, make sure the bottom pane is in the matching folder on the badge, then
   right-click → **Upload to …**.

4. **Conflicts.** Take the new version, then redo your change on top of it. That's
   easy for a one-line change, which is one reason to keep your changes small.

5. Press **{{ facts.power.reset_button }}** and check that the badge starts and your
   apps are still there.

**✅ Done when** the badge runs the new firmware and your own files are untouched.

## What just happened

Updating is just copying, but *selective* copying. The new folder is the right version of
every system file. It's the wrong version of your files, because it doesn't know they
exist.

The tricky part is telling "a system file I never touched" from "a file I edited."
Both look like "different from the new folder." To tell them apart you compare against
the **old** folder: if the badge's copy matches the old one, you never touched it.

Updating MicroPython itself (the interpreter underneath all these files) is a different,
rarer job. You won't need it at Supercon.

<!-- TODO(diagram): three columns (old folder / badge / new folder) with arrows for each row of the table in step 2 -->

## Stuck?

| Symptom | Fix |
|---|---|
| Badge won't start after the update | Read the traceback (see [[break-and-restore]]). A missed file is the usual cause. If you're lost, [[start-fresh]]. |
| `ImportError` for a module you've never heard of | The update added a file you didn't copy. |
| Your app broke | The update may have changed something your app uses. Read the release notes, then fix your app. |
| Too many files to do by hand | Use the script below. |

## Prefer the command line?

[badgetool.py](../badgetool.py) does all of step 2 for you (see [[backup]] for setup):

```bash
python badgetool.py update new/{{ facts.firmware.folder }} --base old/{{ facts.firmware.folder }} --dry-run
python badgetool.py update new/{{ facts.firmware.folder }} --base old/{{ facts.firmware.folder }}
```

It backs up your files first, shows the plan, and asks about each conflict (press **d**
to see the differences). Afterwards, it leaves a small `.badgetool.json` on the badge
that remembers which folder you installed, so next time you can leave out `--base`.

Don't like what it does? Its `POLICY` table near the top lists every kind of file
and what `backup`, `update`, and `restore` do with each. Change `ASK` to `KEEP` or
`OVERWRITE` (or anything else) and run it again.

## Have fun!

Run `python badgetool.py diff new/{{ facts.firmware.folder }}` before and after. Predict
what the second one will say first.
