---
id: animate-leds
title: Animate the LEDs without blocking (one step per tick)
label: Animate without blocking
topic: gpio
workshop: false
needs: [all-leds, on-time]
time: 20 min
touches: [apps/userA.py]
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
   Put that in `run_foreground()` and the badge freezes (see [[hog-the-cpu]]). So
   split it: **one frame per call**, and remember where you were in `self`.

2. **Set up once.** At the top of `{{ facts.firmware.user_app }}`, paste `wheel()` from
   [[all-leds]], and add:

   ```python
   import time
   from machine import Pin
   import neopixel
   ```

   In `__init__`:

   ```python
           self.np = neopixel.NeoPixel(Pin({{ facts.leds.pin }}), {{ facts.leds.count }})
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
           n = len(self.np)
           for i in range(n):
               self.np[i] = wheel(i * 256 // n + self.offset)
           self.np.write()
           self.offset = (self.offset + 8) % 256
   ```

4. **Call it** from `run_foreground()` (and turn the LEDs off when you go home):

   ```python
       def run_foreground(self):
           self.animate()
           if {{ facts.buttons.home }}:
               self.np.fill((0, 0, 0)); self.np.write()
               self.switch_to_background()
   ```

5. Save, **Ctrl+D**, open your app. The rainbow scrolls, and the home button still works.

6. **Speed it up and slow it down** with buttons: change `self.frame_ms` on
   **{{ facts.buttons.app_1_label }}** and **{{ facts.buttons.app_2_label }}**. What's
   the fastest it'll go? (Hint: the app is only called every `foreground_sleep_ms`.)

**✅ Done when** the rainbow scrolls smoothly and every button still responds.

## What just happened

An animation is a state machine with one state that never ends (see [[fsm]]): its
state is `self.offset`, and each step draws a frame and moves it along. Timing each
frame with `ticks_diff` (not counting calls) keeps the speed steady even when calls
come late.

`np.write()` is fast: about 30 µs per LED, so {{ facts.leds.count }} LEDs take well under a
millisecond. That's why the LEDs can animate smoothly while the e-ink can't. Use the
LEDs for anything that moves or needs to react *now*, and the screen for what changes
slowly (see [[eink-updates]]).

A frame can't come faster than your app is called. If `frame_ms` is smaller than
`foreground_sleep_ms`, you'll get one frame per call, and the badge sets the speed.

## Stuck?

| Symptom | Fix |
|---|---|
| `NameError: wheel` | Paste `wheel()` above `class App`, at the left margin. |
| The animation stutters every so often | Another task took a long turn (often the screen). Normal; see [[on-time]] to measure it. |
| LEDs stay lit after leaving | Turn them off before `switch_to_background()`. |
| Rainbow only runs while the app is open | Call `self.animate()` from `run_background()` too, and see [[background-app]]. |

## Have fun!

- A "breathing" fade: brightness from `math.sin()` of the time.
- Make it react: flash white for one frame on every button press.
- Two animations at once on different halves of the LEDs, at different speeds.
