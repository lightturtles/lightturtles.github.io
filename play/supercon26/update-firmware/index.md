---
id: update-firmware
title: Update the badge's firmware without losing your files
label: Update the firmware
topic: setup
workshop: true
needs: [backup]
time: 20 min
touches:
  - lib/app_switcher.py#AppSwitcher.__init__   # new/removed apps show up in the menu without editing anything
  - lib/json_configs.py         # data/panel_config.json: never overwrite
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Install the newest badge firmware and keep everything you've made.

## You need

- Your badge, connected (see [[repl]])
- A fresh [[backup]]
- Your clone of the badge's repo from [[map-firmware]] (or, without `git`, the old ZIP
  folder plus a freshly downloaded one, unzipped somewhere else)

## Steps

1. **Find what changed.** In your clone, note which version you have, get the new one,
   and ask `git` what changed in `{{ facts.firmware.folder }}/`:

   ```bash
   git rev-parse --short HEAD          # the version you have now; write it down (say, abc1234)
   git pull
   git diff --stat abc1234 HEAD -- {{ facts.firmware.folder }}
   ```

   Each line is a file that was added, changed or removed. `git diff abc1234 HEAD -- <file>`
   shows exactly what changed in one of them.

   Downloaded ZIPs instead? Compare the two folders: `diff -rq old/{{ facts.firmware.folder }} new/{{ facts.firmware.folder }}`
   (on Windows, try [WinMerge](https://winmerge.org)).

2. **Sort each changed file** into one of these:

   | The update… | And you… | Do this |
   |---|---|---|
   | added a file | (couldn't have touched it) | Upload it |
   | changed a file | never edited it | Upload it (overwrite) |
   | changed a file | edited it too (e.g. {{ facts.name_badge.file }}) | **Conflict:** your choice, see below |
   | removed a file | never edited it | Delete it from the badge |
   | didn't touch a file | edited it | Leave it alone |

   Your own apps aren't in the folder, so the update never touches them. In
   `{{ facts.firmware.state_dir }}/`, *do* upload new pictures or a new `schedule.csv` if
   the update has them, but never upload over `panel_config.json`. You don't need to touch
   `user_apps.py` or `app_list` at all; the badge rewrites them when it starts.

3. **Copy the files.** In Thonny's top pane, browse into the new folder. For each file to
   upload, make sure the bottom pane is in the matching folder on the badge, then
   right-click → **Upload to …**.

4. **Conflicts.** Take the new version, then redo your change on top of it. That's
   easy for a one-line change, which is one reason to keep your changes small.

5. Press **{{ facts.power.reset_button }}** and check that the badge starts and your
   apps are still there. If the update added or removed an app, the menu has already
   caught up: the badge rebuilds it from `apps/` every time it starts.

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

[badgetool.py](../badgetool.py) does all of step 2 for you (see [[backup]] for setup).
It needs the old folder as well as the new one. With a clone, `git worktree` makes
you a copy of the old version next to it:

```bash
git worktree add ../badge-old abc1234      # the version you wrote down in step 1
python badgetool.py update {{ facts.firmware.folder }} --base ../badge-old/{{ facts.firmware.folder }} --dry-run
python badgetool.py update {{ facts.firmware.folder }} --base ../badge-old/{{ facts.firmware.folder }}
```

It backs up your files first, shows the plan, and asks about each conflict (press **d**
to see the differences). Afterwards, it leaves a small `.badgetool.json` on the badge
that remembers which folder you installed, so next time you can leave out `--base`.

**Careful with the repo's own script.** `python scripts/update.py push` (in the repo's
`firmware/` folder) doesn't update, it *replaces*. It makes the badge match the folder:
it deletes your apps, overwrites files you edited, and resets your start-up counter.
That's [[start-fresh]], not an update.

Don't like what it does? Its `POLICY` table near the top lists every kind of file
and what `backup`, `update`, and `restore` do with each. Change `ASK` to `KEEP` or
`OVERWRITE` (or anything else) and run it again.

## Have fun!

Run `python badgetool.py diff new/{{ facts.firmware.folder }}` before and after. Predict
what the second one will say first.
