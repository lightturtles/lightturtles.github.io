---
id: explore-badge
title: Explore the badge with dir(), help() and Tab
label: Explore the badge
topic: setup
workshop: false
needs: [repl]
time: 15 min
touches:
  - main.py                 # its top-level imports are what dir() shows after Ctrl+C
  - lib/epd.py#display
  - lib/led_bar.py#leds
  - lib/button.py           # UserA, UserB, MenuPlus, MenuMinus, Boot
  - lib/app_switcher.py#switcher
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Find out what this badge can do, using the firmware's own names, from the REPL.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])

## Steps

1. **What did the badge leave behind?** Press **Ctrl+C** to stop the badge's program.
   Everything it set up is still in memory. `dir()` with nothing in the brackets lists
   the names at `>>>`:

   ```python
   dir()
   ```

   You never made any of these. They're `main.py`'s: `main.py` and the REPL share one
   set of global names, so everything it imported at the top of the file is still
   there after **Ctrl+C**: `display`, `leds`, `UserA`, `UserB`, `switcher`, and a few
   more. Things it made *inside a function* (like `async def main()`) are gone.

2. **What's inside?** `dir()` on an object lists every name it holds. Try the LEDs:

   ```python
   leds
   dir(leds)
   ```

   Skip the ones that start with `_`. The rest are what you can do with it: `fill`,
   `write`, `clear`, `set_sequence`...

3. **Tab instead of typing.** Type `display.` (with the dot) and press **Tab**. You get
   the same kind of list. Type the first letter or two of a name and press **Tab** again
   to finish it. Do this from now on: it's faster than typing, and it can't misspell.

4. **One level down.** Some of those names are values, and some are objects of their own:

   ```python
   display.width, display.height
   display.black
   dir(display.black)
   ```

   `display.black` is a MicroPython `FrameBuffer`: the black half of the picture on the
   screen (see [[draw-pixels]]).

5. **Ask for help.** `help()` on an object lists its methods, and its `repr` (what prints
   when you type its name) sometimes says what state it's in:

   ```python
   UserA
   help(UserA)
   ```

   Hold **User A** down and type `UserA` again.

6. **Where is it written?** Every class remembers the module it came from:

   ```python
   type(display).__module__
   ```

   `'lib.epd'`: the file `lib/epd.py`. Open it (see [[map-firmware]]) and find `class
   EPaperDisplay`. Each `self.something = ...` in `__init__`, and each `def`, is one of
   the names you found in step 3.

7. **The apps, too.** The menu is an object, and so is every app in it:

   ```python
   switcher.apps
   [a.name for a in switcher.apps]
   ```

8. **What's built in?** The firmware also has modules that aren't files:

   ```python
   help('modules')
   ```

   Spot a few you know (`time`, `machine`, `network`) and a few you don't.

9. **Every module that's loaded.** The rest of what the badge set up is inside modules:

   ```python
   import sys
   sorted(sys.modules)
   ```

   A module is only loaded once, so importing one again hands you the very same module,
   with everything the badge put in it. `from lib.epd import display` gives you the
   same `display` you've been using: that's how apps get at the hardware.

10. **Paste a block.** Typing a `for` loop line by line works, but pasting one often
    gets its indentation mangled. Press **Ctrl+E** (paste mode), paste, then **Ctrl+D**:

    ```python
    for name in dir(display):
        if not name.startswith("_"):
            print(name, type(getattr(display, name)))
    ```

11. Press **Ctrl+D** at an empty `>>>` to get the badge back.

**✅ Done when** you can name the objects for the display, the LEDs and a button, and
say which file defines each one.

## What just happened

The badge's firmware has **one module per piece of hardware** in `lib/`, and each
module makes its object the moment it's imported: `display` in `lib/epd.py`, `leds` in
`lib/led_bar.py`, the buttons in `lib/button.py`. Apps import the same objects
(`from lib.led_bar import leds`), so at the REPL you're holding exactly what the apps
use. Using the firmware's objects, not your own, means your code and the badge's agree
on pins, speeds and settings.

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

<!-- TODO(diagram): main.py's names (display, leds, UserA…, switcher) pointing into lib/epd.py, lib/led_bar.py, lib/button.py, lib/app_switcher.py; "apps: from lib.x import y" pointing at the same objects -->

## Stuck?

| Symptom | Fix |
|---|---|
| `NameError: name 'display' isn't defined` | `main.py` didn't run (a blank REPL, see [[resets]]), or it stopped before its imports. `from lib.epd import display`. |
| Tab does nothing | Some terminals handle Tab differently. Try ViperIDE or `mpremote`. |
| Output scrolls off the top | Scroll up, or print one per line: `for n in dir(display): print(n)` |
| Paste mode shows `===` lines | That's paste mode. Finish with **Ctrl+D**, or **Ctrl+C** to cancel. |

## Have fun!

- Find something in `dir(leds)` you can't explain (`menu_display`? `set_sequence`?). Read its code to find out.
- `import machine; dir(machine)`, then `machine.freq()` (CPU speed) and
  `import gc; gc.mem_free()` (free RAM).
- `import this`, and see if anyone left an easter egg.
