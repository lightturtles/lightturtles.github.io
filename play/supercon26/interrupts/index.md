---
id: interrupts
title: "Polling vs. interrupts: catch every button press"
label: Polling vs. interrupts
topic: gpio
workshop: false
needs: [read-button, asyncio-basics]
time: 25 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): is button {{ facts.buttons.example_label }} a direct GPIO (not through an I/O expander or a keyboard scanner)? Interrupts need a direct pin. -->

**Goal:** Miss button presses by polling too slowly, then catch every one with an
interrupt, and hand the work off to an asyncio task.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- The button setup from [[read-button]]

## Steps

1. **Miss some presses.** Press **Ctrl+C**, then poll slowly while you tap the button
   quickly, 10 times:

   ```python
   from machine import Pin
   import time
   btn = Pin({{ facts.buttons.example_pin }}, Pin.IN, Pin.PULL_UP)

   presses, was = 0, 1
   for i in range(50):              # 5 seconds
       now = btn.value()
       if was == 1 and now == 0:    # it just went down
           presses += 1
       was = now
       time.sleep(0.1)
   presses
   ```

   Fewer than 10? A press shorter than 0.1 s can fall between two checks.

2. **Interrupt instead.** Ask the chip to call a function the moment the pin falls:

   ```python
   count = 0
   def on_press(pin):
       global count
       count += 1

   btn.irq(trigger=Pin.IRQ_FALLING, handler=on_press)
   ```

   Tap 10 times, then check `count`. It may be *more* than 10: see step 3.

3. **Bounce.** A button's metal contacts rattle for a millisecond or two, so one press
   can look like several. Ignore edges that come too soon after the last:

   ```python
   count, last = 0, 0
   def on_press(pin):
       global count, last
       now = time.ticks_ms()
       if time.ticks_diff(now, last) > 50:
           count += 1
       last = now

   btn.irq(trigger=Pin.IRQ_FALLING, handler=on_press)
   ```

   Tap 10 times. Exactly 10 now?

4. **Hand the work to a task.** A handler should be tiny: note that something happened,
   and leave. The real work goes in an asyncio task, woken with a `ThreadSafeFlag`
   (see [[pass-data]]):

   ```python
   import asyncio
   asyncio.new_event_loop()
   flag = asyncio.ThreadSafeFlag()

   def on_press(pin):
       flag.set()                  # that's all

   async def worker():
       for i in range(5):
           await flag.wait()
           print("pressed! doing the slow part...")
           await asyncio.sleep_ms(500)

   btn.irq(trigger=Pin.IRQ_FALLING, handler=on_press)
   asyncio.run(worker())
   ```

5. **Turn it off** when you're done, then **Ctrl+D**:

   ```python
   btn.irq(handler=None)
   ```

**✅ Done when** you've caught presses polling missed, and debounced them so each press
counts once.

## What just happened

**Polling** asks "is it pressed?" over and over. It's simple, and the badge's own apps
mostly poll: each `run_foreground()` call checks the buttons. Its catch: anything
shorter than the gap between checks can be missed, and checking more often costs
processor time.

An **interrupt** turns that around. The pin hardware watches for the edge itself and
interrupts whatever's running to call your **handler**. Nothing is missed, and no time
is spent checking.

**Rules for handlers.** A handler runs *in the middle of* other code, at a moment you
don't choose:

- Do as little as possible: set a flag, bump a counter, note the time.
- Don't print, sleep, or touch the screen or I2C. Hand that to a task.
- On the ESP32, pin handlers run "soft" by default: MicroPython schedules them to run
  very soon after the edge, so they *can* allocate memory. A `hard=True` handler runs
  immediately and can't. From one of those, call `micropython.schedule(func, arg)` to
  run the rest a moment later.

<!-- TODO(diagram): timeline with polling dots and a short press falling between them; interrupt arrow catching it; handler → ThreadSafeFlag → task -->

## Stuck?

| Symptom | Fix |
|---|---|
| `count` never goes up | Is the button really on that pin? Check with `btn.value()` while holding it. |
| One press counts many times | That's bounce. Make the 50 ms bigger. |
| Presses counted on release too | Use `Pin.IRQ_FALLING` (press) only, not `IRQ_RISING`. |
| The badge's own program stopped reacting to the button | Your `irq()` replaced its handler. **Ctrl+D** to start over. |

## Have fun!

- Measure your reaction time: light an LED after a random delay, and time the press
  in the handler with `time.ticks_us()`.
- Count presses in the background of your app, and show the total when it opens.
- Detect a long press: trigger on both edges and compare the times.
