---
id: hog-the-cpu
title: Hog the processor; find the culprit with Ctrl+C; fix it
label: Preventing freezes
topic: write-app
workshop: false
needs: [first-app, break-and-restore]
time: 20 min
touches:
  - apps/base_app.py#BaseApp.arun         # run(), then the await that lets everyone else go
  - lib/app_switcher.py#AppSwitcher.arun  # checks Menu +/- only between calls to the app
  - lib/button.py#scan                    # the 1 ms button task; a press it never sees is lost
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Freeze the whole badge from inside your app, find the exact line responsible
from a traceback, and fix it so the badge stays responsive.

## You need

- Your app from [[first-app]], open in Thonny from the badge

## Steps

1. **Add some slow work.** In `{{ facts.firmware.user_app }}`, change the import to
   `from lib.button import UserA, UserB`, and add a "count to two million" job on
   **{{ facts.buttons.app_2_label }}** at the end of `run()`:

   ```python
       def run(self):
           # ...what your run() already does stays the same, then:
           if {{ facts.buttons.app_2 }}:
               print("counting...")
               n = 0
               while n < 2_000_000:
                   n += 1
               print("done", n)
   ```

2. Save, **Ctrl+D**, open your app, and press **{{ facts.buttons.app_2_label }}**. While it's counting, try
   everything else: **{{ facts.buttons.app_1_label }}**, **{{ facts.buttons.home_label }}** to go back to the menu. Nothing responds until
   `done` prints. Does the badge notice the presses afterwards, or are they lost? (Try
   one quick press, and one you hold until `done` appears.)

3. **Freeze it for good.** Change `while n < 2_000_000:` to `while True:`. Save,
   **Ctrl+D**, open your app, and press **{{ facts.buttons.app_2_label }}**. The badge is stuck, and will stay stuck.

4. **Find the culprit.** Click in the shell and press **Ctrl+C**. You'll get something like:

   ```
   Traceback (most recent call last):
     File "main.py", line 69, in <module>
     File "asyncio/core.py", line 1, in run
     ...
     File "lib/app_switcher.py", line 110, in arun
     File "apps/base_app.py", line 29, in arun
     File "apps/my_app.py", line 27, in run
   KeyboardInterrupt:
   ```

   Read it bottom-up, like in [[break-and-restore]]. The last line says *what*
   happened: you pressed Ctrl+C (`KeyboardInterrupt`). The line above says *where*
   the badge was at that moment: your file, your line. Above that, `base_app.py`
   called your `run()`, the switcher called `base_app.py`, and the asyncio scheduler
   called the switcher.

5. **Fix it: do a little at a time.** The badge calls `run()` again and again, so let
   it. Each call does a small slice of the work, and the count lives in `self` between
   calls. Add `self.n = 0` and `self.counting = False` to `__init__`, and replace the
   counting job with:

   ```python
           if {{ facts.buttons.app_2 }}:
               print("counting...")
               self.n = 0
               self.counting = True
           if self.counting:
               for _ in range(10_000):       # one small slice per call
                   self.n += 1
               if self.n >= 2_000_000:
                   print("done", self.n)
                   self.counting = False
   ```

6. Save, **Ctrl+D**, and try again. Now the other buttons work while it counts. It
   takes longer, though: 200 slices, with a `sleep_ms` nap after each one. Can you go
   back to the menu mid-count? What happens to the count when you open the app again?

7. **Measure a slice.** How long does one call hold the processor? Wrap the slice:

   ```python
   import time   # at the top of the file

               t0 = time.ticks_ms()
               for _ in range(10_000):
                   self.n += 1
               print("slice took", time.ticks_diff(time.ticks_ms(), t0), "ms")
   ```

   Aim for a few milliseconds. Change `10_000` and watch the number change.

**✅ Done when** you've found the frozen line from the Ctrl+C traceback alone, and your
count runs without freezing the badge.

## What just happened

Your app runs inside the switcher's task (see [[asyncio-basics]]). `run()` is called,
then `base_app.py` does `await aio.sleep_ms(self.sleep_ms)` so everyone else gets a
turn. If `run()` never returns, that `await` never comes, and *nothing else on the
badge runs*: not the button reader, not the screen updater, not the menu. The button
reader only notices a button that's *down* when it gets its turn, so a press that
starts and ends during a freeze is gone for good.

**Ctrl+C** raises a `KeyboardInterrupt` in whatever code is running at that moment.
On a frozen badge, that's always the guilty line, so the traceback points straight at
it. That's the most useful debugging trick on the badge, and it costs nothing.

The fix is the shape every app takes: **keep your state in `self`, do one small step per
call, and return.** [[fsm]] turns that into a habit. The usual hogs in real apps are:

- `time.sleep(...)`: use a timestamp and `time.ticks_diff()` instead (see [[on-time]])
- `while` loops waiting for something to happen: check once per call instead
- network requests and big file reads: do them rarely, and expect a stutter (see [[web-data]])

A badge that **stutters** rather than freezes has the same problem, just smaller. Ctrl+C
won't catch it in the act, but timing like step 7 will.

<!-- TODO(diagram): two timelines. Top: app call → await → other tasks → app call … Bottom: app call that never returns; everything else greyed out; Ctrl+C arrow pointing into it -->

## Stuck?

| Symptom | Fix |
|---|---|
| Ctrl+C does nothing | Click in the shell first, then press it again. Still nothing? Press **{{ facts.power.reset_button }}**, then see [[recover]]. |
| The traceback ends in `asyncio/core.py`, not your app | You pressed Ctrl+C between calls, so nothing was stuck. Make sure the badge is frozen first. |
| The traceback ends in `time.sleep` or a library | Read one line *up*: that's where *your* code called it. |
| `AttributeError: ... 'counting'` | Add `self.counting = False` (and `self.n = 0`) to `__init__`. |
| Ctrl+D doesn't restart a frozen badge | Ctrl+D only works at `>>>`. Ctrl+C first, then Ctrl+D. |

## Have fun!

- Find the biggest slice that still feels responsive. Then make the count finish sooner without freezing anything: what happens if you set `self.sleep_ms = 0` while counting?
- Make a progress bar: print `self.n * 100 // 2_000_000` every 10 %.
- Have a logic analyzer? Toggle a spare SAO GPIO (see [[sao-pinout]]) high at the start of
  `run()` and low at the end. You'll *see* every slice, and printing won't
  slow your code down while you measure it.
- A progressive fractal: compute a Mandelbrot set one strip per slice, and update the screen as each strip finishes (see [[draw-pixels]] and [[eink-updates]]).
- A maze generator and solver: build the maze one step per slice, then watch the solver draw its path. Pick the algorithm with a button (depth-first, breadth-first, follow-the-wall) and see which one wanders the most (see [[draw-pixels]] and [[fsm]]).
