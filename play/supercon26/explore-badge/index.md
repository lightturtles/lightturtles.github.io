---
id: explore-badge
title: Explore the badge object with dir(), help() and Tab
label: Explore the badge object
topic: setup
workshop: false
needs: [repl]
time: 15 min
touches: [hardware/badge.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): names below (badge_obj, its attributes) are from the 2025 firmware -->

**Goal:** Find out what this badge can do, using the firmware's own names, from the REPL.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])

## Steps

1. Press **Ctrl+C** to stop the badge's program. Everything it set up is still in
   memory, including one object that holds all the hardware. Grab it:

   ```python
   {{ facts.firmware.badge_import }}
   badge_obj
   ```

2. **What's inside?** `dir()` lists every name an object holds:

   ```python
   dir(badge_obj)
   ```

   Skip the ones that start with `_`. The rest are the pieces of hardware
   ({{ facts.badge.devices }}) and a few helpers.

3. **Tab instead of typing.** Type `badge_obj.` (with the dot) and press **Tab**. You get
   the same list. Type the first letter or two of a name and press **Tab** again to finish
   it. Do this from now on: it's faster than typing, and it can't misspell.

4. **One level down.** Pick a piece of hardware and look inside that:

   ```python
   badge_obj.{{ facts.sao.i2c_attr }}
   dir(badge_obj.{{ facts.sao.i2c_attr }})
   ```

   Its `repr` (what prints when you type its name) often says what it is and how it's
   set up: which pins, what speed.

5. **Ask for help.** `help()` on an object lists its contents along with their types:

   ```python
   help(badge_obj.{{ facts.sao.i2c_attr }})
   type(badge_obj.display)
   ```

6. **Where is it written?** Every class remembers the module it came from:

   ```python
   type(badge_obj).__module__     # the file that defines the Badge class
   ```

   Open that file (see [[map-firmware]]) and find `__init__`. Each `self.something = ...`
   line is one of the names you found in step 2.

7. **What's built in?** The firmware also has modules that aren't files:

   ```python
   help('modules')
   ```

   Spot a few you know (`time`, `machine`, `network`) and a few you don't.

8. **What did the badge leave behind?** `dir()` with nothing in the brackets lists the
   names at `>>>` itself:

   ```python
   dir()
   ```

   Besides `badge_obj` (which you imported), there are names you never made. They're
   `main.py`'s: `main.py` and the REPL share one set of global names, so anything it
   made at the top level of the file is still there after **Ctrl+C**. Things it made
   *inside a function* (like `async def main()`) are gone.

   <!-- TODO(verify): which useful objects this year's main.py leaves at the top level -->

9. **Every module that's loaded.** The rest of what the badge set up is inside modules:

   ```python
   import sys
   sorted(sys.modules)
   ```

   A module is only loaded once, so importing one again hands you the very same module,
   with everything the badge put in it. That's why step 1 worked.

10. **Paste a block.** Typing a `for` loop line by line works, but pasting one often
    gets its indentation mangled. Press **Ctrl+E** (paste mode), paste, then **Ctrl+D**:

    ```python
    for name in dir(badge_obj):
        if not name.startswith("_"):
            print(name, type(getattr(badge_obj, name)))
    ```

11. Press **Ctrl+D** at an empty `>>>` to get the badge back.

**✅ Done when** you can name the attribute for the display, the LEDs (if there is one)
and the SAO I2C bus, and say which file defines them.

## What just happened

The badge's firmware builds **one object for all the hardware** at startup and hands
it to every app. Apps write `self.badge.display`; at the REPL, the same object is
`badge_obj`. Using the firmware's objects, not your own, means your code and the
badge's agree on pins, speeds and settings.

`dir()` and `help()` work on *anything*: modules, classes, objects, even numbers. When
you meet something new on the badge, they're the first two things to type. Tab
completion is `dir()` at your fingertips.

`help('modules')` shows a different layer: the modules compiled into MicroPython
itself (written in C, like `machine`), plus any files on `sys.path`. Some names show
up there but not in `os.listdir('/')`. They're part of the **firmware image**, not the
filesystem.

**Ctrl+C** stops the badge's program but doesn't clean anything up: every object it
made stays in RAM until the next reset. That's what lets you look around now, and it's
what lets you look inside an app after it crashes (see [[post-mortem]]).

<!-- TODO(diagram): badge_obj in the middle, arrows to display / LEDs / I2C / buttons; "apps: self.badge" and "REPL: badge_obj" both pointing at it -->

## Stuck?

| Symptom | Fix |
|---|---|
| `ImportError` on the first line | The firmware keeps it somewhere else. Open `main.py` and search for `Badge(`. |
| `NameError: badge_obj` | You skipped the import. Every new `>>>` session needs it again after a reset. |
| Tab does nothing | Some terminals handle Tab differently. Try ViperIDE or `mpremote`. |
| Output scrolls off the top | Scroll up, or print one per line: `for n in dir(badge_obj): print(n)` |
| `dir()` shows almost nothing | `main.py` keeps everything inside functions. Use `sys.modules` (step 9) instead. |
| Paste mode shows `===` lines | That's paste mode. Finish with **Ctrl+D**, or **Ctrl+C** to cancel. |

## Have fun!

- Find something in `dir(badge_obj)` you can't explain. Read its code to find out.
- `import machine; dir(machine)`, then `machine.freq()` (CPU speed) and
  `import gc; gc.mem_free()` (free RAM).
- `import this`, and see if anyone left an easter egg.
