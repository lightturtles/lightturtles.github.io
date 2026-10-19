---
id: drive-badge
title: "Drive the whole badge: build the task list yourself, run it a second at a time"
label: Drive the whole badge
topic: advanced
workshop: false
needs: [drive-app, asyncio-basics]
time: 40 min
touches: [main.py, apps/base_app.py, apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): names below (Badge task, LVGL task, BaseApp.start) are from the 2025 firmware -->

**Goal:** From a blank REPL, set up the tasks the badge would run (your app, and
whatever else it needs), then let them run for a second, or for a few turns, or until
something happens, and stop to look around in between.

## You need

- [[drive-app]] done: you can make your app at a blank `>>>`
- [[asyncio-basics]]: tasks, `await`, and `asyncio.run`

## Steps

1. **Get a blank REPL** (see [[resets]]) and make your app, as in [[drive-app]]:

   ```python
   import asyncio
   {{ facts.firmware.badge_import }}
   import {{ facts.firmware.user_app | remove: ".py" | replace: "/", "." }} as m
   a = m.App("test", badge_obj)
   ```

2. **Give it its task.** `start()` creates the app's task, the `run()` loop from
   [[firmware-diagram]]:

   ```python
   a.start()
   ```

   Nothing runs yet. The task is in asyncio's queue, waiting for someone to start the
   scheduler.

3. **Run everything for one second.** The scheduler runs until the task you hand
   `asyncio.run` finishes. Hand it one that just waits:

   ```python
   asyncio.run(asyncio.sleep_ms(1000))
   a.ticks
   ```

   For one second, your app ran exactly as it would on the badge: `run_background()`
   every `background_sleep_ms`. Then everything stopped and you got `>>>` back. Look
   around; nothing is changing while you do. Run the same line again, and it carries
   on from where it stopped.

4. **Bring it to the front.** Do what the menu would do, then run again:

   ```python
   a.switch_to_foreground()
   asyncio.run(asyncio.sleep_ms(1000))
   a.__dict__
   ```

   Now `run_foreground()` is being called. Press a button while it runs (or call
   `a.on_press()` from [[drive-app]] between runs).

5. **Add the helpers.** Save this as `{{ facts.firmware.lib_dir }}/drive.py`:

   ```python
   import asyncio

   def run_for(ms):
       """Let every task run for ms milliseconds, then come back to >>>."""
       asyncio.run(asyncio.sleep_ms(ms))

   async def _rounds(n):
       for _ in range(n):
           await asyncio.sleep(0)       # one pass through the tasks that are ready

   def rounds(n=1):
       """Give every ready task n turns."""
       asyncio.run(_rounds(n))

   async def _until(cond, period_ms):
       while not cond():
           await asyncio.sleep_ms(period_ms)

   def until(cond, timeout_ms=5000, period_ms=10):
       """Run until cond() is true. Gives up with TimeoutError after timeout_ms."""
       asyncio.run(asyncio.wait_for_ms(_until(cond, period_ms), timeout_ms))

   def step(app, n=1, fg=True):
       """Call the app's methods yourself, n times, with no scheduler at all."""
       for _ in range(n):
           if fg:
               app.run_foreground()
           app.run_background()
   ```

6. **Run until something happens.**

   ```python
   from drive import run_for, rounds, until, step
   until(lambda: a.ticks >= 5)
   a.ticks
   until(lambda: a.ticks >= 1000, timeout_ms=2000)     # TimeoutError: it didn't happen in time
   ```

   The timeout matters: without it, a condition that never comes true hangs the REPL
   until you press **Ctrl+C**.

7. **Add the rest of the badge.** Your app on its own can't draw on the screen or hear
   the buttons, if those are other tasks' jobs. Open `main.py` and find where it starts
   them. Copy just those lines (not the menu, not the forever loop):

   ```python
   # TODO(verify): the lines from this year's main.py that start the badge's own task
   # and LVGL's, e.g.
   # asyncio.create_task(badge_obj.run())
   # asyncio.create_task(lvgl_setup.lvgl_task_handler())
   ```

   `run_for(3000)` again. Now your screen is drawn, and the buttons reach your app.

8. **Ctrl+D** to get the normal badge back.

**✅ Done when** you've run your app for one second at a time from a blank REPL,
checked a variable between runs, and stopped it with `until()`.

## What just happened

asyncio keeps one **queue** of tasks. `create_task` (which `start()` calls) only puts a
task in the queue. `asyncio.run(x)` starts the scheduler, which runs *every* task in the
queue, taking turns, until `x` finishes. Then it stops and returns, and the other tasks
stay in the queue, paused wherever they last `await`ed. The next `asyncio.run` picks
them up again.

That makes `asyncio.run` a pause button you control:

| Helper | Runs the scheduler… | Good for |
|---|---|---|
| `run_for(ms)` | for `ms` milliseconds | "run normally for a moment, then let me look" |
| `rounds(n)` | for `n` turns of the tasks that are ready | stepping one turn at a time |
| `until(cond)` | until something is true (or the timeout) | "run until the third message arrives" |
| `step(app, n)` | doesn't: calls the app's methods directly | testing the app's logic with no timing at all |

`rounds` only moves tasks that are *ready*. A task in `await asyncio.sleep_ms(1000)`
isn't ready until its second is up, so `rounds(1)` won't wake it. Use `run_for` when
time has to pass.

Building the task list yourself is the opposite of [[post-mortem]]. There, the badge
ran everything and you looked at the wreckage. Here, nothing runs unless you put it in
the queue, so when something goes wrong you know exactly which tasks were involved.

<!-- TODO(diagram): the task queue: your app, Badge task, LVGL task; asyncio.run(sleep_ms(1000)) runs them all, returns, they wait for the next run -->

## Stuck?

| Symptom | Fix |
|---|---|
| `run_for` returns at once and nothing changed | The app's task isn't in the queue. Did you call `a.start()`? |
| Menu messages or heartbeats show up | You're not in a blank REPL: `main.py` ran. Start again from [[resets]]. |
| `TimeoutError` from `until` | The condition didn't come true in time. Check it by hand, or give it longer. |
| `run_for` never returns | A task is hogging the processor (see [[hog-the-cpu]]). **Ctrl+C**. |
| Everything is stuck after a Ctrl+C | The task that was running when you pressed it is dead. Start again from a blank REPL. |
| `AttributeError: wait_for_ms` | Use `asyncio.wait_for(..., timeout_ms / 1000)` instead. |

## Have fun!

- Run two of your own apps side by side and watch their ticks interleave.
- Time how long one `rounds(1)` takes with your app in the foreground. That's one lap
  of the scheduler.
- Write a `trace(ms)` helper that runs for `ms` and prints `a.__dict__` whenever it changes
  (see the `watch` helper in [[better-prints]]).
