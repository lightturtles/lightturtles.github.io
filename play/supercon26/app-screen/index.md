---
id: app-screen
title: "Lay out a real screen: containers, alignment and fonts"
label: Layout and fonts
topic: display
workshop: false
needs: [lvgl-hello]
time: 30 min
touches:
  - apps/schedule.py#ScheduleApp._build   # the firmware's own full-screen LVGL layout
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Go from one label to a screen you'd be proud of: a header, a row of values
laid out neatly, button hints, and fonts that fit.

## You need

- Your app from [[lvgl-hello]]

## Steps

1. **A frame for the whole screen.** Make the screen itself a column: header at the
   top, the values in the middle, button hints at the bottom. Replace your `build()`:

   ```python
       def build(self):
           scr = lvgl.obj()
           scr.set_flex_flow(lvgl.FLEX_FLOW.COLUMN)          # top to bottom
           scr.set_flex_align(lvgl.FLEX_ALIGN.SPACE_BETWEEN,
                              lvgl.FLEX_ALIGN.CENTER, lvgl.FLEX_ALIGN.CENTER)

           header = lvgl.label(scr)
           header.set_text("{{ facts.firmware.user_app_name }}")
           header.set_style_text_font(lvgl.font_montserrat_36, 0)

           row = lvgl.obj(scr)                               # a box to hold the three boxes
           row.set_size(lvgl.pct(100), lvgl.SIZE_CONTENT)
           row.set_flex_flow(lvgl.FLEX_FLOW.ROW)
           row.set_flex_align(lvgl.FLEX_ALIGN.SPACE_EVENLY,
                              lvgl.FLEX_ALIGN.CENTER, lvgl.FLEX_ALIGN.CENTER)
           self.boxes = []
           for title in ("Presses", "Seconds", "Mode"):
               self.boxes.append(self.make_box(row, title))

           footer = lvgl.label(scr)
           footer.set_text("A: +1      B: reset      Menu: leave")
           footer.set_style_text_font(lvgl.font_montserrat_24, 0)
           self.screen = scr
   ```

   The order you create them in is the order they stack in.

2. **A box with a title and a big number.** Each box is a container too, stacking its
   two labels in a column. Add this method:

   ```python
       def make_box(self, parent, title):
           box = lvgl.obj(parent)
           box.set_size(lvgl.SIZE_CONTENT, lvgl.SIZE_CONTENT)
           box.set_flex_flow(lvgl.FLEX_FLOW.COLUMN)
           box.set_flex_align(lvgl.FLEX_ALIGN.CENTER,
                              lvgl.FLEX_ALIGN.CENTER, lvgl.FLEX_ALIGN.CENTER)

           name = lvgl.label(box)
           name.set_text(title)
           name.set_style_text_font(lvgl.font_montserrat_24, 0)

           value = lvgl.label(box)
           value.set_text("0")
           value.set_style_text_font(lvgl.font_montserrat_48, 0)
           return value          # the label you'll change later
   ```

3. **Which fonts are there?** Only the fonts compiled into the firmware exist. At `>>>`:

   ```python
   import lvgl
   [f for f in dir(lvgl) if f.startswith("font_montserrat")]
   ```

   Swap sizes in `make_box` and see how much fits.

4. **Fill it in.** Change the button code at the end of `run()`, so
   **{{ facts.buttons.app_1_label }}** counts and **{{ facts.buttons.app_2_label }}** resets (and add `UserB` to the
   `from lib.button import` line):

   ```python
           if {{ facts.buttons.app_1 }}:
               self.presses += 1
               self.boxes[0].set_text(str(self.presses))
               self.show()
           if {{ facts.buttons.app_2 }}:
               self.presses = 0
               self.boxes[0].set_text("0")
               self.show()
   ```

5. Save, **Ctrl+D**, and open your app.

<!-- TODO(photo): the finished three-box screen -->

**✅ Done when** your screen has a header, three neatly spaced boxes, button hints at
the bottom, and **{{ facts.buttons.app_1_label }}** changes one of the numbers.

## What just happened

**Everything is a box inside a box.** Every LVGL widget has a parent, and its position
is worked out inside that parent. A plain `lvgl.obj` is an empty box: give it children
and a **layout**, and it arranges them for you.

| Tool | Does | Good for |
|---|---|---|
| `align(ALIGN.X, dx, dy)` | puts one widget at a spot in its parent | one thing, in a corner or the middle |
| `align_to(other, ALIGN.OUT_…, dx, dy)` | puts it next to another widget | a label beside an icon |
| **flex** (`set_flex_flow`) | lines children up in a row or column, and spaces them | lists, rows of values, anything repeated |

Flex is the one that saves you arithmetic. Change a font, add a box, and everything
re-spaces itself.

**Sizes.** `lvgl.pct(100)` means "100 % of the parent"; `SIZE_CONTENT` means "just big
enough for what's inside." The screen is {{ facts.display.width }} × {{ facts.display.height }}
pixels, so fewer, bigger things read better from across a room than many small ones.

**Fonts are images of letters,** stored in flash at fixed sizes. That's why you can only
pick from the list in step 3, and why a bigger font costs more flash.

## Stuck?

| Symptom | Fix |
|---|---|
| `AttributeError: ... font_montserrat_28` | Not compiled in. Pick one from step 3's list. |
| Boxes overlap or pile up in a corner | The row needs `set_flex_flow`, and must be the boxes' parent. |
| Boxes have borders you don't want, or grey ones vanish | That's the default style, and the e-ink turns light grey into white and dark grey into black. `box.set_style_border_width(0, 0)` removes a border; `set_style_border_color(lvgl.color_hex(0x000000), 0)` makes it black. |
| The header and footer crowd the boxes | `SPACE_BETWEEN` pushes the first and last children to the edges. Try `SPACE_EVENLY` on the screen too. |

## Have fun!

- Leave a gap in the layout and draw a picture into it with `display.draw_png()` after `refr_now()` (see [[eink-images]]).
- Make one value {{ facts.display.third_color }} (see [[use-red]]).
- Turn the boxes into a column instead: one word changes.
- Show your sensor reading in the first box (see [[use-a-library]]), and the seconds since start in the second (see [[on-time]]).
