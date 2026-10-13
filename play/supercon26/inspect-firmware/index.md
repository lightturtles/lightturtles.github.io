---
id: inspect-firmware
title: Inspect the MicroPython firmware from the REPL
label: Inspect the firmware
tier: developmental
difficulty: 1
group: poking-around
icon: magnifier
needs: [repl]
time: 15 min
touches: []
verified_against: null
video: null
---

**Goal:** Find out what's built into your badge's MicroPython, using only the REPL.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])

## Steps

1. List every module you can `import`:

   ```python
   help('modules')
   ```

   Spot a few you recognize (`time`, `os`, `machine`) and a few you don't.

2. Compare that to the **files** on the badge:

   ```python
   import os
   os.listdir('/')
   ```

   Some modules show up in step 1 but not here. They're baked into the firmware
   itself, not stored as files.

3. Look inside a module. `dir()` lists everything it contains:

   ```python
   import machine
   dir(machine)
   ```

4. Ask for help on one thing you found:

   ```python
   help(machine.Pin)
   ```

5. See which pins have names on this board:

   ```python
   from machine import Pin
   help(Pin.board)
   ```

   If you get `AttributeError`, this firmware doesn't name its pins; that's normal on
   many ESP32 builds.

6. A few quick facts about the chip:

   ```python
   machine.freq()            # CPU speed, in Hz
   import gc; gc.mem_free()  # free RAM for Python, in bytes
   import esp; esp.flash_size()
   ```

7. Try **Tab completion**: type `machine.` (with the dot) and press **Tab**.

<!-- TODO(screenshot): help('modules') output with a couple of badge-specific modules circled -->

**✅ Done when** you can name one module that's built into the firmware but isn't a file,
and one thing inside `machine` you hadn't heard of.

## What just happened

The **firmware** is everything flashed onto the chip: the MicroPython interpreter,
its built-in modules (written in C, like `machine`), and sometimes **frozen** Python
modules compiled right into it. The **filesystem** is a separate area of flash where
your `.py` files live. `import` looks in both.

`dir(x)` and `help(x)` work on *anything* (modules, classes, objects you made), so
whenever you meet something new on the badge, these are the first two things to type.

<!-- TODO(diagram): flash split into "firmware (interpreter + built-in + frozen modules)" and "filesystem (your files)", both feeding `import` -->

## Stuck?

| Symptom | Fix |
|---|---|
| Output scrolls off the top | Scroll up in the shell pane, or make it taller. |
| `NameError` on `machine` | Run `import machine` first. |
| `ImportError: no module named 'esp'` | Skip it; that line is ESP32-only. |
| Tab does nothing | Some terminals (and Thonny) handle Tab differently. Try `mpremote` or ViperIDE. |

## Have fun!

- Run `dir()` with nothing in the brackets. That's everything *you've* defined this session.
- Find the badge's own modules in `help('modules')` and `dir()` them. What can you guess
  about how the firmware is built?
- `import this`, and see if anyone left an easter egg.
