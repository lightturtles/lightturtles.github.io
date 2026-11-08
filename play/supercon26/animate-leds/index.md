---
id: animate-leds
title: Animate the LEDs without blocking (one step per tick)
label: Animate without blocking
topic: gpio
workshop: false
needs: [all-leds, on-time]
time: 20 min
touches:
  - lib/led_bar.py#leds
  - lib/led_bar.py#LedBar.set_sequence   # hand a generator to the leds.update() task in main.py
  - lib/led_bar.py#LedBar.menu_display   # pauses the sequence; nothing unpauses it but you
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Move the rainbow from [[all-leds]] into your app, so it scrolls while the rest
of the badge keeps working.

## You need

- The `wheel()` rainbow from [[all-leds]]
- Your app, and the timing pattern from [[on-time]]

## Steps

1. **Spot the problem.** The REPL version is a `while True` loop with `time.sleep()`.
   Put that in `run()` and the badge freezes (see [[hog-the-cpu]]). So split it:
   **one frame per call**, and remember where you were in `self`.

2. **Set up once.** At the top of `{{ facts.firmware.user_app }}`, paste `wheel()` from
   [[all-leds]], and add:

   ```python
   import time
   from lib.led_bar import leds
   ```

   In `__init__`:

   ```python
           self.offset = 0                 # where the rainbow is
           self.last_frame = 0
           self.frame_ms = 50              # 20 frames a second
   ```

3. **One step per call.** Add a method that draws the *next* frame only when it's due:

   ```python
       def animate(self):
           now = time.ticks_ms()
           if time.ticks_diff(now, self.last_frame) < self.frame_ms:
               return                      # not time yet
           self.last_frame = now
           for i in range({{ facts.leds.count }}):
               leds[i] = wheel(i * 256 // {{ facts.leds.count }} + self.offset)
           leds.write()
           self.offset = (self.offset + 8) % 256
   ```

4. **Call it** every time from `run()`:

   ```python
       def run(self):
           self.animate()
   ```

5. Save, **Ctrl+D**, open your app. The rainbow scrolls, and **{{ facts.buttons.home_label }}** still takes
   you back to the menu (which turns your rainbow off and shows the menu instead).

6. **Speed it up and slow it down** with buttons: change `self.frame_ms` on
   **{{ facts.buttons.app_1_label }}** and **{{ facts.buttons.app_2_label }}**. What's
   the fastest it'll go? (Hint: the app is only called every `self.sleep_ms`, 100 ms
   unless you changed it.)

7. **Or let the firmware animate for you.** `main.py` runs a task, `leds.update()`, that
   plays an animation handed to it as a **generator**: a function that `yield`s each
   frame (a list of colors) and how many ms to show it. Add this above the class:

   ```python
   def rainbow():
       offset = 0
       while True:
           yield [wheel(i * 256 // {{ facts.leds.count }} + offset) for i in range({{ facts.leds.count }})], 50
           offset = (offset + 8) % 256
   ```

   and replace `run()` with:

   ```python
       def run(self):
           if self.launched:
               leds.set_sequence(rainbow)
               leds.unpause()
   ```

   It runs at the full 20 frames a second, however slowly your app is called. Leave out
   `leds.unpause()` and nothing happens: the menu pauses the animation task every time
   it shows, and nothing in the firmware un-pauses it.

**✅ Done when** the rainbow scrolls smoothly and every button still responds.

## What just happened

An animation is a state machine with one state that never ends (see [[fsm]]): its
state is `self.offset`, and each step draws a frame and moves it along. Timing each
frame with `ticks_diff` (not counting calls) keeps the speed steady even when calls
come late.

`leds.write()` is fast: about 30 µs per LED, so {{ facts.leds.count }} LEDs take well under a
millisecond. That's why the LEDs can animate smoothly while the e-ink can't. Use the
LEDs for anything that moves or needs to react *now*, and the screen for what changes
slowly (see [[eink-updates]]).

A frame can't come faster than your app is called. If `frame_ms` is smaller than
`sleep_ms`, you'll get one frame per call, and the badge sets the speed. A generator
handed to `leds.set_sequence()` doesn't have that limit: it runs in its own task, and
says for itself how long to wait between frames. It's the same idea as `animate()`, with
the "where was I?" kept inside the generator instead of in `self`.

## Stuck?

| Symptom | Fix |
|---|---|
| `NameError: wheel` | Paste `wheel()` above `class MyApp`, at the left margin. |
| The animation stutters every so often | Another task took a long turn (often the screen). Normal; see [[on-time]] to measure it. |
| `set_sequence` does nothing | Call `leds.unpause()` after it. |
| The sequence stops when you go to the menu, and doesn't come back | The menu paused it. Set it again (and unpause) in the `if self.launched:` part of `run()`. |
| Rainbow only runs while the app is open | That's how apps work: only the open one is called (see [[firmware-diagram]]). |

## Have fun!

- A "breathing" fade: brightness from `math.sin()` of the time.
- Make it react: flash white for one frame on every button press.
- Two animations at once on different halves of the LEDs, at different speeds.
