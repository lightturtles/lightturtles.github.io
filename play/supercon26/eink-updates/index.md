---
id: eink-updates
title: "Update the e-ink well: what to change, how often, and when to use the LEDs"
label: Update the screen well
topic: display
workshop: false
needs: [eink-refresh, on-time]
time: 30 min
touches:
  - lib/epd.py#EPaperDisplay.is_done_updating   # False while a refresh is running
  - lib/epd.py#EPaperDisplay.run                # an update() asked for mid-refresh is dropped
  - lib/led_bar.py#leds
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Make an app whose screen changes as little as possible while still showing
what matters, with the LEDs covering anything that needs to be fast.

## You need

- Your app from [[lvgl-hello]] (a label, and a `show()` method that does `refr_now` and `update`)
- Your refresh time from [[eink-refresh]], and the timing patterns from [[on-time]]

## Steps

1. **Count your refreshes.** Add a method that changes the label and refreshes, but
   only when the text is different. In `__init__`, add `self.shown = None` and
   `self.refreshes = 0`, and add `import time` at the top. Then:

   ```python
       def show_text(self, text):
           if text == self.shown:
               return                                  # nothing new
           self.shown = text
           self.label.set_text(text)
           self.show()
           self.refreshes += 1
           print(f"[{self.name}] refresh #{self.refreshes}: {text}")
   ```

2. **Decide how fresh it needs to be.** Show the seconds since start, every call. At the
   end of `run()`:

   ```python
           self.show_text(str(time.ticks_ms() // 1000))
   ```

   Open your app and watch the shell. A refresh every second can't work: each one takes
   longer than that, and the ones asked for mid-refresh are dropped. Now show *minutes*
   instead (`// 60_000`). Same app, 60 times fewer refreshes. Pick the coarsest unit
   that's still useful.

3. **Set a speed limit, and wait for the panel.** Even with real changes, don't refresh
   more often than you need. Add `self.last_refresh = time.ticks_ms()` to `__init__`,
   and two checks to `show_text()`, after the first one:

   ```python
           if not display.is_done_updating():
               return                                  # the panel is busy; try next call
           if time.ticks_diff(time.ticks_ms(), self.last_refresh) < 60_000:
               return                                  # too soon; try next call
   ```

   and `self.last_refresh = time.ticks_ms()` right after `self.show()`. Because
   `run()` calls `show_text()` every time with the newest text, the newest text goes
   up as soon as the panel is free and a minute has passed. Nothing gets lost. (The
   panel alone takes over half a minute per refresh, so `is_done_updating()` is doing
   most of the limiting.)

4. **Change several things in one go.** If two labels change, set both, then call
   `show()` once. One refresh instead of two.

5. **Fast feedback on the LEDs.** A button press should feel instant, and the e-ink
   can't do instant. Flash an LED the moment you press, and let the screen catch up.
   Add `from lib.led_bar import leds` at the top, `self.flash_until = None` and
   `self.count = 0` in `__init__`, and this in `run()`. (It uses the *last* LED: the
   first one belongs to the display, below.)

   ```python
           if {{ facts.buttons.app_1 }}:
               leds[{{ facts.leds.count }} - 1] = (0, 16, 0)
               leds.write()
               self.flash_until = time.ticks_add(time.ticks_ms(), 150)
               self.count += 1
           if self.flash_until is not None and time.ticks_diff(time.ticks_ms(), self.flash_until) >= 0:
               leds[{{ facts.leds.count }} - 1] = (0, 0, 0)
               leds.write()
               self.flash_until = None
   ```

**✅ Done when** your app refreshes no more than once every few seconds, never shows a
stale value for long, and answers every button press instantly with an LED.

## What just happened

Every e-ink refresh costs time (seconds, during which the badge is busy), power, and a
visible flash. So the question isn't "how fast can I update?" but "how *rarely* can I
update and still be useful?"

| Choice | Fewer refreshes because… |
|---|---|
| Coarser units, more rounding | small changes don't change the text |
| A speed limit | bursts of changes become one refresh |
| Wait until the panel is free | nothing is asked for mid-refresh, so nothing is dropped |
| Batch changes | two labels, one refresh |
| Only on change | no refresh when nothing's new |

**Why wait for the panel?** The display task copies the framebuffers when a refresh
starts, and forgets any `update()` that arrives before it ends. Ask too soon and the
screen keeps showing the old value, with nothing to tell you. `display.is_done_updating()`
is how you know it's safe to ask.

The display code adds one more trick, on the first LED: blue while LVGL draws or a PNG
loads, blinking red while the panel refreshes, then green for a moment when it's done.
People know to wait. (It also turns all the LEDs off at the start and end of each
refresh, so an LED your app lit may go dark then.)

**Divide the work.** LEDs change in microseconds, and the e-ink in seconds. Use the LEDs
for "something happened just now" (a press, a message, a warning), and the screen
for "here's how things are" (a reading, a name, a status).

## Stuck?

| Symptom | Fix |
|---|---|
| The screen never updates | Is `self.last_refresh = time.ticks_ms()` inside `show_text()`, *after* the checks? Is `show_text()` called every time? |
| The last change never appears | You only call `show_text()` when something changes. Call it every time, so a held-back change gets shown later. |
| The LED flash sticks on | `flash_until` never gets cleared. Check the second `if`. |
| The LED flash comes late | A refresh was being sent to the panel when you pressed, and that part holds up the whole badge (see [[eink-refresh]]). |

## Have fun!

- Print `self.refreshes` per hour. Can you get it under 60 for your app?
- A "something changed" dot: a small red mark in the corner that appears when the
  value moved a lot (see [[use-red]]).
- Show a trend arrow (↑ ↓) instead of every new reading.
- A talk timer: the screen updates once a minute, the LEDs count down the last minute, and the screen turns red when you're over time (see [[use-red]]).
- A dungeon crawler: the buttons move you one square at a time, and only the squares that changed are redrawn (see [[draw-pixels]] and [[fsm]]).
