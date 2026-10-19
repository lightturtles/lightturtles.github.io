---
id: break-and-restore
title: Break a file on purpose; read the traceback; restore the file
label: Read a traceback
topic: crashes
workshop: false
needs: [name-badge, explore-badge]
time: 25 min
touches: [apps/nametag.py]     # TODO: facts.name_badge.file
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
   `:` (like a `def` or `if`) and delete the colon. Note the line number (bottom of
   Thonny's window). Save, then press **Ctrl+D** in the shell.

2. **Read the traceback.** The badge stops and the shell prints something like:

   ```
   Traceback (most recent call last):
     File "main.py", line 10, in <module>
     File "apps/nametag.py", line 42
   SyntaxError: invalid syntax
   ```

   Read it **from the bottom up**:
   - **Last line:** *what* went wrong (`SyntaxError`).
   - **The line above it:** *where*: the file and line number. Does it match the line you broke?
   - **Lines above that:** *how it got there*. `main.py` imported your file and couldn't.

   <!-- TODO(screenshot): real traceback from the badge, with the three parts labeled -->

3. **Look at what's left.** You're at `>>>` already, without pressing **Ctrl+C**:
   `main.py` crashed, so there was nothing left running. Try the buttons and the menu.
   Then look around, as in [[explore-badge]]:

   ```python
   dir()
   ```

   Anything `main.py` made *before* the failed import is still there. Anything after it
   never happened. You can tell how far start-up got.

4. **Break it so it loads, but fails later.** Put the colon back. Now change a variable's
   name on a line *inside* a method, e.g. `self.font` → `self.fnt`. Save, **Ctrl+D**.
   Does the badge start this time? Open **{{ facts.name_badge.app }}**. *Now* what happens?
   This time the shell says:

   ```
   Task exception wasn't retrieved
   future: <Task> coro= <generator object 'run' at ...>
   Traceback (most recent call last):
     File "apps/base_app.py", line 45, in run
     File "apps/nametag.py", line 57, in switch_to_foreground
   AttributeError: 'App' object has no attribute 'fnt'
   ```

   <!-- TODO(verify): the exact message and line numbers from this year's firmware -->

   Same three parts, read bottom up. But the badge is still running: the heartbeat
   still prints, other apps still work. Only this app is gone.

5. **Restore the file.** You could undo with **Ctrl+Z**, but practice the real way:
   1. Close the editor tab without saving.
   2. In the top (laptop) pane, browse to the official folder's
      `{{ facts.name_badge.file | split: "/" | pop | join: "/" }}/`.
   3. Make sure the bottom (badge) pane is showing the *same* folder on the badge.
   4. Right-click the file in the top pane → **Upload to …**. Say **yes** to overwrite.

6. **Ctrl+D**. The badge starts normally, and your one-line change from [[name-badge]] is
   gone. Redo it if you like.

**✅ Done when** you've found both broken lines from the traceback alone, can say which
crash stopped the whole badge and which one didn't, and your badge runs again.

## What just happened

There are two kinds of crash, and they look different:

| | Crash while loading | Crash while running |
|---|---|---|
| Example | `SyntaxError`, a typo in an `import` or at the top of a file | `NameError`, `AttributeError`, `ZeroDivisionError` inside a method |
| When | at start-up, when `main.py` imports the file | later, when that line actually runs |
| The badge | stops: you land at `>>>` | keeps running; only the app's task dies |
| The shell says | `Traceback…` | `Task exception wasn't retrieved`, then `Traceback…` |

Python reads a whole file before running any of it. A **SyntaxError** means it couldn't
even read the file, so `import` failed and took `main.py` down with it.

The misspelled name was valid Python, so the file imported fine. The **AttributeError**
only happened when that line *ran*, inside the app's task. asyncio printed it and
carried on with every other task. Errors that only show up at runtime are the ones that
hide until a demo. To look inside an app after one of those, see [[post-mortem]].

You restored from the **folder**, not from your [[backup]]. Your backup only holds your
own files, and when you made it, this file still matched the folder. If you'd broken
one of *your* files ({{ facts.firmware.user_apps }}), you'd restore it from the backup
the same way.

### Asking for help

When you're stuck, a helper, Discord or an AI can only help with what you give them.
Paste, as text (not a photo):

1. **The whole traceback**, from `Traceback` to the last line.
2. **The code around the line it names**, with line numbers if you can.
3. **What you changed** just before it broke ([[badge-diff]] tells you exactly).
4. **Which firmware** you're on: `{{ facts.firmware.version_check }}`.

Most problems get solved at step 1. Often by you, while you're copying it out.

<!-- TODO(diagram): traceback lines mapped to a call stack: main.py at the bottom, nametag.py on top, the error message as the top frame's label -->

## Stuck?

| Symptom | Fix |
|---|---|
| No traceback, just a blank screen | The error went to the shell; scroll up. Or press **Ctrl+C** then **Ctrl+D** to see it again. |
| Traceback points at a line you didn't touch | Look at the line *before* it. A missing `)` or `:` often gets blamed on the next line. |
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

Make a list of every kind of error you can cause on purpose in one line:
`ZeroDivisionError`, `IndexError`, `KeyError`, `TypeError`, `ImportError`…
Which ones stop the badge from booting, and which only kill one app?
