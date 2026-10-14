---
id: eink-updates
title: "Update the e-ink well: what to change, how often, and when to use the LEDs"
label: Update the screen well
topic: display
workshop: false
needs: [eink-refresh, on-time]
time: 30 min
touches: [apps/userA.py, hardware/display.py, hardware/lvgl_setup.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): how to force a full refresh, and whether partial refresh is on by default -->

**Goal:** Make an app whose screen changes as little as possible while still showing
what matters, with the LEDs covering anything that needs to be fast.

## You need

- Your app with a label that shows a changing value (from [[lvgl-hello]] or [[app-screen]])
- Your refresh time from [[eink-refresh]], and the timing patterns from [[on-time]]

## Steps

1. **Count your refreshes.** Wrap every `set_text()` in a helper that counts, and only
   changes the label when the text is different:

   ```python
       def show(self, label, text):
           if label.get_text() != text:
               label.set_text(text)
               self.refreshes = getattr(self, "refreshes", 0) + 1
               print(f"[{self.name}] refresh #{self.refreshes}: {text}")
   ```

   Use `self.show(self.label, ...)` everywhere you called `set_text()`.

2. **Decide how fresh it needs to be.** Show the seconds since start, every call:

   ```python
           self.show(self.label, str(time.ticks_ms() // 1000))
   ```

   Count the refreshes in a minute. Now show *minutes* instead (`// 60_000`). Same app,
   60 times fewer refreshes. Pick the coarsest unit that's still useful.

3. **Set a speed limit.** Even with real changes, don't refresh more often than the
   panel can keep up with. Hold changes back until enough time has passed. Add
   `self.last_refresh = None` to `switch_to_foreground()`, then:

   ```python
       def show(self, label, text):
           now = time.ticks_ms()
           self.pending = (label, text)
           if self.last_refresh is not None and time.ticks_diff(now, self.last_refresh) < 5000:
               return                      # too soon; keep the newest text for later
           label, text = self.pending
           if label.get_text() != text:
               label.set_text(text)
               self.last_refresh = now
   ```

   Now call `self.show()` with the same arguments every call, so the newest text goes
   up once the 5 seconds are over.

4. **Change several things in one go.** If two labels change, set both in the same
   call. LVGL redraws both together, in one refresh, instead of two.

5. **Fast feedback on the LEDs.** A button press should feel instant, and the e-ink
   can't do instant. Flash an LED the moment you press, and let the screen catch up
   (with `self.np` set up in `__init__`, as in [[animate-leds]]):

   ```python
           if {{ facts.buttons.app_1 }}:
               self.np[0] = (0, 16, 0); self.np.write()
               self.flash_until = time.ticks_add(time.ticks_ms(), 150)
               self.count += 1
           if getattr(self, "flash_until", None) and time.ticks_diff(time.ticks_ms(), self.flash_until) >= 0:
               self.np[0] = (0, 0, 0); self.np.write()
               self.flash_until = None
   ```

6. **Clean up the ghosts.** After many partial refreshes, do one full refresh, say
   every 10 updates or every 10 minutes. <!-- TODO(verify): the call for a full refresh -->

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
| Batch changes | two labels, one refresh |
| Only on change | no refresh when nothing's new |

**Full vs. partial refresh.** A partial refresh is faster and flashes less, but leaves
ghosts. A full refresh is slow and flashy, but clean. Mostly partial, with an
occasional full one, gets the best of both.

**Divide the work.** LEDs change in microseconds, and the e-ink in seconds. Use the LEDs
for "something happened just now" (a press, a message, a warning), and the screen
for "here's how things are" (a reading, a name, a status).

## Stuck?

| Symptom | Fix |
|---|---|
| The screen never updates | Is `self.last_refresh = None` in `switch_to_foreground()`? Is `self.last_refresh = now` inside the `if` that changes the label? |
| The last change never appears | You only call `show()` when something changes. Call it every time, so a pending change gets shown later. |
| `get_text` doesn't exist | Keep your own copy of what's shown in `self.shown` instead (as in [[name-badge]]). |
| The LED flash sticks on | `flash_until` never gets cleared. Check the second `if`. |

## Have fun!

- Print `self.refreshes` per hour. Can you get it under 60 for your app?
- A "something changed" dot: a small red mark in the corner that appears when the
  value moved a lot (see [[use-red]]).
- Show a trend arrow (↑ ↓) instead of every new reading.
- A talk timer: the screen updates once a minute, the LEDs count down the last minute, and the screen turns red when you're over time (see [[use-red]]).
- A dungeon crawler: the buttons move you one square at a time, and only the squares that changed are redrawn (see [[draw-pixels]] and [[fsm]]).
