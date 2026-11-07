---
id: backup
title: Back up your files from the badge
label: Back up your badge
topic: setup
workshop: true
needs: [map-firmware]
time: 15 min
touches:
  - lib/json_configs.py         # data/panel_config.json: the one badge-written file worth keeping
  - lib/app_switcher.py#AppSwitcher.__init__   # rewrites data/user_apps.py and data/app_list every start-up
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Copy every file that exists *only* on your badge onto your laptop, so you
can't lose it.

## You need

- Your badge, connected (see [[repl]])
- The official folder on your laptop, and the map you made in [[map-firmware]]

## Steps

1. On your laptop, make a new folder next to the official one, e.g.
   `backups/2026-11-01/`. Put the date in the name; you'll make more of these.

2. In Thonny's **Files** view, browse the top (laptop) pane into that new folder.

3. In the bottom (badge) pane, select the files that are **yours**. Hold **Ctrl**
   (**Cmd** on a Mac) to pick several:
   - any app in `apps/` that isn't in the folder's `apps/`
   - any file you've edited (none yet, but after [[name-badge]], `{{ facts.name_badge.file }}`)
   - `{{ facts.firmware.state_dir }}/panel_config.json`
   - anything else you've added since you got the badge (e.g. a library in `{{ facts.firmware.lib_dir }}/`)

   You can skip the rest of `{{ facts.firmware.state_dir }}/`. The pictures and the
   schedule came in the folder, and the badge rewrites `user_apps.py` and `app_list`
   every time it starts.

4. Right-click → **Download to …**. The files appear in the top pane.

   <!-- TODO(screenshot): badge pane with user files selected, right-click menu open on "Download to" -->

5. Check it worked: double-click one of the downloaded files in the top pane and make
   sure it opens and has code in it.

**✅ Done when** your backup folder holds a copy of every file from step 3.

## What just happened

You didn't copy the system files, and you didn't need to: the official folder
already *is* their backup. A backup only has to hold what exists nowhere else.

That shortcut only works if you know which files are yours. Edit a system file (you
will, in [[name-badge]]) and it becomes yours too. Rule of thumb: **back up
before you change anything, and back up anything you changed.**

There's nothing secret on this year's badge, so your backup is safe to share. That
will change if you save a WiFi password in one of your apps.

<!-- TODO(diagram): badge files split into "same as the folder" (grey, skip), "rebuilt at start-up" (grey, skip) and "only here" (highlighted, arrow to laptop backup folder) -->

## Stuck?

| Symptom | Fix |
|---|---|
| No **Download** option | You right-clicked in the top pane. Right-click a file in the bottom (badge) pane. |
| "Device is busy" | Click **Stop** first. |
| Not sure which files you changed | Back up everything (see the command line below), or use `badgetool.py diff`. |
| Downloaded file is empty | Re-download it. If it's still empty, it's empty on the badge too. |

## Prefer the command line?

Easiest: copy **everything** on the badge. It's slower, but you can't miss a file.

```bash
mpremote cp -r : backups/2026-11-01/
```

Smarter: let a script compare the badge to the folder and copy only what's yours.
Download [badgetool.py](../badgetool.py) and put it next to the `{{ facts.firmware.folder }}/`
folder, then:

```bash
python badgetool.py diff   {{ facts.firmware.folder }}    # what's yours, and why
python badgetool.py backup {{ facts.firmware.folder }}    # copies it to backups/<date-time>/
```

It needs `mpremote` (see [[repl]]). `badgetool.py` sorts every file into one of a few
kinds ("yours-new", "yours-edited", "state", …). The table near the top of the script
decides what each command does with each kind. Read it; you can change it.

The badge's repo has a similar script, `{{ facts.firmware.update_script }}`. Its `pull`
copies *everything* into one `badge-backup/` folder (like the `mpremote` line above),
and `ls` lists which files differ, without saying whose they are.

## Have fun!

- Back up a friend's badge (with permission!) and compare: which files differ between two badges?
- Open `user_apps.py` from your backup. Delete it from the badge, press **Ctrl+D**, and look again. Is it back?
