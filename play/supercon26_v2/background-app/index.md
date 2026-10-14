---
id: background-app
title: Write an app that works in the background, with no screen
label: A background-only app
topic: write-app
workshop: false
needs: [fsm]
time: 25 min
touches: [apps/userA.py, apps/base_app.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Build an app whose real job happens while some other app has the screen: a
focus timer that lights the LEDs as the minutes pass.

## You need

- Your app from [[fsm]], and the LED setup from [[one-led]]

## Steps

1. **Plan the states.** A focus timer (the "Pomodoro" technique) alternates work and
   breaks:

   | State | Lasts | LEDs |
   |---|---|---|
   | `WORK` | 25 min | one more LED lights green as each part passes |
   | `BREAK` | 5 min | all blue |
   | `OFF` | until started | dark |

2. **Do the work in `run_background()`.** It's called every `background_sleep_ms`,
   whichever app is on screen, so the timer runs while you use the rest of the badge:

   ```python
   import time
   from machine import Pin
   import neopixel

   OFF, WORK, BREAK = 0, 1, 2
   WORK_MS, BREAK_MS = 25 * 60_000, 5 * 60_000

   class App(BaseApp):
       def __init__(self, name, badge):
           super().__init__(name, badge)
           self.background_sleep_ms = 1000        # once a second is plenty
           self.np = neopixel.NeoPixel(Pin({{ facts.leds.pin }}), {{ facts.leds.count }})
           self.state = OFF

       def start_state(self, state):
           self.state, self.started = state, time.ticks_ms()
           print(f"[{self.name}] -> {state}")

       def run_background(self):
           if self.state == OFF:
               return
           elapsed = time.ticks_diff(time.ticks_ms(), self.started)
           n = len(self.np)
           if self.state == WORK:
               lit = elapsed * n // WORK_MS
               for i in range(n):
                   self.np[i] = (0, 16, 0) if i < lit else (0, 0, 0)
               if elapsed >= WORK_MS:
                   self.start_state(BREAK)
           elif self.state == BREAK:
               self.np.fill((0, 0, 16))
               if elapsed >= BREAK_MS:
                   self.start_state(WORK)
           self.np.write()
   ```

3. **Keep the foreground tiny.** Opening the app just starts or stops the timer, then
   goes straight home:

   ```python
       def run_foreground(self):
           if self.state == OFF:
               self.start_state(WORK)
           else:
               self.state = OFF
               self.np.fill((0, 0, 0)); self.np.write()
           self.switch_to_background()
   ```

   <!-- TODO(verify): is it OK to call switch_to_background() on the first foreground call, before the screen is drawn? -->

4. **Test it fast.** Change `WORK_MS` to `20_000` and `BREAK_MS` to `5_000` while you
   try it. Save, **Ctrl+D**, open your app once from the menu, and go use another app.
   The LEDs keep counting.

5. Put the real times back when it works.

**✅ Done when** the timer keeps running and lighting LEDs while you use other apps.

## What just happened

Every app on the badge is always in one of two states (see [[first-app]]): foreground,
with the screen, or background. Most apps do nothing in the background. Yours does
everything there, and uses the foreground only as an on/off switch.

The background has rules of its own:

- **No screen.** It belongs to whatever app is in the foreground. Show your status
  with the LEDs, a sound, or a message, instead.
- **Slow and steady.** `background_sleep_ms` sets how often you're called. Pick the
  slowest that works: every call costs every other app a little time (see [[on-time]]).
- **Share politely.** If another app also uses the LEDs, you'll fight. See
  [[share-hardware]] for how to split them.
- **Timestamps, not counts.** Background calls are even less regular than foreground
  ones, so the timer measures elapsed time instead of counting calls.

## Stuck?

| Symptom | Fix |
|---|---|
| The LEDs only update while the app is open | Your code is in `run_foreground()`. Move it to `run_background()`. |
| The app opens and closes instantly | That's step 3 working. Watch the LEDs. |
| Another app keeps turning your LEDs off | See [[share-hardware]]. |
| LEDs flicker once a second | You're `fill`ing then setting them. Build the colors first, then `write()` once. |

## Have fun!

- Flash all the LEDs three times when a work period ends.
- Use the screen anyway: when the app *is* opened, show the minutes left before going home.
- Save the number of finished work periods with [[save-settings]].
