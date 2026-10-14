---
id: resets
title: Soft reset vs. hard reset vs. power cycle
label: Three kinds of reset
topic: modify-app
workshop: false
needs: [name-badge]
time: 15 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Do all three kinds of reset and find out what each one does (and doesn't) wipe.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- A file you've edited and saved, from [[name-badge]]

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
   (Or run `machine.soft_reset()`.)
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

5. **Which one picks up your edit?** Change your line from [[name-badge]] again and save,
   but don't reset. Open **{{ facts.name_badge.app }}**: still the old version. Now try each
   kind of reset in turn, changing the line between them.

6. Fill in the table below as you go.

**✅ Done when** you can say, for each kind of reset, whether it clears your
variables, the LEDs, and the screen, and whether it picks up your edit.

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

A **soft reset** only restarts the Python interpreter. It's quick, but anything the
old program set up in hardware may still be running. A **hard reset** restarts the
whole chip as if it had just powered on, but anything with its own power (like the
LED chips) keeps its last state. Only a **power cycle** truly starts from zero.

All three pick up your edit, because each one starts Python over, and `main.py`
imports every app again from the files. Saving alone doesn't: the old version stays
loaded in RAM until something restarts Python. Soft reset is the quickest, so it's the
one you'll use most.

When something acts strangely, work up the list: soft, then hard, then power cycle.

<!-- TODO(diagram): three nested boxes: Python interpreter ⊂ chip ⊂ whole board, labeled with the reset that clears each -->

## Stuck?

| Symptom | Fix |
|---|---|
| Ctrl+D does nothing | It only works at an empty `>>>`. Press **Ctrl+C** first. |
| Port gone after a hard reset | Normal; the chip's USB restarts. Reconnect (Thonny: **Stop/Restart**). |
| Badge keeps running after unplugging | It's on battery. Use the power switch too. |
| `reset_cause()` says something unexpected | Note it. A soft reset doesn't change it; it reports the last *hard* reset. |

## Prefer the command line?

```bash
mpremote soft-reset
mpremote reset        # hard reset
```

## Have fun!

Which reset makes the badge show its boot screen fastest? Time it.
