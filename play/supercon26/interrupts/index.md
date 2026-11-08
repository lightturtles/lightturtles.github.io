---
id: interrupts
title: "Polling vs. interrupts: catch every button press"
label: Polling vs. interrupts
topic: gpio
workshop: false
needs: [read-button, asyncio-basics]
time: 25 min
touches:
  - lib/button.py#scan              # the firmware polls every button, every 1 ms; no interrupts
  - lib/button.py#Button.scan       # a press is forgotten as soon as the button is released
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify) on a real badge: the IRQ and ThreadSafeFlag steps -->

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

**Polling** asks "is it pressed?" over and over. It's simple, and it's what the badge
does: a task in `main.py` reads all five buttons every millisecond, and remembers a
press until an app asks `UserA.pressed()`. Its catch: anything shorter than the gap
between checks can be missed, and checking more often costs processor time. The badge
has a second, sneakier gap: `Button.scan()` forgets a press as soon as the button is
let go, so an app that only asks every 100 ms can still miss a quick tap (see
[[first-app]]).

Every button on this badge is wired straight to its own GPIO pin
(`lib/button.py` lists them), so any of them can trigger an interrupt.

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
| The badge's own program still reacts to the button | That's fine: it polls the pin, and your interrupt doesn't change that. Both see the press. |

## Have fun!

- Measure your reaction time: light an LED after a random delay, and time the press
  in the handler with `time.ticks_us()`.
- Count presses with an interrupt while another app is open (set it up the first time
  your app opens), and show the total when you come back.
- Detect a long press: trigger on both edges and compare the times.
