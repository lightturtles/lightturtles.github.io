---
id: lvgl-hello
title: Put one LVGL label on the screen from your app
label: Hello, LVGL
topic: display
workshop: false
needs: [first-app]
time: 20 min
touches: [apps/userA.py, ui/page.py, hardware/display.py, hardware/lvgl_setup.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): Page helper and LVGL calls below are from the 2025 firmware -->

**Goal:** Draw text on the e-ink screen when your app comes to the foreground, and
change it when you press a button.

## You need

- Your app from [[first-app]]

## Steps

1. **Add the imports** at the top of `{{ facts.firmware.user_app }}`:

   ```python
   import lvgl
   from ui.page import Page
   ```

2. **Build the screen when you get it.** Replace your `switch_to_foreground()`:

   ```python
       def switch_to_foreground(self):
           super().switch_to_foreground()
           self.presses = 0
           self.page = Page()                       # a new, empty screen
           self.page.create_content()               # an area to put things in
           self.label = lvgl.label(self.page.content)
           self.label.set_text("Hello, Supercon!")
           self.label.align(lvgl.ALIGN.CENTER, 0, 0)
           self.page.replace_screen()               # show it
   ```

3. **Let go of it when you leave.** Replace your `switch_to_background()`:

   ```python
       def switch_to_background(self):
           self.page = None
           self.label = None
           super().switch_to_background()
   ```

4. Save, **Ctrl+D**, and open your app. Your text appears in the middle of the screen
   (after a refresh; e-ink is slow).

5. **Change it on a button.** In `run_foreground()`, where you print on **{{ facts.buttons.app_1_label }}**:

   ```python
           if {{ facts.buttons.app_1 }}:
               self.presses += 1
               self.label.set_text(f"Pressed {self.presses} times")
   ```

   Save, **Ctrl+D**, open your app, and press **{{ facts.buttons.app_1_label }}** a few times.

6. **Now do it wrong, on purpose.** Add this line at the end of `run_foreground()`, so
   the label changes on *every* call:

   ```python
           self.label.set_text(str(time.ticks_ms()))   # add "import time" at the top
   ```

   Open your app and watch the screen. Does it flicker non-stop, lag far behind, or
   both? <!-- TODO(verify) --> Now **delete that line**.

**✅ Done when** your app shows your text, and **{{ facts.buttons.app_1_label }}** changes it.

## What just happened

**LVGL** is a graphics library: you describe the screen as a tree of **widgets**, and
it draws them. You made a tree:

```
screen (Page)
 └─ content area
     └─ label "Hello, Supercon!"
```

Every widget is created *inside* a parent (`lvgl.label(self.page.content)`), and its
position is relative to that parent (`align(CENTER)` means the center of the content
area). `Page` is the firmware's helper that makes a screen with the standard layout.
`replace_screen()` swaps it in.

`set_text()` doesn't draw anything. It marks the label as changed. LVGL has its own
asyncio task (in `hardware/lvgl_setup.py`) that wakes up every {{ facts.display.lvgl_period_ms }} ms, redraws
whatever changed, and sends it to the display. That's another task taking turns with
yours.

**The e-ink rule.** An e-ink refresh takes {{ facts.display.refresh_s }} seconds and flashes the screen. If
you change the screen every call, the display spends all its time refreshing and
never catches up. **Only call `set_text()` when the text is actually different.**
[[eink-refresh]] shows why it's so slow.

**Only the foreground app draws.** You build your screen in `switch_to_foreground()`
and drop it in `switch_to_background()`. A background app that touches widgets is
drawing on someone else's screen, or on a screen that's gone.

<!-- TODO(diagram): your code → set_text() marks label dirty → LVGL task (every N ms) → redraws dirty area → display driver → e-ink -->

## Stuck?

| Symptom | Fix |
|---|---|
| Nothing on screen | Did you call `self.page.replace_screen()`? Did the app come to the foreground? |
| `AttributeError: 'NoneType' ... 'set_text'` | You touched `self.label` while the app was in the background. Only use it in `run_foreground()`. |
| `AttributeError: 'App' object has no attribute 'label'` | `run_foreground()` ran before `switch_to_foreground()` made the label. Check that `super().switch_to_foreground()` is the *first* line. |
| Screen flickers constantly | You're changing it too often. Only `set_text()` on a change. |
| Text is cut off | The screen is {{ facts.display.width }} × {{ facts.display.height }} pixels. Use shorter text, or `\n` for a new line. |

## Have fun!

- Change the font: `self.label.set_style_text_font(lvgl.font_montserrat_28, 0)`.
  (`{{ facts.name_badge.file }}` lists the fonts the firmware has.)
- Add a second label with `align(lvgl.ALIGN.TOP_LEFT, 5, 5)`.
- Try another widget: `lvgl.bar(self.page.content)` with `.set_value(50, 0)`.
- A magic 8-ball: each button press shows a random answer from a list (`random.choice`). Or roll dice with `random.randint(1, 6)`.
- "They fight crime!": build "He's a ___. She's a ___. They fight crime!" from your own lists of random words, and show a new one on every press. (For the real website's version, see [[web-data]].)
