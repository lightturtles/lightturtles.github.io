---
id: drive-app
title: Drive your app by hand from the REPL
label: Drive your app by hand
topic: workflow
workshop: false
needs: [first-app, repl-setup]
time: 25 min
touches: [apps/userA.py, apps/base_app.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Make your own copy of your app at `>>>`, call its methods one at a time, and
look inside it between calls. No menu, no buttons, no waiting.

## You need

- Your app from [[first-app]]
- The reload trick from [[repl-setup]]

## Steps

1. **Make your app yourself.** Press **Ctrl+C**, then:

   ```python
   {{ facts.firmware.badge_import }}
   import {{ facts.firmware.user_app | remove: ".py" | replace: "/", "." }} as m
   a = m.App("test", badge_obj)
   ```

   You now have a second copy of your app, separate from the one the badge made.
   Nothing calls it but you.

2. **Look inside:**

   ```python
   a.__dict__
   ```

   Every variable it set in `__init__`, and its value.

3. **Step it by hand.** Call each method yourself and check what changed:

   ```python
   a.run_background()
   a.ticks
   a.run_background()
   a.ticks
   ```

   You're the scheduler now: one call at a time, as slowly as you like.

4. **Make it easy to drive.** Button checks are hard to fake. Move what each button
   *does* into its own method:

   ```python
       def run_foreground(self):
           if {{ facts.buttons.app_1 }}:
               self.on_press()

       def on_press(self):
           self.presses = getattr(self, "presses", 0) + 1
           print(f"[{self.name}] pressed {self.presses} times")
   ```

   Save, then reload and make a fresh app (see [[repl-setup]]):

   ```python
   import sys
   sys.modules.pop("{{ facts.firmware.user_app | remove: ".py" | replace: "/", "." }}", None)
   import {{ facts.firmware.user_app | remove: ".py" | replace: "/", "." }} as m
   a = m.App("test", badge_obj)
   a.on_press(); a.on_press()
   a.presses
   ```

5. **Try the edges.** What happens on the 100th press? With a value of 0? Set a
   variable to something odd and call a method:

   ```python
   a.presses = 99
   a.on_press()
   ```

6. **The screen.** `a.switch_to_foreground()` builds your screen, but LVGL's task
   stopped with **Ctrl+C**, so nothing appears. Ask it to draw now:

   ```python
   import lvgl
   a.switch_to_foreground()
   lvgl.refr_now(None)
   ```

   <!-- TODO(verify): refr_now draws to the e-ink without the LVGL task running -->

7. **Ctrl+D** when you're done. Your test copy disappears; the badge makes its own again.

**✅ Done when** you've made your app at `>>>`, called its methods by hand, and checked
a variable between calls.

## What just happened

Your app is just a class. The badge's `main.py` makes one, and `BaseApp.run()` calls
its methods on a schedule. Nothing stops you doing the same by hand, and that's the
quickest way to test one piece: no reboot, no menu, no pressing buttons, and you can
look at everything between steps.

Splitting "which button" from "what it does" made your app **testable**: `on_press()`
can be called from a button, from the REPL, or from a message from another badge
(see [[espnow-in-app]]). It's a habit worth keeping.

This is also how you narrow down a bug: drive the app to just before it goes wrong,
look at its state, then take one more step (see [[post-mortem]] and [[bp]]).

## Stuck?

| Symptom | Fix |
|---|---|
| `TypeError` making `App` | Its `__init__` takes different arguments. Check `{{ facts.firmware.user_app }}` and `apps/base_app.py`. |
| Changes don't show | You're using the old `a`. Reload the module, then make a new `a`. |
| `AttributeError` on a variable | It's set in `switch_to_foreground()`, not `__init__`. Call that first. |
| Two apps' LEDs fighting | The badge's copy is stopped after Ctrl+C, but its last LED write stays. Ignore it, or clear the LEDs. |

## Have fun!

- Write a tiny test: a function that makes an app, presses 3 times, and checks
  `a.presses == 3`. Run it after every change.
- Drive the background: call `run_background()` 1000 times in a loop and time it
  (see [[on-time]]).
