---
id: draw-pixels
title: Draw pixels, shapes and charts straight into the e-ink framebuffers
label: Draw pixels, shapes and charts
topic: display
workshop: false
needs: [first-app]
time: 30 min
touches:
  - lib/epd.py#EPaperDisplay   # display.black / display.red (framebuf MONO_HLSB, 960x672), clear(), update()
  - lib/epd.py#EPaperDisplay.run   # an update() asked for during a refresh is dropped
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Draw things that aren't text: a graph of numbers over time, and shapes and
patterns you place pixel by pixel. No LVGL needed.

## You need

- Your app from [[first-app]] (you're about to replace it)

## Steps

### A chart

1. **Replace `{{ facts.firmware.user_app }}`** with this. It keeps a list of numbers, and
   redraws a line chart of them whenever one is added:

   ```python
   """Draw straight into the e-ink's framebuffers: a chart and some shapes."""

   import random
   import time

   from apps.base_app import BaseApp
   from lib.button import UserA, UserB
   from lib.epd import display


   class MyApp(BaseApp):
       def __init__(self):
           super().__init__("{{ facts.firmware.user_app_name }}")
           self.values = []

       def run(self):
           if self.launched:
               self.draw()
           if UserA.pressed():
               self.values.append(random.randint(0, 100))
               self.values = self.values[-20:]     # keep the last 20
               self.draw()

       def draw(self):
           bk, rd = display.black, display.red     # 1 = ink, 0 = white
           display.clear()                         # both framebuffers to white

           bk.text("Random numbers", 60, 40, 1)    # 8x8-pixel letters
           x0, y0, w, h = 60, 600, 840, 500        # the chart's bottom-left corner, and size
           bk.hline(x0, y0, w, 1)                  # x axis
           bk.vline(x0, y0 - h, h, 1)              # y axis

           step = w // 19
           points = [(x0 + i * step, y0 - v * h // 100) for i, v in enumerate(self.values)]
           for (xa, ya), (xb, yb) in zip(points, points[1:]):
               bk.line(xa, ya, xb, yb, 1)
           for x, y in points:
               bk.fill_rect(x - 5, y - 5, 11, 11, 0)   # make room for the red dot...
               rd.fill_rect(x - 5, y - 5, 11, 11, 1)   # ...and draw it in red

           display.update()                        # send it to the e-ink
   ```

2. **Save, Ctrl+D, and open your app.** You get an empty chart. Press **{{ facts.buttons.app_1_label }}** to add a
   point, and wait for the screen to finish refreshing before you press it again.
   Each new point pushes the oldest off once there are 20.

3. **Press it twice, quickly.** The screen shows one new point, not two. The second
   drawing went into the framebuffers while the first was still being sent, and the
   display task threw its request away. Press once more and both catch up.

4. **Plot something real.** Swap the random number for a reading: `gc.mem_free() // 100_000`
   (see [[out-of-memory]]), or your sensor (see [[use-a-library]]). Add a point every
   minute or so, not every call: every point is a whole screen refresh (see [[on-time]]).

### Shapes and pixels

5. **Add a second drawing on {{ facts.buttons.app_2_label }}.** In `run()`, add:

   ```python
           if UserB.pressed():
               self.pattern()
   ```

   and this method to the class:

   ```python
       def pattern(self):
           bk, rd = display.black, display.red
           display.clear()
           for row in range(8):                     # a checkerboard, 64 pixels to a square
               for col in range(8):
                   if (row + col) % 2:
                       bk.fill_rect(220 + col * 64, 80 + row * 64, 64, 64, 1)
           bk.ellipse(480, 336, 120, 120, 0, True)  # a white circle...
           rd.ellipse(480, 336, 100, 100, 1, True)  # ...with a red one inside
           bk.ellipse(480, 336, 100, 100, 0, True)
           t0 = time.ticks_ms()
           for y in range(128):                     # one pixel at a time
               for x in range(128):
                   if (x * x + y * y) % 7 == 0:
                       bk.pixel(800 + x, 500 + y, 1)
           print("128 x 128 pixels took", time.ticks_diff(time.ticks_ms(), t0), "ms")
           display.update()
   ```

6. Save, **Ctrl+D**, open your app, and press **{{ facts.buttons.app_2_label }}**. How long did the
   pixel-by-pixel square take? Then try your own pattern: stripes, random dots, or
   `(x - 64) ** 2 + (y - 64) ** 2 < 2500` for a circle.

<!-- TODO(photo): chart and checkerboard on the e-ink -->

**✅ Done when** your app shows a chart you can add points to, and a pattern you drew
pixel by pixel.

## What just happened

The badge keeps two pictures of the screen in RAM: `display.black` and `display.red`.
Each is a MicroPython **`framebuf.FrameBuffer`** with one bit per pixel,
{{ facts.display.width }} × {{ facts.display.height }}. A 1 in `black` means a black pixel; a 1 in `red`, a red one; 0 in
both means white. (Don't set both for one pixel: clear one when you set the other,
as the red dots do.)

Drawing only changes RAM, and it's fast: `line`, `rect`, `fill_rect`, `ellipse` and
`text` are written in C. Nothing reaches the e-ink until `display.update()`. That tells
the display task (in `main.py`) to send *both whole framebuffers* to the panel, which
takes seconds. While it does, more `update()`s are ignored, so wait for one to finish
before asking for the next: `display.is_done_updating()` tells you.

A **chart** is just this: remember the numbers, and redraw them all when one changes.
For pixel art, game boards (tic-tac-toe, Game of Life) and fractals, you decide every
pixel. **Drawing pixel by pixel in Python is slow**, though. Use the shape functions
where you can, and keep a big job short enough not to freeze the badge (see
[[hog-the-cpu]]).

Apps that draw this way, like Gallery (its `draw_png()` writes straight into the same
framebuffers), skip LVGL entirely. [[lvgl-hello]] is the other way to draw: widgets.

## Stuck?

| Symptom | Fix |
|---|---|
| Nothing changes on the screen | Did you call `display.update()`? Or did you ask during a refresh? Wait, and press again. |
| The text is tiny | `text()` only has one 8 × 8 font. For big text, use LVGL ([[lvgl-hello]]). |
| `AttributeError: ... 'ellipse'` | Your MicroPython is older than 1.20. Use `fill_rect` instead. |
| Bits of the last picture remain | You didn't call `display.clear()` first. |
| The badge freezes while drawing | Too many `pixel()` calls in one go. Draw a few rows per call, as in [[fsm]]. |

## Have fun!

- Conway's Game of Life on a 64 × 64 grid, drawn as 8 × 8 squares, one generation per button press.
- A bar chart instead: `fill_rect` for each value.
- Langton's ant: one ant on a grid of white squares. On white, turn right; on black, turn left; flip the square and step forward. After about 10,000 steps it starts building a "highway". Run a few hundred steps per screen refresh.
- A thermometer with a history graph: the last few hours of readings, redrawn every few minutes, with the minimum and maximum marked in red (see [[use-a-library]], [[on-time]] and [[use-red]]).
- Let Game of Life run by itself: one generation per screen refresh, with newborn cells in red (see [[eink-updates]]).
