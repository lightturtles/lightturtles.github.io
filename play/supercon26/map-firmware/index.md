---
id: map-firmware
title: Find the badge's files (what's there, and which ones are yours)
label: Find the files
topic: basics
workshop: true
needs: [repl]
time: 20 min
touches: []
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

1. **Get the official files.** Go to <{{ facts.firmware.repo }}>, click **Code → Download
   ZIP**, and unzip it somewhere you'll find again. Inside is a folder called
   `{{ facts.firmware.folder }}/`. It holds *exactly* the files that belong on the badge.
   From here on, "**the folder**" means that folder.

   <!-- TODO(verify): if there are releases, link the one that matches the badges as shipped -->

2. **Show both side by side.** In Thonny, open **View → Files**. The top pane is your
   laptop: browse to the folder. The bottom pane is the badge (**MicroPython device**).

   <!-- TODO(screenshot): Thonny Files view, laptop folder on top, badge below, same names highlighted -->

   They should look nearly the same. That's not a coincidence: whoever built the badge
   copied that folder onto it.

3. **Do the same from the REPL:**

   ```python
   import os
   os.listdir('/')
   os.listdir('/apps')
   ```

4. **Fill in this table** for each top-level item. Guess from the names, then open a file
   or two to check.

   | Item | What it's for | Should you edit it? |
   |---|---|---|
   | `boot.py` | | |
   | `main.py` | | |
   | `apps/` | | |
   | `hardware/` | | |
   | `ui/` | | |
   | `{{ facts.firmware.lib_dir }}/` | | |
   | `{{ facts.firmware.state_dir }}/` | | |

   <!-- TODO(verify): swap in this year's top-level names once the firmware is out -->

5. **Spot the differences.** Is anything on the badge that *isn't* in the folder?
   The `{{ facts.firmware.state_dir }}/` folder is the usual one: the badge writes there
   itself (saved settings, keys for messaging), so it's different on every badge.

**✅ Done when** you can point to: the file that starts everything, where the apps live,
the files meant for you to edit ({{ facts.firmware.user_apps }}), and the folder the badge
writes its own data to.

## What just happened

The files on your badge come in three kinds:

| Kind | Examples | Where else it exists |
|---|---|---|
| **System files** | `main.py`, `hardware/`, `ui/` | In the folder. Mess one up and you can always get it back. |
| **Your files** | {{ facts.firmware.user_apps }}, anything you add | **Only on your badge**, until you back it up. |
| **Badge data** | `{{ facts.firmware.state_dir }}/` | Only on your badge. The badge made it. |

Everything in the rest of this round ([[backup]], [[update-firmware]], [[start-fresh]])
is just "compare the badge to the folder, then copy one way or the other." Which way
depends on which kind of file it is.

<!-- TODO(diagram): block diagram: boot.py → main.py → menu → apps (user apps highlighted); hardware/ and ui/ underneath; data/ off to the side -->

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
```

## Have fun!

- Open `main.py` and skim it. What does it import? Then follow it properly in [[firmware-diagram]].
- Which file is the biggest? `mpremote fs tree -h`
