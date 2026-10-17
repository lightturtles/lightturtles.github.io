---
id: hog-the-cpu
title: Hog the processor; find the culprit with Ctrl+C; fix it
label: Preventing freezes
topic: write-app
workshop: false
needs: [first-app, break-and-restore]
time: 20 min
touches: [main.py, apps/base_app.py, apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): traceback shape and button API are from the 2025 firmware -->

**Goal:** Freeze the whole badge from inside your app, find the exact line responsible
from a traceback, and fix it so the badge stays responsive.

## You need

- Your app from [[first-app]], open in Thonny from the badge

## Steps

1. **Add some slow work.** In `run_foreground()`, add a "count to two million" job on
   **{{ facts.buttons.app_2_label }}**:

   ```python
       def run_foreground(self):
           if {{ facts.buttons.app_2 }}:
               print("counting...")
               n = 0
               while n < 2_000_000:
                   n += 1
               print("done", n)
           # ...the rest of your run_foreground stays the same
   ```

2. Save, **Ctrl+D**, open your app, and press **{{ facts.buttons.app_2_label }}**. While it's counting, try
   everything else: the other buttons, **{{ facts.buttons.home_label }}** to go home. Nothing responds until
   `done` prints. Does the badge notice the presses afterwards, or are they lost?

3. **Freeze it for good.** Change `while n < 2_000_000:` to `while True:`. Save,
   **Ctrl+D**, open your app, and press **{{ facts.buttons.app_2_label }}**. The badge is stuck, and will stay stuck.

4. **Find the culprit.** Click in the shell and press **Ctrl+C**. You'll get something like:

   ```
   Traceback (most recent call last):
     File "main.py", line 75, in <module>
     File "asyncio/core.py", line 1, in run
     ...
     File "apps/base_app.py", line 45, in run
     File "apps/userA.py", line 27, in run_foreground
   KeyboardInterrupt:
   ```

   Read it bottom-up, like in [[break-and-restore]]. The last line says *what*
   happened: you pressed Ctrl+C (`KeyboardInterrupt`). The line above says *where*
   the badge was at that moment: your file, your line. Above that, `base_app.py`
   called your method, and the asyncio scheduler called `base_app.py`.

5. **Fix it: do a little at a time.** The badge calls `run_foreground()` again and
   again, so let it. Each call does a small slice of the work, and the count lives in
   `self` between calls:

   ```python
       def run_foreground(self):
           if {{ facts.buttons.app_2 }}:
               print("counting...")
               self.n = 0
               self.counting = True
           if getattr(self, "counting", False):
               for _ in range(10_000):       # one small slice per call
                   self.n += 1
               if self.n >= 2_000_000:
                   print("done", self.n)
                   self.counting = False
           # ...the rest of your run_foreground
   ```

6. Save, **Ctrl+D**, and try again. The count takes about as long, but now the other
   buttons work while it runs. Can you go home mid-count?

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

Your app runs inside a task (see [[asyncio-basics]]). `run_foreground()` is called,
then `base_app.py` does `await aio.sleep_ms(...)` so everyone else gets a turn. If your
method never returns, that `await` never comes, and *nothing else on the badge runs*:
not the button reader, not the screen updater, not the menu.

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
| `AttributeError: ... 'n'` | You pressed nothing yet, so `self.n` doesn't exist. That's why the fix checks `counting` with `getattr` first. |
| Ctrl+D doesn't restart a frozen badge | The badge reads Ctrl+D in a task, and nothing is running. Ctrl+C first, then Ctrl+D. |

## Have fun!

- Find the biggest slice that still feels responsive. Is it the same in the background?
- Make a progress bar: print `self.n * 100 // 2_000_000` every 10 %.
- Have a logic analyzer? Toggle a spare SAO GPIO (see [[sao-pinout]]) high at the start of
  `run_foreground()` and low at the end. You'll *see* every slice, and printing won't
  slow your code down while you measure it.
- A progressive fractal: compute a Mandelbrot set one strip per slice, and update the screen as each strip finishes (see [[draw-pixels]] and [[eink-updates]]).
- A maze generator and solver: build the maze one step per slice, then watch the solver draw its path. Pick the algorithm with a button (depth-first, breadth-first, follow-the-wall) and see which one wanders the most (see [[draw-pixels]] and [[fsm]]).
