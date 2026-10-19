---
id: post-mortem
title: "Inspect a crash: keep the error, find the app, read its state"
label: Inspect a crash
topic: crashes
workshop: false
needs: [break-and-restore, firmware-diagram]
time: 30 min
touches: [apps/base_app.py, apps/app_menu.py, apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): crash behavior and BaseApp.all_apps are the 2025 firmware's (BaseApp.run has no try/except) -->

**Goal:** Find out what the badge does when an app hits an error mid-run, keep hold of
the error, then stop the world and look inside the app: what were its variables at
that moment?

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

3. **Keep the error.** The traceback scrolls away, and the error itself is gone once
   it's printed. Ask asyncio to hand it to you instead. At the top of your app's file:

   ```python
   import asyncio, sys

   last_crash = None

   def on_crash(loop, context):
       global last_crash
       last_crash = context                 # keep it for later
       print(context["message"])            # ...and still print it, as before
       sys.print_exception(context["exception"])
   ```

   And in your app's `__init__`:

   ```python
           asyncio.get_event_loop().set_exception_handler(on_crash)
   ```

   Save, **Ctrl+D**, and let it crash on tick 3 again.

   <!-- TODO(verify): that main.py doesn't replace the exception handler after the apps are created -->

4. **Stop the world and look at the error.** Press **Ctrl+C**. Nothing is cleaned up:
   every app is still in RAM, and so is your module, with `last_crash` in it:

   ```python
   import {{ facts.firmware.user_app | remove: ".py" | replace: "/", "." }} as m
   m.last_crash["exception"]        # the error itself
   m.last_crash["future"]           # the task it killed
   ```

   Any task that crashes is caught by your handler, not just yours: it's one handler
   for the whole badge. Handy, as long as you know that's what it is.

5. **Find your app.** The error tells you *what* went wrong, but not *which app object*
   it happened in. The badge keeps a list of its apps:

   ```python
   from apps.base_app import BaseApp
   [a.name for a in BaseApp.all_apps]
   me = [a for a in BaseApp.all_apps if a.name == "{{ facts.firmware.user_app_name }}"][0]
   ```

   <!-- TODO(verify): if this year's firmware doesn't keep a list of apps, add `global me; me = self` to the app's __init__ and use `m.me` instead -->

6. **Look inside.**

   ```python
   me.__dict__                              # every variable, and its value
   me.ticks                                 # was it really 3?
   me.task                                  # the dead task
   me.active_foreground, me.active_background
   ```

   Pick one value and explain it. Is it what you expected at the moment of the crash?

7. **More places to look:**

   ```python
   import sys, micropython
   sorted(sys.modules)        # every module that's loaded
   micropython.mem_info()     # how much RAM is in use
   ```

8. Take the error lines out of your app (keep the handler if you like it), save, and
   **Ctrl+D**.

**✅ Done when** you can say what happens to the menu and the other apps when your app
crashes, and you've read one of its variables after the crash and explained its value.

## What just happened

An error (**exception**) travels up the chain of calls until something catches it. In
your app, that chain is short: your method ← `BaseApp.run()` ← the asyncio scheduler.
`BaseApp.run()` doesn't catch anything, so the exception ends your app's **task**.
asyncio prints *"Task exception wasn't retrieved"* with the traceback, and keeps
running everyone else. `set_exception_handler` replaces that printing with your own
function, which can keep the error where you can find it later.

That's why the badge *looks* frozen after a foreground crash. Your app is still
marked as the foreground app, so the menu waits for it to finish, and it never will.

**Ctrl+C** raises a `KeyboardInterrupt` wherever the badge happens to be. The main loop
dies, but nothing is cleaned up: every object stays in RAM until the next reset (as in
[[explore-badge]]). That's what makes a post-mortem possible. You can't resume
afterwards, though; look all you like, then **Ctrl+D** to start over.

**What you can't see: local variables.** On a laptop, Python's debugger can show you
every variable in the function that crashed. MicroPython keeps no record of them: once
the error leaves your method, its locals are gone for good. What survives is *objects*:
your app (`self` and everything in it), module variables, the error. That's the best
reason for the rule in [[fsm]]: **keep state in `self`**. If the value that caused the
crash lives in `self`, you can read it afterwards. If it was a local, you can only
guess.

To survive an error instead of just studying it, see [[log-unplugged]].

<!-- TODO(diagram): call chain: asyncio scheduler → BaseApp.run → run_background → your error; the exception's path back up, to the exception handler and last_crash -->

## Stuck?

| Symptom | Fix |
|---|---|
| No traceback at all | Scroll up. It printed once, when it happened. |
| `m.last_crash` is `None` | The handler wasn't set. Did `__init__` run `set_exception_handler`? Did the crash happen *after* the last reset? |
| `IndexError` finding your app | Print `[a.name for a in BaseApp.all_apps]` and use the exact name. |
| The badge crashes at every boot now | Your error is in `__init__` or at the top of the file. Read the traceback (see [[break-and-restore]]). |
| `__dict__` is huge | Look at one value at a time: `me.some_name`. |

## Have fun!

- Make `on_crash` print *which* app crashed. Hint: compare `context["future"]` with each
  app's `task`.
- Which errors can you cause in one line? Which ones kill the task?
- Use `dir(me)` to find its *methods* too. Can you call one from `>>>`? (See [[drive-app]].)
