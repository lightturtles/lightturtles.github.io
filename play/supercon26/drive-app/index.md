---
id: drive-app
title: Drive your app by hand from the REPL
label: Drive your app by hand
topic: advanced
workshop: false
needs: [resets]
time: 30 min
touches:
  - apps/base_app.py#BaseApp     # run() and launched: all the switcher ever uses
  - lib/epd.py#EPaperDisplay.run # the display task; nothing reaches the e-ink without it
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Start from a badge that's running nothing, make your app at `>>>`, call its
methods one at a time, and look inside it between calls. No menu, no buttons, no
waiting. Then change the code and test again without a reset.

## You need

- Your app from [[first-app]]
- A blank REPL: `boot.py` run, `main.py` not (see [[resets]])

## Steps

1. **Get a blank REPL.** **Ctrl+A**, **Ctrl+D**, **Ctrl+B** (or `mpremote soft-reset + repl`).
   Nothing is running: no menu, no other apps, nothing to get in your way.

2. **Make your app yourself.** Import your app's file, then make one:

   ```python
   import apps.my_app as m
   a = m.MyApp()
   ```

   It prints `[{{ facts.firmware.user_app_name }}] created`. This is the only copy of your app, and nothing
   calls it but you. (Your file's own imports, like `lib.button`, set up the hardware
   it needs.)

3. **Look inside:**

   ```python
   a.__dict__
   ```

   Every variable it set in `__init__`, and its value.

4. **Step it by hand.** Be the switcher: "open" the app, then call it a few times and
   check what changed:

   ```python
   a.launched = True
   a.run()
   a.launched = False
   for i in range(49): a.run()
   a.calls
   ```

   You're the scheduler now: one call at a time, as slowly as you like.

5. **Make it easy to drive.** Button checks are hard to fake. Move what each button
   *does* into its own method:

   ```python
       def run(self):
           # ...
           if {{ facts.buttons.app_1 }}:
               self.on_press()

       def on_press(self):
           self.presses = getattr(self, "presses", 0) + 1
           print(f"[{self.name}] pressed {self.presses} times")
   ```

   Save it to the badge, but don't reset.

6. **Load the new code without a reset.** Your old `a` was made from the old code, and
   importing again just hands you the module that's already loaded. Make Python forget
   it, then import it again:

   ```python
   import sys
   sys.modules.pop("apps.my_app", None)     # forget the old version
   import apps.my_app as m                  # read the file again
   a = m.MyApp()                            # and make a new app from the new code
   a.on_press(); a.on_press()
   a.presses
   ```

   The catch: objects made *before* the reload still run the old code. Always make a
   new `a` afterwards.

7. **Try the edges.** What happens on the 100th press? With a value of 0? Set a
   variable to something odd and call a method:

   ```python
   a.presses = 99
   a.on_press()
   ```

8. **The screen.** If your app draws (as in [[lvgl-hello]]), `a.launched = True` and
   `a.run()` draw into the framebuffers and ask for a refresh. But the display task
   isn't running, so nothing reaches the e-ink. Run it yourself, for one refresh:

   ```python
   import asyncio
   from lib.epd import display

   async def refresh():
       task = asyncio.create_task(display.run())   # the display task, for one refresh
       await asyncio.sleep_ms(200)
       while not display.is_done_updating():
           await asyncio.sleep_ms(100)
       task.cancel()

   asyncio.run(refresh())
   ```

   Change a label (`a.label.set_text("driven by hand")`, `a.show()`), and run
   `asyncio.run(refresh())` again.

9. **Ctrl+D** when you're done. The badge starts normally, with its own copy of your app.

**✅ Done when** you've made your app at a blank `>>>`, called its methods by hand,
checked a variable between calls, and tested a change without a reset.

## What just happened

Your app is just a class. At start-up the switcher makes one, and while the app is
open it sets `launched` and calls `run()` on a schedule (see [[firmware-diagram]]). Nothing stops you doing the same
by hand, and that's the quickest way to test one piece: no reboot, no menu, no pressing
buttons, and you can look at everything between steps.

Starting from a blank REPL means **only what you make exists**. Nothing else calls
your app, changes its variables, or prints over your output. (You *can* do this after
**Ctrl+C** instead, but then there are two copies of your app: yours and the badge's.)

`sys.modules` is the list of loaded modules. `import` checks it first, and only reads
the file if the name isn't there. Removing a name forces a fresh read. Python's
`importlib.reload()` does the same on a laptop; MicroPython doesn't have it, so you do
it by hand.

Splitting "which button" from "what it does" made your app **testable**: `on_press()`
can be called from a button, from the REPL, from a message from another badge (see
[[espnow-in-app]]), or from a test (see [[unit-tests]]). It's a habit worth keeping.

This is also how you narrow down a bug: drive the app to just before it goes wrong,
look at its state, then take one more step.

## Stuck?

| Symptom | Fix |
|---|---|
| The menu is running | `main.py` ran: you pressed Ctrl+D at a normal `>>>`. Start again with step 1. |
| `TypeError` making `MyApp` | Its `__init__` takes arguments the switcher wouldn't give it. It should take only `self`. |
| `AttributeError: 'module' object has no attribute 'MyApp'` | Your class has another name. `dir(m)` lists what's in the file. |
| Changes don't show | You're using the old `a`. Reload the module, then make a new `a`. Or the file wasn't saved to the badge. |
| `AttributeError` on a variable | It's set in the `if self.launched:` part of `run()`, not `__init__`. Set `a.launched = True` and call `a.run()` first. |
| Reloaded, but a helper module is still old | Pop that one from `sys.modules` too. For a module in a folder, use the full name: `"apps.my_app"`. |
| The screen doesn't change in step 8 | Did `refresh()` print `Updating display to new image`? If not, nothing asked for an update: call `a.show()` (or `display.update()`) first. |

## Have fun!

- Write a one-line `reload(name)` helper in `{{ facts.firmware.lib_dir }}/`. (Watch out:
  `__import__("apps.my_app")` returns the `apps` package, not `my_app`.)
- Write a tiny test: a function that makes an app, presses 3 times, and checks
  `a.presses == 3`. Run it after every change. (Then see [[unit-tests]].)
- Call `run()` 1000 times in a loop and time it (see [[on-time]]). That's your code
  alone: calling `run()` directly skips the `sleep_ms` nap that `arun()` adds.
