---
id: app-crash
title: Crash your app while it runs; see what survives
label: Crash your app
tier: developmental
difficulty: 7
group: debugging
icon: explosion
needs: [first-app, break-and-restore]
time: 20 min
touches: [main.py, apps/base_app.py, apps/app_menu.py, apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): crash behavior described here is the 2025 firmware's (BaseApp.run has no try/except) -->

**Goal:** Find out what the badge does when your app hits an error mid-run, make your
app survive errors, and keep a record of crashes that happen while no laptop is
plugged in.

## You need

- Your app from [[first-app]]
- A [[backup]]

## Steps

1. **Crash in the foreground.** In `run_foreground()`, add an error on **{{ facts.buttons.app_2_label }}**:

   ```python
           if {{ facts.buttons.app_2 }}:
               x = 1 / 0
   ```

   Save, **Ctrl+D**, open your app, and press **{{ facts.buttons.app_2_label }}**. Then try every button. Watch
   the shell:

   ```
   Task exception wasn't retrieved
   future: <Task> coro= <generator object 'run' at ...>
   Traceback (most recent call last):
     File "apps/base_app.py", line 45, in run
     File "apps/userA.py", line 31, in run_foreground
   ZeroDivisionError: divide by zero
   ```

   The screen stays on your app and the buttons do nothing. *But* the heartbeat still
   prints every 60 seconds. The badge isn't frozen: your app is gone and the menu
   doesn't know.

2. **Crash in the background.** Move the error to `run_background()`, on the third tick:

   ```python
           if self.ticks == 3:
               raise ValueError("bad sensor read")
   ```

   Save, **Ctrl+D**, and stay on the menu. After the third tick, the traceback prints
   and the ticks stop. The rest of the badge is fine. Now open your app from the menu.
   What happens? <!-- TODO(verify): in 2025, nothing happened: its task is gone, so nothing calls run_foreground() -->

3. **Survive it.** Wrap the risky part in `try`/`except`, print the error, and carry on:

   ```python
   import sys   # at the top of the file

       def run_background(self):
           self.ticks += 1
           try:
               if self.ticks == 3:
                   raise ValueError("bad sensor read")
               print(f"[{self.name}] tick {self.ticks}")
           except Exception as e:
               print(f"[{self.name}] error on tick {self.ticks}, carrying on:")
               sys.print_exception(e)
   ```

   Now tick 3 prints a traceback, and tick 4 happens anyway.

4. **Keep a crash log.** On demo night there's no laptop to see the shell. Write the
   traceback to a file instead (inside the `except`):

   ```python
               with open("crash.log", "a") as f:
                   f.write(f"tick {self.ticks}, t={time.ticks_ms()}\n")   # import time at the top
                   sys.print_exception(e, f)
   ```

   Run it unplugged for a minute, then plug in and read the log at `>>>`:

   ```python
   print(open("crash.log").read())
   ```

5. **Look around after a crash.** Undo step 3 so the background crash kills the task
   again. After the traceback, press **Ctrl+C** and inspect your app (like
   [[post-mortem]], without needing `global me`):

   ```python
   from apps.base_app import BaseApp
   me = [a for a in BaseApp.all_apps if a.name == "{{ facts.firmware.user_app_name }}"][0]
   me.ticks
   me.task          # the dead task
   me.active_foreground, me.active_background
   ```

6. Put your app back the way you want it, and delete `crash.log` when you're done
   (`import os; os.remove("crash.log")`).

**✅ Done when** you can say what happens to the menu and the other apps when your app
crashes, and your app survives an error and logs it.

## What just happened

An error (**exception**) travels up the chain of calls until something catches it. In
your app, that chain is short: your method ← `BaseApp.run()` ← the asyncio scheduler.
`BaseApp.run()` doesn't catch anything, so the exception ends your app's **task**.
asyncio prints *"Task exception wasn't retrieved"* with the traceback, and keeps
running everyone else.

That's why the badge *looks* frozen after a foreground crash. Your app is still
marked as the foreground app, so the menu waits for it to finish, and it never will.
The heartbeat proves the rest of the badge is alive.

`try`/`except` puts a catcher in your own code, so the exception stops there and your
task lives on. Catch around the risky part (a sensor read, a web request), not around
everything, or real bugs get hidden.

**What about a real debugger?** Thonny's step-by-step debugger only works with Python
on your laptop. Not on the badge, and stock MicroPython can't step through code at
all. On the badge, your toolkit is: tracebacks, `print`, Ctrl+C to stop the world
(see [[hog-the-cpu]]), and the REPL to look around afterwards. That's what most
embedded developers use too.

<!-- TODO(diagram): call chain: asyncio scheduler → BaseApp.run → run_background → your error; the exception's path back up, with "caught here" at try/except vs. "task dies" without it -->

## Stuck?

| Symptom | Fix |
|---|---|
| No traceback at all | Scroll up. It printed once, when it happened. |
| The badge crashes at every boot now | Your error is in `__init__` or at the top of the file. See [[recover]]. |
| `crash.log` is huge | Your error happens every tick. Fix the bug, or only log the first few (`if self.errors < 5:`). |
| `sys.print_exception` isn't found | `import sys` at the top of the file. |

## Have fun!

- **A poor-man's breakpoint.** Paste this into your app, then call `bp(globals())`
  where you want to stop. The whole badge pauses at a `dbg>` prompt where you can
  type Python. Press Enter on an empty line to carry on.

  ```python
  def bp(g):
      while (s := input("dbg> ")):
          try:
              exec(s, g)
          except Exception as e:
              print(repr(e))
  ```

  It only sees module-level variables, so do `global me; me = self` first (see
  [[post-mortem]]).

- Show errors on screen instead of in a file: an "Oops: ZeroDivisionError" label.
- Which errors can you cause in one line? Which ones kill the task, and which does
  MicroPython catch for you?
