---
id: draw-pixels
title: Draw pixels, shapes and charts (LVGL chart and canvas)
label: Draw pixels, shapes and charts
topic: display
workshop: false
needs: [lvgl-hello]
time: 30 min
touches: [apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): chart and canvas calls are LVGL 9's; check lvgl.version_major() on the badge, and which widgets are compiled in -->

**Goal:** Draw things that aren't text: a graph of numbers over time, and a canvas
you can set pixel by pixel for game boards and generated art.

## You need

- Your app from [[lvgl-hello]]

## Steps

### A chart

1. **Make a chart** in `switch_to_foreground()`, where you made your label:

   ```python
           self.chart = lvgl.chart(self.page.content)
           self.chart.set_size(200, 100)
           self.chart.align(lvgl.ALIGN.CENTER, 0, 0)
           self.chart.set_type(lvgl.chart.TYPE.LINE)
           self.chart.set_point_count(20)                         # 20 points across
           self.chart.set_range(lvgl.chart.AXIS.PRIMARY_Y, 0, 100)
           self.series = self.chart.add_series(lvgl.color_black(), lvgl.chart.AXIS.PRIMARY_Y)
   ```

2. **Add a point** on **{{ facts.buttons.app_1_label }}**:

   ```python
           if {{ facts.buttons.app_1 }}:
               import random
               self.chart.set_next_value(self.series, random.randint(0, 100))
   ```

   Each new point pushes the oldest off the left. Press it 20 times.

3. **Plot something real.** Swap the random number for a reading: the seconds since
   start, `gc.mem_free() // 1000` (see [[out-of-memory]]), or your sensor (see
   [[real-units]]). Add a point every few seconds, not every call: every point is a
   screen refresh.

### A canvas

4. **Make a canvas:** a blank image you draw on. It needs a buffer to hold its pixels:

   ```python
           W, H = 64, 64
           self.buf = bytearray(W * H * 2)            # 2 bytes per pixel (RGB565)
           self.canvas = lvgl.canvas(self.page.content)
           self.canvas.set_buffer(self.buf, W, H, lvgl.COLOR_FORMAT.RGB565)
           self.canvas.align(lvgl.ALIGN.RIGHT_MID, -10, 0)
           self.canvas.fill_bg(lvgl.color_white(), lvgl.OPA.COVER)
   ```

5. **Set some pixels.** A checkerboard, 8 pixels to a square:

   ```python
           black = lvgl.color_black()
           for y in range(H):
               for x in range(W):
                   if (x // 8 + y // 8) % 2:
                       self.canvas.set_px(x, y, black, lvgl.OPA.COVER)
   ```

6. Save, **Ctrl+D**, open your app. Then try your own pattern: a circle
   (`(x-32)**2 + (y-32)**2 < 400`), stripes, or random dots.

<!-- TODO(photo): chart and checkerboard on the e-ink -->

**✅ Done when** your app shows a chart you can add points to, and a canvas with a
pattern you drew pixel by pixel.

## What just happened

A **chart** is a widget that remembers a list of numbers and draws them. You only
hand it new values; it does the scaling and drawing. That makes it the easy way to
show anything over time.

A **canvas** is the opposite: a block of memory with one entry per pixel, and LVGL
copies it to the screen. You decide every pixel. That's what you want for game
boards (tic-tac-toe, Game of Life), fractals, and anything generated.

The canvas's buffer is `W × H × 2` bytes: 8 kB for 64 × 64. A full-screen canvas
is much more (see [[out-of-memory]]). The e-ink only shows {{ facts.display.colors }}
anyway, so the firmware turns your colors into the nearest of those.

**Drawing pixel by pixel in Python is slow.** 4096 `set_px` calls take a noticeable
moment. Draw once, then change only what's new, and keep it short enough not to
freeze the badge (see [[hog-the-cpu]]).

## Stuck?

| Symptom | Fix |
|---|---|
| `AttributeError: ... 'chart'` or `'canvas'` | Not compiled into this build. Check `dir(lvgl)`. |
| `AttributeError` on `set_buffer` or `set_px` | Your LVGL is a different version. `lvgl.version_major()`; v8 uses `set_px_color(x, y, color)` and `lvgl.img.CF.TRUE_COLOR`. |
| The canvas is garbage or black | The buffer is the wrong size for the color format. |
| The badge freezes while drawing | Too many pixels in one call. Draw a few rows per call, as in [[fsm]]. |

## Have fun!

- Conway's Game of Life on a 32 × 32 canvas, one generation per button press.
- A bar chart instead: `set_type(lvgl.chart.TYPE.BAR)`.
- Draw with lines and rectangles instead of pixels: look for `draw_` in `dir(lvgl.canvas)`.
- Draw into a `framebuf.FrameBuffer` (MicroPython's own drawing module: lines, text,
  rectangles), then copy its bytes into the canvas.
- Langton's ant: one ant on a grid of white squares. On white, turn right; on black, turn left; flip the square and step forward. After about 10,000 steps it starts building a "highway". Run a few hundred steps per screen refresh.
- A thermometer with a history graph: the last few hours of readings, redrawn every few minutes, with the minimum and maximum marked in red (see [[real-units]], [[on-time]] and [[use-red]]).
- Let Game of Life run by itself: one generation per screen refresh, with newborn cells in red (see [[eink-updates]]).
