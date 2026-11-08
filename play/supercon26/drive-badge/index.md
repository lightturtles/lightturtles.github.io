---
id: drive-badge
title: "Drive the whole badge: build the task list yourself, run it a second at a time"
label: Drive the whole badge
topic: advanced
workshop: false
needs: [drive-app, asyncio-basics]
time: 40 min
touches:
  - main.py                               # import main sets everything up and starts nothing
  - main.py#main                          # the four create_task lines to copy
  - lib/app_switcher.py#AppSwitcher.arun  # what "pick an app" sets: active_idx, launched, selecting_mode
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** From a blank REPL, set up the tasks the badge would run (the switcher with
your app in it, and whatever else it needs), then let them run for a second, or for a
few turns, or until something happens, and stop to look around in between.

## You need

- [[drive-app]] done: you can make your app at a blank `>>>`
- [[asyncio-basics]]: tasks, `await`, and `asyncio.run`

## Steps

1. **Get a blank REPL** (see [[resets]]) and set the badge up, without starting it:

   ```python
   import asyncio
   import main
   ```

   `main.py` prints its start-up messages, makes every app (yours too), and gives you
   `>>>` back. Look at the `if __name__ == "__main__":` block at its bottom: it only runs
   `main()` when it's *the* program, not when something imports it. (Do this at a
   fresh blank REPL. If something already set up the screen, `main.py` resets the badge
   instead: see its first lines.)

2. **Save the helpers** as `{{ facts.firmware.lib_dir }}/drive.py`, then import them:

   ```python
   import asyncio

   async def _wait(ms):
       await asyncio.sleep_ms(ms)

   def run_for(ms):
       """Let every task run for ms milliseconds, then come back to >>>."""
       asyncio.run(_wait(ms))

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

   def open_app(name):
       """Do what the menu does when you pick an app."""
       from lib.app_switcher import switcher
       names = [app.name for app in switcher.apps]
       switcher.active_idx = switcher.selection_idx = names.index(name)
       switcher.apps[switcher.active_idx].launched = True
       switcher.selecting_mode = False
       return switcher.apps[switcher.active_idx]

   def step(app, n=1):
       """Call the app's run() yourself, n times, with no scheduler at all."""
       for _ in range(n):
           app.run()
           app.launched = False
   ```

   ```python
   from drive import run_for, rounds, until, open_app, step
   ```

3. **Start the tasks.** Open `main.py` and find the four `aio.create_task(...)` lines
   in `main()`. Copy the ones you want. The buttons, the screen and the switcher:

   ```python
   from lib.app_switcher import switcher
   from lib.button import scan
   from lib.epd import display
   asyncio.create_task(scan())
   asyncio.create_task(display.run())
   asyncio.create_task(switcher.arun())
   ```

   Nothing runs yet. The tasks are in asyncio's queue, waiting for someone to start
   the scheduler.

4. **Run everything for one second.**

   ```python
   run_for(1000)
   switcher.selecting_mode
   ```

   For one second, the badge ran exactly as normal: the menu, on the LEDs. Then
   everything stopped and you got `>>>` back. Look around; nothing is changing while
   you do. Run it again, and it carries on from where it stopped. Press **Menu +**
   during a `run_for(3000)`, and check `switcher.selection_idx` afterwards.

5. **Open your app** without the buttons, then run again:

   ```python
   a = open_app("{{ facts.firmware.user_app_name }}")
   run_for(1000)
   a.calls
   ```

   Your app printed `launched`, and `run()` has been called about ten times.

6. **Run until something happens.**

   ```python
   until(lambda: a.calls >= 50)
   a.calls
   until(lambda: a.calls >= 1000, timeout_ms=2000)     # TimeoutError: it didn't happen in time
   ```

   The timeout matters: without it, a condition that never comes true hangs the REPL
   until you press **Ctrl+C**.

7. **Ctrl+D** to get the normal badge back.

**✅ Done when** you've run the badge for one second at a time from a blank REPL,
opened your app without touching a button, checked a variable between runs, and
stopped with `until()`.

## What just happened

asyncio keeps one **queue** of tasks. `create_task` only puts a task in the queue. `asyncio.run(x)` starts the scheduler, which runs *every* task in the
queue, taking turns, until `x` finishes. Then it stops and returns, and the other tasks
stay in the queue, paused wherever they last `await`ed. The next `asyncio.run` picks
them up again.

That makes `asyncio.run` a pause button you control:

| Helper | Runs the scheduler… | Good for |
|---|---|---|
| `run_for(ms)` | for `ms` milliseconds | "run normally for a moment, then let me look" |
| `rounds(n)` | for `n` turns of the tasks that are ready | stepping one turn at a time |
| `until(cond)` | until something is true (or the timeout) | "run until the third message arrives" |
| `step(app, n)` | doesn't: calls the app's `run()` directly | testing the app's logic with no timing at all |

`rounds` only moves tasks that are *ready*. A task in `await asyncio.sleep_ms(1000)`
isn't ready until its second is up, so `rounds(1)` won't wake it. Use `run_for` when
time has to pass.

Building the task list yourself is the opposite of [[post-mortem]]. There, the badge
ran everything and you looked at the wreckage. Here, nothing runs unless you put it in
the queue, so when something goes wrong you know exactly which tasks were involved.

(`run_for` needs the little `_wait()` wrapper because MicroPython's `asyncio.sleep_ms()`
doesn't return a coroutine, and `asyncio.run()` only takes one.)

<!-- TODO(diagram): the task queue: button scan, display, switcher (running your app); asyncio.run(_wait(1000)) runs them all, returns, they wait for the next run -->

## Stuck?

| Symptom | Fix |
|---|---|
| `run_for` returns and nothing changed | The switcher's task isn't in the queue (step 3), or your app isn't open (step 5). |
| `TypeError: coroutine expected` | You passed `asyncio.sleep_ms(...)` straight to `asyncio.run()`. Use the helpers. |
| `ValueError` from `open_app` | No app has that name. `[a.name for a in switcher.apps]`. |
| Menu messages or heartbeats show up | You're not in a blank REPL: `main.py` ran. Start again from [[resets]]. |
| `TimeoutError` from `until` | The condition didn't come true in time. Check it by hand, or give it longer. |
| `run_for` never returns | A task is hogging the processor (see [[hog-the-cpu]]). **Ctrl+C**. |
| Everything is stuck after a Ctrl+C | The task that was running when you pressed it is dead. Start again from a blank REPL. |
| `AttributeError: wait_for_ms` | Use `asyncio.wait_for(..., timeout_ms / 1000)` instead. |

## Have fun!

- Add `leds.update()` (the fourth task in `main()`) and give it an animation (see [[animate-leds]]).
- Time how long one `rounds(1)` takes with your app open. That's one lap of the
  scheduler.
- Write a `trace(ms)` helper that runs for `ms` and prints `a.__dict__` whenever it changes
  (see the `watch` helper in [[better-prints]]).
