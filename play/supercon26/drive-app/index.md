---
id: drive-app
title: Drive your app by hand from the REPL
label: Drive your app by hand
topic: advanced
workshop: false
needs: [resets]
time: 30 min
touches: [apps/userA.py, apps/base_app.py]
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

2. **Make your app yourself.** Import what `main.py` would have, then make the app:

   ```python
   {{ facts.firmware.badge_import }}
   import {{ facts.firmware.user_app | remove: ".py" | replace: "/", "." }} as m
   a = m.App("test", badge_obj)
   ```

   This is the only copy of your app, and nothing calls it but you.

   <!-- TODO(verify): whether importing badge_obj in a blank REPL sets up the hardware by itself, or main.py does more (LVGL set-up, etc.) that has to be copied here -->

3. **Look inside:**

   ```python
   a.__dict__
   ```

   Every variable it set in `__init__`, and its value.

4. **Step it by hand.** Call each method yourself and check what changed:

   ```python
   a.run_background()
   a.ticks
   a.run_background()
   a.ticks
   ```

   You're the scheduler now: one call at a time, as slowly as you like.

5. **Make it easy to drive.** Button checks are hard to fake. Move what each button
   *does* into its own method:

   ```python
       def run_foreground(self):
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
   # forget the old version
   sys.modules.pop("{{ facts.firmware.user_app | remove: ".py" | replace: "/", "." }}", None)
   # read the file again, and make a new app from the new code
   import {{ facts.firmware.user_app | remove: ".py" | replace: "/", "." }} as m
   a = m.App("test", badge_obj)
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

8. **The screen.** `a.switch_to_foreground()` builds your screen, but nothing is
   running to draw it. Ask LVGL to draw now:

   ```python
   import lvgl
   a.switch_to_foreground()
   lvgl.refr_now(None)
   ```

   <!-- TODO(verify): refr_now draws to the e-ink without the LVGL task running, and LVGL is set up in a blank REPL -->

9. **Ctrl+D** when you're done. The badge starts normally, with its own copy of your app.

**✅ Done when** you've made your app at a blank `>>>`, called its methods by hand,
checked a variable between calls, and tested a change without a reset.

## What just happened

Your app is just a class. The badge's `main.py` makes one, and `BaseApp.run()` calls
its methods on a schedule (see [[firmware-diagram]]). Nothing stops you doing the same
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
| `TypeError` making `App` | Its `__init__` takes different arguments. Check `{{ facts.firmware.user_app }}` and `apps/base_app.py`. |
| Changes don't show | You're using the old `a`. Reload the module, then make a new `a`. Or the file wasn't saved to the badge. |
| `AttributeError` on a variable | It's set in `switch_to_foreground()`, not `__init__`. Call that first. |
| Reloaded, but a helper module is still old | Pop that one from `sys.modules` too. For a module in a folder, use the full name: `"apps.userA"`. |

## Have fun!

- Write a one-line `reload(name)` helper in `{{ facts.firmware.lib_dir }}/`. (Watch out:
  `__import__("apps.userA")` returns the `apps` package, not `userA`.)
- Write a tiny test: a function that makes an app, presses 3 times, and checks
  `a.presses == 3`. Run it after every change. (Then see [[unit-tests]].)
- Drive the background: call `run_background()` 1000 times in a loop and time it
  (see [[on-time]]).
