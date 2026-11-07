---
id: post-mortem
title: "Inspect a crash: keep the error, find the app, read its state"
label: Inspect a crash
topic: crashes
workshop: false
needs: [break-and-restore, firmware-diagram]
time: 30 min
touches:
  - apps/base_app.py#BaseApp.arun   # catches, prints and forgets errors from run()
  - lib/app_switcher.py#AppSwitcher # switcher.apps, active_idx, selecting_mode
  - apps/nametag.py
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Make an app hit an error mid-run, keep hold of the error, then stop the world
and look inside the app: what were its variables at that moment?

## You need

- The name badge app from [[name-badge]] open in Thonny from the badge (or your own app
  from [[first-app]]; it works the same way)
- A [[backup]]

## Steps

1. **Crash it on a button.** At the very end of `NametagApp.run()`, add an `else:` lined
   up with `if self.launched:` (or, if you added the sensor `elif` in [[name-badge]], put
   these two lines at the top of it):

   ```python
           else:
               if {{ facts.buttons.app_2 }}:
                   x = 1 / 0
   ```

   Save, **Ctrl+D**, open **{{ facts.name_badge.app }}**, and press
   **{{ facts.buttons.app_2_label }}** a few times. Watch the shell:

   ```
   Nametag hit an exception divide by zero
   Traceback (most recent call last):
     File "apps/base_app.py", line 29, in arun
     File "apps/nametag.py", line 72, in run
   ZeroDivisionError: divide by zero
   ```

   One traceback per press. In between, the app carries on: the menu works, and the
   heartbeat still prints every 60 seconds. Every error from `run()` is caught by
   `arun()` in `apps/base_app.py`, printed, and then **forgotten**.

2. **Keep the error.** The traceback scrolls away, and nothing remembers it. Make the app
   keep its own last error. Wrap the body of `run()` like this (indent everything that was
   in `run()` one more level):

   ```python
       def run(self):
           try:
               if self.launched:
                   ...                         # everything that was here before
               else:
                   if {{ facts.buttons.app_2 }}:
                       x = 1 / 0
           except Exception as e:
               self.last_error = e             # keep it for later
               self.errors = getattr(self, "errors", 0) + 1
               raise                           # ...and still let arun() print it
   ```

   Save, **Ctrl+D**, open the app, and crash it twice.

3. **Stop the world.** Press **Ctrl+C**. Nothing is cleaned up: every app is still in
   RAM, and the app switcher still has its list of them:

   ```python
   from lib.app_switcher import switcher
   [a.name for a in switcher.apps]
   me = switcher.apps[switcher.active_idx]     # the app that was on screen
   me.name
   ```

4. **Look inside.**

   ```python
   me.__dict__                  # every variable, and its value
   me.last_error                # the error itself
   me.errors                    # how many times?
   me.launched                  # True or False? Why?
   switcher.selecting_mode      # was the menu showing?
   ```

   Pick one value and explain it. Is it what you expected at the moment of the crash?

5. **Errors that nobody catches.** `arun()` only protects `run()`. A task an app starts
   for itself (with `asyncio.create_task`, to do something in the background) has no one
   watching it. Try one at the REPL:

   ```python
   import asyncio
   async def oops():
       await asyncio.sleep(1)
       1 / 0
   async def main():
       asyncio.create_task(oops())    # start it, and don't wait for it
       await asyncio.sleep(2)
       print("main is still fine")
   asyncio.run(main())
   ```

   You get `Task exception wasn't retrieved` and a traceback, then `main is still fine`.
   The task is gone for good, and nothing else noticed. To keep those
   errors too, give asyncio a handler of your own:

   ```python
   last_crash = None
   def on_crash(loop, context):
       global last_crash
       last_crash = context                      # keep it
       print(context["message"])                 # ...and still print it
       sys.print_exception(context["exception"])

   asyncio.get_event_loop().set_exception_handler(on_crash)
   ```

   That goes at the top of your app's file (with `import asyncio, sys`). It's one
   handler for the whole badge, not just your app.

6. **More places to look:**

   ```python
   import sys, micropython
   sorted(sys.modules)        # every module that's loaded
   micropython.mem_info()     # how much RAM is in use
   ```

7. Take the error lines out of your app (keep the `try` if you like it), save, and
   **Ctrl+D**.

**✅ Done when** you can say what happens to the menu and the other apps when your app
hits an error, and you've read one of its variables after the crash and explained its value.

## What just happened

An error (**exception**) travels up the chain of calls until something catches it. In
an app, that chain is short: your `run()` ← `BaseApp.arun()` ← the app switcher ←
asyncio. `arun()` catches everything, prints it, and goes back to calling `run()` as if
nothing happened. That's why the badge never freezes on an app's mistake. It's also why
an app can be quietly broken: if the error is in a part of `run()` that only runs once,
it prints once and the app just never finishes what it started.

Your `try`/`except` sits one step closer to the error. It keeps the error in `self`, and
`raise` passes it on up, so `arun()` still prints it.

**Ctrl+C** raises a `KeyboardInterrupt` wherever the badge happens to be. That's not an
`Exception`, so `arun()` lets it through, and the whole program stops. But nothing is
cleaned up: every object stays in RAM until the next reset (as in [[explore-badge]]).
That's what makes a post-mortem possible. You can't resume afterwards, though; look all
you like, then **Ctrl+D** to start over.

**What you can't see: local variables.** On a laptop, Python's debugger can show you
every variable in the function that crashed. MicroPython keeps no record of them: once
the error leaves `run()`, its locals are gone for good. What survives is *objects*: your
app (`self` and everything in it), module variables, the error. That's the best reason
for the rule in [[fsm]]: **keep state in `self`**. If the value that caused the crash
lives in `self`, you can read it afterwards. If it was a local, you can only guess.

To survive an error instead of just studying it, see [[log-unplugged]].

<!-- TODO(diagram): call chain: asyncio → AppSwitcher.arun → BaseApp.arun (catches, prints) → your run() → the error; a second chain for a task you made yourself, ending at the exception handler -->

## Stuck?

| Symptom | Fix |
|---|---|
| No traceback at all | Scroll up. It printed once per crash, when it happened. |
| `me` is the wrong app | `active_idx` is the last app you *opened*. Find yours by name: `[a for a in switcher.apps if a.name == "{{ facts.name_badge.app }}"][0]`. |
| `AttributeError: ... 'last_error'` | It hasn't crashed since the last reset, or your `except` isn't reached. Check the indenting. |
| The badge stops at `>>>` at start-up | The `try` broke the indenting (`SyntaxError`). Read the traceback (see [[break-and-restore]]). |
| `__dict__` is huge | Look at one value at a time: `me.some_name`. |

## Have fun!

- Change `arun()`'s behaviour for just your app: give your class its own `arun()` that
  stops calling `run()` after 3 errors. (Copy `BaseApp.arun` as a start.)
- Which errors can you cause in one line? Does any of them get past `arun()`?
- Use `dir(me)` to find its *methods* too. Can you call one from `>>>`? (See [[drive-app]].)
