---
id: map-firmware
title: Find the badge's files (what's there, and which ones are yours)
label: Find the files
topic: setup
workshop: true
needs: [repl]
time: 20 min
touches:
  - main.py                     # what "the file that starts everything" imports
  - lib/app_switcher.py#AppSwitcher.__init__   # finds apps/*.py; writes data/user_apps.py and data/app_list
  - lib/json_configs.py         # data/panel_config.json (the start-up counter)
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Know what every top-level file and folder on the badge is for, and which ones
are meant for *you* to change.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- The official firmware folder on your laptop (step 1)

## Steps

1. **Get the official files.** Clone the badge's repo somewhere you'll find again:

   ```bash
   git clone {{ facts.firmware.repo }}
   ```

   Expect updates during the conference. With a clone, getting them is one command
   (`git pull`, see [[update-firmware]]).

   No `git`? Go to <{{ facts.firmware.repo }}>, click **Code → Download ZIP**, and unzip
   it. You'll have to download a fresh ZIP for every update.

   Inside is a folder called `{{ facts.firmware.folder }}/`. It holds *exactly* the files
   that belong on the badge. From here on, "**the folder**" means that folder.

2. **Show both side by side.** In Thonny, open **View → Files**. The top pane is your
   laptop: browse to `{{ facts.firmware.folder }}/`. The bottom pane is the badge
   (**MicroPython device**).

   <!-- TODO(screenshot): Thonny Files view, laptop folder on top, badge below, same names highlighted -->

   The badge should look nearly the same as `{{ facts.firmware.folder }}/`. That's not
   a coincidence: whoever built the badge
   copied that folder onto it.

3. **Do the same from the REPL:**

   ```python
   import os
   os.listdir('/')
   os.listdir('/apps')
   os.listdir('/lib')
   os.listdir('/data')
   ```

4. **Fill in this table** for each top-level item. Guess from the names, then open a file
   or two to check.

   | Item | What it's for | Should you edit it? |
   |---|---|---|
   | `boot.py` | | |
   | `main.py` | | |
   | `apps/` | | |
   | `{{ facts.firmware.lib_dir }}/` | | |
   | `{{ facts.firmware.state_dir }}/` | | |

5. **Spot the differences.** Is anything on the badge that *isn't* in the folder, or
   different from it? Look in `{{ facts.firmware.state_dir }}/`. Most of it (pictures, the
   schedule) came in the folder, but the badge also writes a few files there itself:

   | File | What the badge keeps in it |
   |---|---|
   | `panel_config.json` | How many times it has started up (see [[use-badge]]) |
   | `user_apps.py` | The list of apps it found in `apps/`, rewritten at every start-up |
   | `app_list` | The apps' names, in menu order (a small database, not text) |

   Open `panel_config.json`. How many times has your badge started?

**✅ Done when** you can point to: the file that starts everything, where the apps live
(and where *your* apps will go), the firmware's own building blocks, and the files the
badge writes itself.

## What just happened

The files on your badge come in three kinds:

| Kind | Examples | Where else it exists |
|---|---|---|
| **System files** | `boot.py`, `main.py`, `{{ facts.firmware.lib_dir }}/`, the apps that came in `apps/`, the pictures and schedule in `{{ facts.firmware.state_dir }}/` | In the folder. Mess one up and you can always get it back. |
| **Your files** | New apps you put in `apps/`, anything else you add | Thonny and ViperIDE can edit files right on the badge. Anything you write that way is **only on your badge** until you back it up. (Write on your laptop and copy it over, and your laptop has a copy too. See [[mount-and-run]].) |
| **Badge data** | `{{ facts.firmware.state_dir }}/panel_config.json`, `user_apps.py`, `app_list` | Only on your badge. The badge wrote them. |

The apps are plain Python files, and the badge finds them on its own: at every start-up
it lists `apps/`, loads each file it finds, and builds the menu from them. That's why
there's no list of apps to edit anywhere.

Everything in the rest of this round ([[backup]], [[update-firmware]], [[start-fresh]])
is just "compare the badge to the folder, then copy one way or the other." Which way
depends on which kind of file it is.

<!-- TODO(diagram): block diagram: boot.py → main.py → app switcher (menu) → apps/*.py (your apps highlighted); lib/ (buttons, LEDs, e-ink, SAO) underneath; data/ off to the side, with the three badge-written files marked -->

## Stuck?

| Symptom | Fix |
|---|---|
| The bottom pane is missing | **View → Files**. Then click **Stop** so Thonny can talk to the badge. |
| The bottom pane is empty or says "busy" | The badge's program is running. Click **Stop**, or press **Ctrl+C** in the shell. |
| Can't find `{{ facts.firmware.folder }}/` in the ZIP | It's one level down, inside `{{ facts.firmware.zip_folder }}/`. |
| The badge has lots of files the folder doesn't | Its firmware may be a different release. Ask a helper, or see [[update-firmware]]. |
{% if facts.firmware.usb_drive %}| Want to drag files instead? | The badge also shows up as a USB drive on your laptop. |
{% else %}| Why doesn't the badge show up as a USB drive? | MicroPython on this chip doesn't do that. Thonny, ViperIDE and `mpremote` move files over the serial connection instead. |
{% endif %}

## Prefer the command line?

```bash
mpremote fs tree      # everything on the badge
mpremote fs cat :main.py
mpremote fs cat :data/panel_config.json
```

## Have fun!

- Open `main.py` and skim it. What does it import? Find the line that counts start-ups,
  and the one that checks for 42. Then follow it properly in [[firmware-diagram]].
- Put a copy of `apps/template.py` in `apps/` under a new name, press **Ctrl+D**, and
  open `data/user_apps.py` again. What changed? (Then delete your copy.)
- Which file is the biggest? `mpremote fs tree -h`
