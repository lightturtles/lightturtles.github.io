---
id: break-and-restore
title: Break a file on purpose; read the traceback; restore the file
label: Read a traceback
topic: crashes
workshop: false
needs: [name-badge, explore-badge]
time: 25 min
touches:
  - main.py                     # the try/except around its imports: prints the error, then re-raises
  - lib/app_switcher.py#AppSwitcher.__init__   # imports every app via data/user_apps.py; catches errors while building each app
  - apps/base_app.py#BaseApp.arun   # catches errors in run(): "<name> hit an exception"
  - apps/nametag.py
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Read an error message well enough to find the exact line that caused it, tell
the two kinds of crash apart, then put the file back the way it was.

## You need

- The file you edited in [[name-badge]], open in Thonny from the badge
- The official folder on your laptop (see [[map-firmware]])

## Steps

1. **Break it so it can't load.** In `{{ facts.name_badge.file }}`, find a line ending in
   `:` (like `def run(self):` or `if self.launched:`) and delete the colon. Note the line
   number (bottom of Thonny's window). Save, then press **Ctrl+D** in the shell.

2. **Read the traceback.** The badge stops, and the shell prints something like this
   (twice: once from `main.py`, once from MicroPython):

   ```
   Traceback (most recent call last):
     File "main.py", line 8, in <module>
     File "lib/app_switcher.py", line 115, in <module>
     File "lib/app_switcher.py", line 41, in __init__
     File "data/user_apps.py", line 1, in <module>
     File "apps/nametag.py", line 28
   SyntaxError: invalid syntax
   ```

   <!-- TODO(verify): the exact traceback from a real badge -->

   Read it **from the bottom up**:
   - **Last line:** *what* went wrong (`SyntaxError`).
   - **The line above it:** *where*: the file and line number. Does it match the line you broke?
   - **Lines above that:** *how it got there*. `main.py` started the app switcher, which
     imported every app at once (through `data/user_apps.py`), and couldn't read yours.

   <!-- TODO(screenshot): real traceback from the badge, with the three parts labeled -->

3. **Look at what's left.** You're at `>>>` already, without pressing **Ctrl+C**:
   `main.py` crashed, so there was nothing left running. Try the buttons and the menu.
   Then look around, as in [[explore-badge]]:

   ```python
   dir()
   ```

   Almost nothing. Start-up failed at its first big import, so the menu, the button
   scanner and every app were never made. **One unreadable app file stops the whole
   badge**, not just that app.

4. **Break it so it loads, but fails later.** Put the colon back. Now misspell a name
   that only gets used when the app draws: change `plate.set_style_pad_all(8, 0)` to
   `plate.set_style_pad_al(8, 0)`. Save, **Ctrl+D**.

   The badge starts normally this time. Open **{{ facts.name_badge.app }}** from the menu.
   The LEDs turn cyan and stay that way, the screen doesn't change, and the shell says:

   ```
   Nametag hit an exception 'obj' object has no attribute 'set_style_pad_al'
   Traceback (most recent call last):
     File "apps/base_app.py", line 29, in arun
     File "apps/nametag.py", line 49, in run
   AttributeError: 'obj' object has no attribute 'set_style_pad_al'
   ```

   <!-- TODO(verify): the exact message from a real badge -->

   Same three parts, read bottom up. But now press a **Menu** button: the menu works,
   and so does every other app. Only the line that broke didn't run.

5. **Restore the file.** You could undo with **Ctrl+Z**, but practice the real way:
   1. Close the editor tab without saving.
   2. In the top (laptop) pane, browse to the official folder's
      `{{ facts.name_badge.file | split: "/" | pop | join: "/" }}/`.
   3. Make sure the bottom (badge) pane is showing the *same* folder on the badge.
   4. Right-click the file in the top pane → **Upload to …**. Say **yes** to overwrite.

6. **Ctrl+D**. The badge starts normally, and your changes from [[name-badge]] are
   gone. Redo them if you like.

**✅ Done when** you've found both broken lines from the traceback alone, can say which
crash stopped the whole badge and which one didn't, and your badge runs again.

## What just happened

There are two kinds of crash, and they look different:

| | Crash while loading | Crash while running |
|---|---|---|
| Example | `SyntaxError`: a missing `:` or `)`, bad indenting | `NameError`, `AttributeError`, `ZeroDivisionError` inside `run()` |
| When | at start-up, when the badge imports the file | later, when that line actually runs |
| The badge | stops: you land at `>>>` | keeps running |
| The shell says | `Traceback…` | `Nametag hit an exception …`, then `Traceback…` |

Python reads a whole file before running any of it. A **SyntaxError** means it couldn't
even read the file, so the import failed. The badge imports all its apps in one go, so
that one failure took the whole start-up down with it.

The misspelled name was valid Python, so the file imported fine. The **AttributeError**
only happened when that line *ran*. Every app's `run()` is called by `arun()` in
`apps/base_app.py`, which catches any error, prints it, and carries on. Handy: one buggy
app can't freeze your badge. Sneaky: the app just stops partway, so an error in a part
that runs over and over prints over and over, and one that runs once is easy to miss.
To look inside an app after one of those, see [[post-mortem]].

There's a third kind, in between: an error in an app's `__init__` (which runs at
start-up). The badge prints `Failed to load app module`, skips that app, and starts
without it on the menu.

You restored from the **folder**, not from your [[backup]]. Your backup only holds your
own files, and when you made it, this file still matched the folder. If you'd broken
one of *your* files (an app you added), you'd restore it from the backup the same way.

### Asking for help

When you're stuck, a helper, Discord or an AI can only help with what you give them.
Paste, as text (not a photo):

1. **The whole traceback**, from the first line to the last.
2. **The code around the line it names**, with line numbers if you can.
3. **What you changed** just before it broke ([[badge-diff]] tells you exactly).
4. **Which firmware** you're on: the output of `os.uname()`, and which version of the
   badge's repo you copied from.

Most problems get solved at step 1. Often by you, while you're copying it out.

<!-- TODO(diagram): traceback lines mapped to a call stack: main.py at the bottom, nametag.py on top, the error message as the top frame's label -->

## Stuck?

| Symptom | Fix |
|---|---|
| No traceback, just a blank screen | The error went to the shell; scroll up. Or press **Ctrl+C** then **Ctrl+D** to see it again. |
| Traceback points at a line you didn't touch | Look at the line *before* it. A missing `)` or `:` often gets blamed on the next line. |
| The same error prints again and again | It's in a part of `run()` that runs every time. Fix it, or open another app to make it stop. |
| "Upload to" isn't in the menu | You right-clicked in the bottom pane. Upload starts from the top (laptop) pane. |
| The badge vanishes from USB before you can do anything | See [[recover]]. |

## Prefer the command line?

```bash
mpremote cp {{ facts.firmware.folder }}/{{ facts.name_badge.file }} :{{ facts.name_badge.file }}
mpremote reset
```

Restoring one of your own files is the same, from your backup folder.
`python badgetool.py diff {{ facts.firmware.folder }} {{ facts.name_badge.file }}` shows exactly
what's different before you do (see [[badge-diff]]).

## Have fun!

- Make a list of every kind of error you can cause on purpose in one line:
  `ZeroDivisionError`, `IndexError`, `KeyError`, `TypeError`, `ImportError`…
  Which ones stop the badge from starting, and which only stop one app?
- Cause the third kind: put `1 / 0` in `NametagApp.__init__`. What's missing from the menu?
- Find the line in `apps/base_app.py` that prints `hit an exception`. What does it do next?
