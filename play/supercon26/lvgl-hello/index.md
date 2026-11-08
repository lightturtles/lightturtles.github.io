---
id: lvgl-hello
title: Put one LVGL label on the screen from your app
label: Hello, LVGL
topic: display
workshop: false
needs: [first-app]
time: 20 min
touches:
  - lib/epd.py#EPaperDisplay._lv_flush   # LVGL's pixels → the black/red framebuffers (a Python loop)
  - lib/epd.py#EPaperDisplay.update      # the e-ink refresh
  - apps/schedule.py#ScheduleApp._draw   # the firmware's own pattern: screen_load, refr_now, update
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Draw text on the e-ink screen when your app opens, and change it when you
press a button.

## You need

- Your app from [[first-app]] (you're about to replace it)

## Steps

1. **Replace `{{ facts.firmware.user_app }}`** with this:

   ```python
   """Hello, LVGL: one label on the e-ink."""

   import lvgl

   from apps.base_app import BaseApp
   from lib.button import UserA
   from lib.epd import display


   class MyApp(BaseApp):
       def __init__(self):
           super().__init__("{{ facts.firmware.user_app_name }}")
           self.screen = None
           self.presses = 0

       def build(self):
           self.screen = lvgl.obj()                    # a new, empty screen
           self.label = lvgl.label(self.screen)        # a label on it
           self.label.set_text("Hello, Supercon!")
           self.label.set_style_text_font(lvgl.font_montserrat_48, 0)
           self.label.align(lvgl.ALIGN.CENTER, 0, 0)

       def show(self):
           lvgl.refr_now(display.lv_display)           # LVGL draws into the framebuffers
           display.update()                            # the e-ink shows them

       def run(self):
           if self.launched:
               if self.screen is None:
                   self.build()
               lvgl.screen_load(self.screen)
               self.screen.invalidate()                # redraw all of it
               self.show()
   ```

2. Save, **Ctrl+D**, and open your app. Your text appears in the middle of the screen,
   after a refresh. E-ink is slow: this one takes over half a minute.

3. **Change it on a button.** At the end of `run()`:

   ```python
           if {{ facts.buttons.app_1 }}:
               self.presses += 1
               self.label.set_text(f"Pressed {self.presses} times")
               self.show()
   ```

   Save, **Ctrl+D**, open your app, and press **{{ facts.buttons.app_1_label }}** a few times. Wait for each
   refresh to finish before the next press.

4. **Leave and come back.** Open Gallery, then your app again. Your screen comes back,
   with the count where you left it: `build()` only ran once, and the label kept its text.

5. **Now do it wrong, on purpose.** Add this at the end of `run()`, so the label changes
   on *every* call:

   ```python
           self.label.set_text(str(time.ticks_ms()))   # add "import time" at the top
           self.show()
   ```

   Open your app and watch the screen, and the shell. Does it flash non-stop, lag far
   behind, or both? Do the buttons still work? Now **delete those two lines**.

**✅ Done when** your app shows your text, and **{{ facts.buttons.app_1_label }}** changes it.

## What just happened

**LVGL** is a graphics library: you describe the screen as a tree of **widgets**, and
it draws them. You made a tree:

```
screen (lvgl.obj())
 └─ label "Hello, Supercon!"
```

Every widget is created *inside* a parent (`lvgl.label(self.screen)`), and its position
is relative to that parent (`align(CENTER)` means the center of the screen). A widget
made with no parent, `lvgl.obj()`, is a whole screen; `lvgl.screen_load()` makes it the
one LVGL draws.

On this badge, **nothing draws until you say so**. There's no LVGL task running in the
background. It takes two calls, every time:

1. `lvgl.refr_now(display.lv_display)`: LVGL redraws whatever changed (here, the
   label), and the firmware turns those pixels into black, white or red in the
   framebuffers (`_lv_flush()` in `lib/epd.py`). This runs right there, in your `run()`,
   and it visits every pixel it redraws: about half a second for the whole screen,
   a few hundredths for one label.
2. `display.update()`: the display task sends the framebuffers to the e-ink.

`set_text()` on its own draws nothing. It only marks the label as changed, so the
next `refr_now()` knows what to redraw. Other apps draw into the same framebuffers
without telling LVGL (Gallery does), so when your app opens, `invalidate()` the whole
screen to draw all of it again.

**The e-ink rule.** A refresh takes seconds and flashes the screen. If you change the
screen every call, the display spends all its time refreshing, and requests that arrive
mid-refresh are dropped. **Only redraw when what's shown is actually different.**
[[eink-refresh]] shows why it's so slow.

**Only the open app draws.** A task that keeps running after you leave your app
(see [[firmware-diagram]]) must not call `show()`: it would draw on someone else's
screen.

<!-- TODO(diagram): your code → set_text() marks the label dirty → refr_now() → _lv_flush() → black/red framebuffers → update() → display task → e-ink -->

## Stuck?

| Symptom | Fix |
|---|---|
| Nothing on screen | Did you call both `lvgl.refr_now(display.lv_display)` and `display.update()`? |
| A label change didn't show | You pressed during a refresh, and that request was dropped. Press again once it's done. |
| `AttributeError: 'MyApp' object has no attribute 'label'` | The button code ran before `build()`. Check that `if self.launched:` comes first in `run()`. |
| The old app's picture shows through | You skipped `self.screen.invalidate()`, so LVGL only redrew what *it* thought had changed. |
| Screen flashes constantly | You're changing it too often. Only redraw on a change. |
| Text is cut off | The screen is {{ facts.display.width }} × {{ facts.display.height }} pixels. Use shorter text, a smaller font, or `\n` for a new line. |

## Have fun!

- Change the font: the badge has `lvgl.font_montserrat_` 14, 16, 24, 28, 32, 36, 40, 44 and 48.
- Add a second label with `align(lvgl.ALIGN.TOP_LEFT, 5, 5)`.
- Watch the first LED while your app draws: blue while LVGL draws, blinking red while the
  panel refreshes, green when it's done. That's the display code telling people to wait.
- Try another widget: `lvgl.bar(self.screen)` with `.set_value(50, 0)`.
- A magic 8-ball: each button press shows a random answer from a list (`random.choice`). Or roll dice with `random.randint(1, 6)`.
- "They fight crime!": build "He's a ___. She's a ___. They fight crime!" from your own lists of random words, and show a new one on every press. (For the real website's version, see [[web-data]].)
