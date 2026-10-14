---
id: one-led
title: Light one LED from the REPL
label: Light one LED
topic: gpio
workshop: true
needs: [repl]
time: 10 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Turn on one of the badge's LEDs by typing three lines of Python.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])

## Steps

1. Click in the shell pane and press **Ctrl+C** so the badge's own program stops
   writing to the LEDs.

2. Tell MicroPython where the LEDs are:

   ```python
   from machine import Pin
   import neopixel
   np = neopixel.NeoPixel(Pin({{ facts.leds.pin }}), {{ facts.leds.count }})
   ```

3. Set the first LED to red, then send it:

   ```python
   np[0] = (32, 0, 0)
   np.write()
   ```

4. Try another LED and another color. The numbers are **(red, green, blue)**, each 0–255.

   ```python
   np[3] = (0, 0, 32)
   np.write()
   ```

5. Turn them all off:

   ```python
   np.fill((0, 0, 0))
   np.write()
   ```

<!-- TODO(photo): badge with LED 0 lit red -->

**✅ Done when** an LED you picked lights up in the color you picked.

## What just happened

The LEDs are **{{ facts.leds.type }}s**: each one has a tiny chip inside that listens
on a single data wire. They're chained, so the badge's GPIO {{ facts.leds.pin }}
talks to LED 0, LED 0 passes the rest of the message to LED 1, and so on.

`np[0] = ...` only changes a list in the badge's memory. Nothing lights until
`np.write()` sends the whole list down the wire. That's why you can set many LEDs
and have them all change at once.

LEDs are numbered from **0**, so the last one is `np[{{ facts.leds.count }} - 1]`.

<!-- TODO(diagram): GPIO pin → LED 0 → LED 1 → … with the color list in RAM above, and np.write() as the arrow that sends it -->

## Stuck?

| Symptom | Fix |
|---|---|
| `ImportError: no module named 'neopixel'` | Run `help('modules')` and look for it; tell a helper your firmware version. |
| `IndexError` | You asked for an LED that doesn't exist. Use `0` to `{{ facts.leds.count }} - 1`. |
| Nothing lights | Did you call `np.write()`? |
| The LED lights, then changes on its own | The badge's program is still running. Press **Ctrl+C** and try again. |
| Wrong color (e.g. green instead of red) | Tell a helper: the LED's color order may differ from the default. |

## Have fun!

Make LED 0 your favorite color. Find the dimmest value you can still see. Is
`(1, 0, 0)` visible in a dark room?

Keep the numbers small. `(255, 255, 255)` on every LED draws a lot of current
and is uncomfortably bright.
