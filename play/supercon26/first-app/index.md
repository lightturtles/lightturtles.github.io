---
id: first-app
title: Add your own app from the template; watch it come and go
label: Your first app
tier: core
difficulty: 6
group: apps
icon: puzzle-piece
needs: [asyncio-basics, name-badge]
time: 25 min
touches: [main.py, apps/base_app.py, apps/template_app.py, apps/app_menu.py, apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): app API below is the 2025 firmware's (apps/base_app.py, apps/template_app.py) -->

**Goal:** Put your own app on the badge's menu, and see exactly when the badge runs
each part of it.

## You need

- A [[backup]] (you're about to replace `{{ facts.firmware.user_app }}`)
- Thonny, connected to the badge (see [[repl]])

## Steps

1. **Look at the template.** Open `{{ facts.firmware.template_app }}` on the badge. Read the
   comments; they say when each method is called. Don't edit it.

2. **Replace `{{ facts.firmware.user_app }}`** with this. It's the template, with a
   `print` in every method so you can watch it work:

   ```python
   """My first app."""

   from apps.base_app import BaseApp


   class App(BaseApp):

       def __init__(self, name, badge):
           super().__init__(name, badge)
           self.background_sleep_ms = 5000   # run_background() every 5 s
           self.ticks = 0
           print(f"[{self.name}] created")

       def switch_to_foreground(self):
           super().switch_to_foreground()
           print(f"[{self.name}] -> FOREGROUND")

       def switch_to_background(self):
           super().switch_to_background()
           print(f"[{self.name}] -> background")

       def run_foreground(self):
           if {{ facts.buttons.app_1 }}:
               print(f"[{self.name}] button {{ facts.buttons.app_1_label }} pressed")
           if {{ facts.buttons.home }}:   # the "go home" button
               self.badge.display.clear()
               self.switch_to_background()   # the menu notices and comes back

       def run_background(self):
           self.ticks += 1
           print(f"[{self.name}] background tick {self.ticks}")
   ```

   Keep the class name `App`: that's what `main.py` looks for.

3. **Save and restart.** Save the file to the badge, then press **Ctrl+D** in the
   shell. Watch the start-up messages: you should see `[{{ facts.firmware.user_app_name }}] created`, then a
   `background tick` every 5 seconds.

4. **Open your app** from the badge's menu (**{{ facts.firmware.user_app_menu }}**). The shell prints `-> FOREGROUND`, and the ticks stop.

5. **Press **{{ facts.buttons.app_1_label }}**.** It prints `button {{ facts.buttons.app_1_label }} pressed`.

6. **Go home** with **{{ facts.buttons.home_label }}**. It prints `-> background`, the menu comes
   back, and the ticks start again.

7. **Change it.** Make the tick every 2 seconds, and change one message. Save,
   **Ctrl+D**, and check that it changed.

<!-- TODO(screenshot): shell output with created / ticks / FOREGROUND / button / background in order -->

**✅ Done when** your app is on the menu and you can predict the next line it will print
before you press anything.

## What just happened

`main.py` imports `{{ facts.firmware.user_app }}`, makes an `App`, and calls its
`start()`. That gives your app its own asyncio task, the `run()` loop in
`apps/base_app.py` (see [[asyncio-basics]]). Your app is now always in exactly one of
two states:

| State | What the badge calls | How often |
|---|---|---|
| **Background** | `run_background()` | every `background_sleep_ms` |
| **Foreground** | `run_foreground()` | every `foreground_sleep_ms` |

`switch_to_foreground()` and `switch_to_background()` run once, on the way in and the
way out. The menu calls the first one; you call the second one when the user wants
to leave.

Two rules follow from this:

1. **Never loop or wait inside these methods.** Do one small thing and return. The
   badge calls you again soon. Keep anything you need for next time in `self.`.
2. **Only the foreground app draws on the screen.** Your app gets the screen in
   `switch_to_foreground()` and gives it up when it goes to the background.

### Who gets to use the rest of the hardware?

Everything except the screen is **shared on the honor system**. Any app, in the
foreground or background, can light the LEDs, use the SAO pins or the I2C bus, or turn
on WiFi. Nothing stops two apps from doing it at once. If you plan to use one of these
from the background, see [[share-hardware]].

<!-- TODO(diagram): app state machine: created → background ⇄ foreground, with which method runs in each state and on each arrow -->

## Stuck?

| Symptom | Fix |
|---|---|
| App isn't on the menu | Did you keep the class name `App`? Is the file named exactly `{{ facts.firmware.user_app }}`? |
| `SyntaxError` or `ImportError` at boot | Read the traceback. See [[break-and-restore]]. |
| No `created` line | Scroll up; it's early in the start-up messages. Or you saved to your laptop, not the badge. |
| Badge froze after your change | You probably have a loop or a `time.sleep()` in one of the methods. See [[hog-the-cpu]]. |
| **{{ facts.buttons.home_label }}** doesn't go home | Is your `if` for it inside `run_foreground()`? Check the indentation. |

## Prefer the command line?

```bash
mpremote cp myapp.py :{{ facts.firmware.user_app }}
mpremote reset
mpremote          # watch the output
```

## Have fun!

- Count button presses in `self.presses` and print the total each tick.
- Print `time.ticks_ms()` in each tick. Is it exactly `background_sleep_ms` apart? Why not?
- Make a second app in another slot ({{ facts.firmware.user_apps }}). Do their ticks interleave?
