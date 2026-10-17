---
id: on-time
title: Do things on time (ticks_ms, ticks_diff, and your time budget)
label: Doing things on time
topic: write-app
workshop: false
needs: [fsm]
time: 25 min
touches: [apps/userA.py, apps/base_app.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Make your app do things at the right time without ever waiting, and measure
how much of the processor your app is using.

## You need

- Your app from [[fsm]]

## Steps

1. **Meet the clock.** At `>>>`:

   ```python
   import time
   time.ticks_ms()
   time.ticks_ms()
   ```

   Milliseconds since the badge started. It only goes up (until it wraps around; see below).

2. **Measure a gap the right way:**

   ```python
   t0 = time.ticks_ms()
   # ...wait a moment, then:
   time.ticks_diff(time.ticks_ms(), t0)
   ```

   Always `ticks_diff(newer, older)`, never `newer - older`.

3. **Periodic: "every N ms."** Replace the call-counting in your [[fsm]] app's
   `FLASHING` state with timestamps. Add `import time` at the top of the file and
   `self.last = 0` in `__init__`, then:

   ```python
           elif self.state == FLASHING:
               now = time.ticks_ms()
               if time.ticks_diff(now, self.last) >= 250:     # every 250 ms
                   self.last = now
                   on = self.count % 2 == 0
                   self.np[0] = (32, 32, 0) if on else (0, 0, 0)
                   self.np.write()
                   self.count += 1
                   if self.count == 10:
                       self.state, self.until = COOLDOWN, time.ticks_add(now, 3000)
   ```

4. **One-shot: "at time T."** For the cooldown, store a deadline instead of counting:

   ```python
           elif self.state == COOLDOWN:
               if time.ticks_diff(time.ticks_ms(), self.until) >= 0:   # deadline passed
                   self.state = IDLE
   ```

   Change `foreground_sleep_ms` to 50, then 300. The flash timing barely changes now.
   (Before, it would have.)

5. **Event-driven: "when X happens."** `IDLE` is already event-driven: it does nothing
   until the button. Most of an app's time should be spent in states like that.

6. **Measure your budget.** How long does one call take, and how often do you get one?
   Add at the top and bottom of `run_foreground()`:

   ```python
       def run_foreground(self):
           t0 = time.ticks_us()
           gap = time.ticks_diff(t0, getattr(self, "t_prev", t0))
           self.t_prev = t0
           # ...your states...
           took = time.ticks_diff(time.ticks_us(), t0)
           if took > 5000 or gap > 200_000:
               print(f"call took {took} us, {gap} us since the last one")
   ```

   It only prints when something's slow. Press buttons, open the menu, change the
   screen. What makes the gap grow?

**✅ Done when** your flashes keep the same rhythm whatever `foreground_sleep_ms` is,
and you know how long your app's calls take.

## What just happened

**Three kinds of timing:**

| Kind | Example | How |
|---|---|---|
| Periodic | blink every 250 ms, read a sensor every 5 s | remember when you last did it; do it again when `ticks_diff` ≥ the period |
| One-shot | stop cooling down in 3 s | store a deadline with `ticks_add`; check whether it's passed |
| Event-driven | when a button is pressed | check for the event each call; do nothing otherwise |

**Why `ticks_diff`?** `ticks_ms()` is a small number that **wraps around** to 0
after a while (about 12 days on the ESP32-S3), so it fits in a fast integer. Plain
subtraction gives nonsense across the wrap. `ticks_diff()` and `ticks_add()` do the
arithmetic the wrap-safe way.

**Your time budget.** Your app gets a call roughly every `foreground_sleep_ms`, but
only if everyone else returns on time. Every task on the badge shares the same
processor (see [[asyncio-basics]]). If yours takes 5 ms and LVGL's redraw takes 50 ms,
your next call comes late. Timestamps make your app *correct* when calls are late;
measuring tells you *how* late, and whether it's your fault.

`ticks_us()` is the same clock in microseconds, for measuring short things.

## Stuck?

| Symptom | Fix |
|---|---|
| `AttributeError: ... 'last'` | Set `self.last = 0` in `__init__`. |
| It never flashes | Did you update `self.last = now` *inside* the `if`? |
| Times are huge or negative | You used `-` instead of `ticks_diff`, or swapped its arguments (newer first). |
| Gaps of a second or more | Something is hogging the processor. A screen refresh? See [[eink-refresh]] and [[hog-the-cpu]]. |

## Have fun!

- Blink two LEDs at two different rates from the same app.
- Make a double-click detector: two presses less than 400 ms apart.
- Find your app's worst call over a minute. Keep `self.worst` and print it on a button.
