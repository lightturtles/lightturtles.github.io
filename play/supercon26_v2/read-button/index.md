---
id: read-button
title: Read a button from the REPL
label: Read a button
topic: gpio
workshop: true
needs: [repl]
time: 10 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Ask the badge whether a button is pressed right now, and watch the answer change.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])

## Steps

1. Press **Ctrl+C** in the shell pane so the badge's own program lets go of the buttons.

2. Set up button **{{ facts.buttons.example_label }}** as an input:

   ```python
   from machine import Pin
   btn = Pin({{ facts.buttons.example_pin }}, Pin.IN, Pin.PULL_UP)
   ```

3. Read it once without pressing, then again while you **hold the button down**:

   ```python
   btn.value()
   ```

   You should see `1` the first time and `0` the second.

4. Now watch it live. Paste this, press **Enter** until it runs, then press and
   release the button a few times:

   ```python
   import time
   while True:
       print(btn.value())
       time.sleep(0.1)
   ```

5. Press **Ctrl+C** to stop the loop.

<!-- TODO(screenshot): shell showing a column of 1s turning to 0s and back -->

**✅ Done when** the printed number changes when you press the button.

## What just happened

`Pin.IN` made the pin an input: the badge *listens* to it instead of driving it.

`Pin.PULL_UP` turned on a weak resistor inside the chip that pulls the pin up to
3.3 V, so it reads `1` when nothing is happening. Pressing the button connects
the pin to ground, which wins over the weak pull-up, so it reads `0`.
Pressed = 0 seems backwards at first, but it's very common.

Your loop checks the button ten times a second. That's called **polling**.
If you tap the button quickly, the loop might miss it. [[interrupts]] fixes that.

<!-- TODO(diagram): 3.3 V → pull-up resistor → pin → button → GND, with "not pressed: 1" and "pressed: 0" -->

## Stuck?

| Symptom | Fix |
|---|---|
| Always `1`, even when pressed | Check you're pressing button **{{ facts.buttons.example_label }}**. |
| Always `0` | Did you include `Pin.PULL_UP`? Without it, the pin floats. |
| Loop won't start | Press **Enter** on an empty line to end the indented block. |
| Loop won't stop | Click in the shell pane first, then **Ctrl+C**. |

## Have fun!

Combine this with [[one-led]]: make an LED light only while the button is held.

```python
while True:
    np[0] = (0, 32, 0) if btn.value() == 0 else (0, 0, 0)
    np.write()
    time.sleep(0.02)
```

Can you find the pins for the other buttons? (Hint: `{{ facts.firmware.pins_file }}`, or [[explore-badge]].)

Make each press step LED 0 to the next color in a list: red, green, blue, off. If one press skips several colors, wait for the button to be released before you check again.
