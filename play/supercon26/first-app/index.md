---
id: first-app
title: Add your own app from the template; watch it come and go
label: Your first app
topic: write-app
workshop: false
needs: [firmware-diagram]
time: 25 min
touches:
  - apps/template.py#TemplateApp      # on the switcher's deny list, so copy it to a new file
  - apps/base_app.py#BaseApp          # name, sleep_ms, launched; arun() calls run()
  - lib/app_switcher.py#AppSwitcher   # finds every BaseApp subclass in /apps at start-up
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Put your own app on the badge's menu, and see exactly when the badge runs it.

## You need

- Thonny, connected to the badge (see [[repl]])

## Steps

1. **Look at the template.** Open `{{ facts.firmware.template_app }}` on the badge. Read the
   comments; they say when `run()` is called and what `self.launched` means. Don't edit
   it: the badge skips any file called `template.py`, so it never shows up in the menu.

2. **Make `{{ facts.firmware.user_app }}`.** In Thonny, **File → New**, paste this, then
   **File → Save as… → MicroPython device**, open the `apps` folder, and name it
   `my_app.py`. It's the template, trimmed, with a `print` in each part so you can watch
   it work:

   ```python
   """My first app."""

   from apps.base_app import BaseApp
   from lib.button import UserA


   class MyApp(BaseApp):
       def __init__(self):
           super().__init__("{{ facts.firmware.user_app_name }}")
           self.sleep_ms = 100   # run() about 10 times a second
           self.calls = 0
           print(f"[{self.name}] created")

       def run(self):
           if self.launched:
               print(f"[{self.name}] launched")
               self.calls = 0
           self.calls += 1
           if self.calls % 50 == 0:
               print(f"[{self.name}] run() has been called {self.calls} times")
           if {{ facts.buttons.app_1 }}:
               print(f"[{self.name}] {{ facts.buttons.app_1_label }} pressed")
   ```

   The class can have any name, as long as it inherits from `BaseApp` (the one in
   `apps/base_app.py`). The badge finds it by itself.

3. **Restart.** Press **Ctrl+D** in the shell. Watch the start-up messages: you should
   see `[{{ facts.firmware.user_app_name }}] created`, then `Added app: {{ facts.firmware.user_app_name }}`. Then nothing
   from your app: it isn't open, so it doesn't run.

4. **Open your app** from the badge's menu: press **Menu +** or **Menu −** until the
   shell says `Selected app …: {{ facts.firmware.user_app_name }}`, then press **{{ facts.buttons.app_1_label }}**. The shell prints
   `Switching to {{ facts.firmware.user_app_name }}`, then `[{{ facts.firmware.user_app_name }}] launched`. Every five seconds or so after
   that, it prints how many times `run()` has been called.

5. **Press {{ facts.buttons.app_1_label }}.** It prints `{{ facts.buttons.app_1_label }} pressed`.

6. **Go back to the menu** with **{{ facts.buttons.home_label }}**. The shell prints
   `Activated app switching`, and your app's messages stop. Open it again: `launched`
   again, and the count starts over.

7. **Change it.** Make `run()` twice as fast (`self.sleep_ms = 50`), and change one
   message. Save, **Ctrl+D**, and check that it changed. Is the count message twice as
   often now?

<!-- TODO(screenshot): shell output with created / Added app / Switching to / launched / count / pressed / Activated app switching, in order -->

**✅ Done when** your app is on the menu and you can predict the next line it will print
before you press anything.

## What just happened

At start-up, `lib/app_switcher.py` imports every file in `apps/` and makes one object
of every class that inherits from `BaseApp`. That's when your `__init__` ran, once.

After that, your app is in one of two places:

| Where | What the badge calls | How often |
|---|---|---|
| **The menu** (closed) | nothing | never |
| **Open** | `run()` | every `self.sleep_ms`, plus however long everything else takes |

On the first `run()` after you open the app, `self.launched` is `True`. That's where an
app draws its screen. When you press **{{ facts.buttons.home_label }}**, the switcher simply stops calling
`run()`. Your app isn't told.

Two rules follow from this:

1. **Never loop or wait inside `run()`.** Do one small thing and return. The badge calls
   you again soon. Keep anything you need for next time in `self.`.
2. **Read the buttons every call.** `{{ facts.buttons.app_1 }}` is `True` once per press,
   but only if you ask *before the button is let go*. A tap shorter than `sleep_ms`
   can slip by unseen.

The full list of rules is in [[firmware-diagram]].

### Who gets to use the rest of the hardware?

Only one app is open at a time, so apps rarely collide. But the firmware itself uses
the LEDs: the menu draws on them, and opening an app turns them all off. If your app
starts a task of its own that keeps running from the menu, see [[share-hardware]].

## Stuck?

| Symptom | Fix |
|---|---|
| App isn't on the menu | Is the file *on the badge*, in `apps/`, ending in `.py`, and not starting with `_`? Does the class say `(BaseApp)`? |
| `Failed to load app module` at start-up | Your `__init__` raised an error; the traceback is printed just below. It must take no arguments besides `self`. |
| `SyntaxError` or `ImportError` at start-up, and no menu | A mistake that stops the file importing stops the whole badge. Read the traceback. See [[break-and-restore]]. |
| No `created` line | Scroll up; it's early in the start-up messages. Or you saved to your laptop, not the badge. |
| A quick tap of **{{ facts.buttons.app_1_label }}** prints nothing | The press ended before `run()` looked. Press a little longer, or make `sleep_ms` smaller. |
| Badge froze after your change | You probably have a loop or a `time.sleep()` in `run()`. See [[hog-the-cpu]]. |

## Prefer the command line?

```bash
mpremote cp my_app.py :{{ facts.firmware.user_app }}
mpremote reset
mpremote          # watch the output
```

## Have fun!

- Count button presses in `self.presses` and print the total with the call count.
- Print `time.ticks_ms()` in each call. Is it exactly `sleep_ms` apart? Why not?
- Make a second app in another file. Open one, then the other. Does the first one
  keep counting while the second is open?
