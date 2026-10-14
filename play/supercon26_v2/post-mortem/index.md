---
id: post-mortem
title: "Post-mortem: crash or stop a running app, see what survives, inspect its state"
label: Post-mortem
topic: debugging
workshop: false
needs: [break-and-restore]
time: 30 min
touches: [main.py, apps/base_app.py, apps/app_menu.py, apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): crash behavior and BaseApp.all_apps are the 2025 firmware's (BaseApp.run has no try/except) -->

**Goal:** Find out what the badge does when an app hits an error mid-run, then stop the
world and look inside the app: what were its variables at that moment?

## You need

- Your app from [[first-app]] (or the name badge app from [[name-badge]])
- A [[backup]]

## Steps

1. **Crash in the foreground.** In `run_foreground()`, add an error on
   **{{ facts.buttons.app_2_label }}**:

   ```python
           if {{ facts.buttons.app_2 }}:
               x = 1 / 0
   ```

   Save, **Ctrl+D**, open your app, and press **{{ facts.buttons.app_2_label }}**. Then try
   every button, and watch the shell:

   ```
   Task exception wasn't retrieved
   future: <Task> coro= <generator object 'run' at ...>
   Traceback (most recent call last):
     File "apps/base_app.py", line 45, in run
     File "apps/userA.py", line 31, in run_foreground
   ZeroDivisionError: divide by zero
   ```

   The screen stays on your app and the buttons do nothing. *But* the heartbeat still
   prints every 60 seconds. The badge isn't frozen: your app is gone, and the menu
   doesn't know.

2. **Crash in the background.** Move the error to `run_background()`, on the third tick:

   ```python
           if self.ticks == 3:
               raise ValueError("bad sensor read")
   ```

   Save, **Ctrl+D**, and stay on the menu. After the third tick, the traceback prints
   and the ticks stop. The rest of the badge is fine. Now open your app from the menu.
   What happens? <!-- TODO(verify): in 2025, nothing happened: its task is gone, so nothing calls run_foreground() -->

3. **Stop the world and find your app.** Press **Ctrl+C**. Nothing is cleaned up: every
   app is still in RAM. Find yours:

   ```python
   from apps.base_app import BaseApp
   [a.name for a in BaseApp.all_apps]
   me = [a for a in BaseApp.all_apps if a.name == "{{ facts.firmware.user_app_name }}"][0]
   ```

   <!-- TODO(verify): if this year's firmware doesn't keep a list of apps, add `global me; me = self` to the app's __init__ and use `import apps.userA as m; m.me` instead -->

4. **Look inside.**

   ```python
   me.__dict__                              # every variable, and its value
   me.ticks                                 # was it really 3?
   me.task                                  # the dead task
   me.active_foreground, me.active_background
   ```

   Pick one value and explain it. Is it what you expected at the moment of the crash?

5. **More places to look:**

   ```python
   import sys, micropython
   sorted(sys.modules)        # every module that's loaded
   micropython.mem_info()     # how much RAM is in use
   ```

6. **Survive it next time.** Wrap the risky part in `try`/`except`, print the error,
   and carry on:

   ```python
   import sys   # at the top of the file

       def run_background(self):
           self.ticks += 1
           try:
               if self.ticks == 3:
                   raise ValueError("bad sensor read")
           except Exception as e:
               print(f"[{self.name}] error on tick {self.ticks}, carrying on:")
               sys.print_exception(e)
   ```

   Tick 3 prints a traceback, and tick 4 happens anyway.

7. **Keep a crash log** for when no laptop is plugged in. Inside the `except`:

   ```python
               with open("crash.log", "a") as f:
                   f.write(f"tick {self.ticks}, t={time.ticks_ms()}\n")   # import time at the top
                   sys.print_exception(e, f)
   ```

   Run it unplugged for a minute, then plug in and `print(open("crash.log").read())`.

8. Put your app back the way you want it, and delete `crash.log`
   (`import os; os.remove("crash.log")`).

**✅ Done when** you can say what happens to the menu and the other apps when your app
crashes, and you've read one of its variables after the crash and explained its value.

## What just happened

An error (**exception**) travels up the chain of calls until something catches it. In
your app, that chain is short: your method ← `BaseApp.run()` ← the asyncio scheduler.
`BaseApp.run()` doesn't catch anything, so the exception ends your app's **task**.
asyncio prints *"Task exception wasn't retrieved"* with the traceback, and keeps
running everyone else.

That's why the badge *looks* frozen after a foreground crash. Your app is still
marked as the foreground app, so the menu waits for it to finish, and it never will.

**Ctrl+C** raises a `KeyboardInterrupt` wherever the badge happens to be. The main loop
dies, but nothing is cleaned up: every object stays in RAM until the next reset.
That's what makes a post-mortem possible. You can't resume afterwards, though; look all
you like, then **Ctrl+D** to start over.

`try`/`except` puts a catcher in your own code, so the exception stops there and your
task lives on. Catch around the risky part (a sensor read, a web request), not around
everything, or real bugs get hidden.

Want to look inside *before* it crashes, and then carry on? That's [[bp]].

<!-- TODO(diagram): call chain: asyncio scheduler → BaseApp.run → run_background → your error; the exception's path back up, with "caught here" at try/except vs. "task dies" without it -->

## Stuck?

| Symptom | Fix |
|---|---|
| No traceback at all | Scroll up. It printed once, when it happened. |
| `IndexError` finding your app | Print `[a.name for a in BaseApp.all_apps]` and use the exact name. |
| The badge crashes at every boot now | Your error is in `__init__` or at the top of the file. See [[recover]]. |
| `crash.log` is huge | Your error happens every tick. Fix the bug, or only log the first few. |
| `__dict__` is huge | Look at one value at a time: `me.some_name`. |

## Have fun!

- Show errors on screen instead of in a file: an "Oops: ZeroDivisionError" label.
- Which errors can you cause in one line? Which ones kill the task?
- Use `dir(me)` to find its *methods* too. Can you call one from `>>>`? (See [[drive-app]].)
