---
id: resets
title: "Resets and start-up: soft, hard, power cycle, and a REPL with nothing running"
label: Resets and start-up
topic: advanced
workshop: false
needs: [first-app]
time: 25 min
touches: [boot.py, main.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Do all three kinds of reset and find out what each one does (and doesn't)
wipe. Then learn what runs at start-up, and how to get a `>>>` with none of the badge's
program running: the starting point for testing your app by hand.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- Your app from [[first-app]]

## Steps

1. Press **Ctrl+C**, then leave a marker in memory and on an LED (the LED lines are
   explained in [[one-led]]):

   ```python
   from machine import Pin
   import neopixel
   np = neopixel.NeoPixel(Pin({{ facts.leds.pin }}), {{ facts.leds.count }})
   x = 42
   np[0] = (0, 32, 0)
   np.write()
   ```

2. **Soft reset.** Press **Ctrl+C**, then **Ctrl+D** at an empty `>>>`.
   (Or run `machine.soft_reset()`.) This is the "leave the REPL" you've been using
   since [[repl]].
   - The badge's program restarts. Press **Ctrl+C** to get back to `>>>`.
   - Type `x`. Is it still there?
   - Is the LED still lit?

3. **Hard reset.** Press the **{{ facts.power.reset_button }}** button
   (or run `import machine; machine.reset()`).
   - Your editor will lose the connection for a moment. Reconnect if it doesn't
     do so on its own.
   - Then check:

     ```python
     import machine
     machine.reset_cause() == machine.HARD_RESET
     ```

4. **Power cycle.** Unplug USB *and* {{ facts.power.power_off }}. Wait five
   seconds, then power it back up and reconnect.
   - Is the LED lit now? Is the e-ink screen still showing an image?
   - Check `machine.reset_cause() == machine.PWRON_RESET`.

5. **Which one picks up your edit?** Change one of your app's messages and save, but
   don't reset. The old message still prints. Now try each kind of reset in turn,
   changing the message between them.

6. **What runs at start-up?** Every kind of reset ends the same way: MicroPython runs
   `boot.py`, then `main.py`. Look at both:

   ```python
   print(open("boot.py").read())
   ```

   `boot.py` is usually short: low-level set-up that has to happen first. `main.py` is
   the badge's whole program (see [[firmware-diagram]]). It never finishes, which is why
   you only reach `>>>` by pressing **Ctrl+C**.

   <!-- TODO(verify): what this year's boot.py does (empty? USB, filesystem, pins?) -->

7. **A REPL with nothing running.** Sometimes you want the badge set up by `boot.py`
   but *not* running `main.py`: no menu, no apps, no tasks, just you. At `>>>`:
   1. Press **Ctrl+A**. The prompt changes to `raw REPL; CTRL-B to exit` and a bare `>`.
   2. Press **Ctrl+D**. The badge soft-resets, but in this mode it runs `boot.py` and
      **skips `main.py`**.
   3. Press **Ctrl+B** to get the normal `>>>` back.

   Now look around:

   ```python
   dir()
   import sys; sorted(sys.modules)
   ```

   Compare with what you saw in [[explore-badge]]. Almost nothing is loaded: no
   `badge_obj`, no apps. Is the LED from step 1 still lit?

8. **Get the badge back.** Press **Ctrl+D** at the normal `>>>`. That soft reset runs
   `main.py` as usual.

9. Fill in the table below as you go.

**✅ Done when** you can say, for each kind of reset, whether it clears your
variables, the LEDs, and the screen, and you've reached a `>>>` with `main.py` not
running.

## What just happened

| | Soft reset | Hard reset | Power cycle |
|---|---|---|---|
| How | **Ctrl+D**, `machine.soft_reset()` | **{{ facts.power.reset_button }}** button, `machine.reset()` | Remove all power |
| Python variables | Gone | Gone | Gone |
| Chip hardware (pins, timers) | **Mostly left as-is** | Reset | Reset |
| USB connection | Stays | Drops and comes back | Drops |
| LEDs | Stay lit | Stay lit (they have power) | Off |
| E-ink image | Stays | Stays | Stays (it needs no power) |
| Files on the badge | Kept | Kept | Kept |
| Picks up your saved edit | Yes | Yes | Yes |
| Runs `boot.py` | Yes | Yes | Yes |
| Runs `main.py` | Yes, unless you're in the raw REPL | Yes | Yes |

A **soft reset** only restarts the Python interpreter. It's quick, but anything the
old program set up in hardware may still be running. A **hard reset** restarts the
whole chip as if it had just powered on, but anything with its own power (like the
LED chips) keeps its last state. Only a **power cycle** truly starts from zero.

All three pick up your edit, because each one starts Python over, and `main.py`
imports every app again from the files. Saving alone doesn't: the old version stays
loaded in RAM until something restarts Python. Soft reset is the quickest, so it's the
one you'll use most. When something acts strangely, work up the list: soft, then hard,
then power cycle.

**Start-up** is two files, in order. `boot.py` gets the badge ready; `main.py` runs the
badge. The **raw REPL** (Ctrl+A) is the mode tools like `mpremote` and Thonny use to
send code to the badge. A soft reset there leaves out `main.py` on purpose, so the
tool gets a quiet badge to work with. You can borrow it to get a **blank REPL**: a
badge that's set up but running nothing. That's where [[drive-app]] starts. You make
your app yourself and decide exactly what runs, and when.

<!-- TODO(diagram): three nested boxes: Python interpreter ⊂ chip ⊂ whole board, labeled with the reset that clears each -->
<!-- TODO(diagram): reset → boot.py → main.py (loops forever; Ctrl+C → >>>), with a raw-REPL branch: reset → boot.py → > (Ctrl+B → >>>) -->

## Stuck?

| Symptom | Fix |
|---|---|
| Ctrl+D does nothing | It only works at an empty `>>>`. Press **Ctrl+C** first. |
| Port gone after a hard reset | Normal; the chip's USB restarts. Reconnect (Thonny: **Stop/Restart**). |
| Badge keeps running after unplugging | It's on battery. Use the power switch too. |
| `reset_cause()` says something unexpected | Note it. A soft reset doesn't change it; it reports the last *hard* reset. |
| The menu came back after Ctrl+A, Ctrl+D | You pressed Ctrl+B first, or Thonny reset the badge for you. Try from `mpremote` (below). |
| Nothing echoes after Ctrl+A | That's the raw REPL: it doesn't echo. Press **Ctrl+B**. |

<!-- TODO(verify): Thonny's Stop/Restart and the raw REPL; it may run main.py anyway -->

## Prefer the command line?

```bash
mpremote soft-reset              # soft reset (mpremote does it in the raw REPL: main.py doesn't run)
mpremote soft-reset + repl       # ...and then a blank >>>
mpremote reset                   # hard reset
```

<!-- TODO(verify): that `mpremote soft-reset + repl` leaves main.py not running on this badge -->

## Have fun!

- Which reset makes the badge show its boot screen fastest? Time it.
- At a blank REPL, import `main` yourself (`import main`). What happens? How do you get
  `>>>` back?
