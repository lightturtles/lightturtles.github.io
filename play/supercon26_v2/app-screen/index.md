---
id: app-screen
title: "Lay out a real screen: containers, alignment and fonts"
label: Layout and fonts
topic: display
workshop: false
needs: [lvgl-hello]
time: 30 min
touches: [apps/userA.py, ui/page.py, ui/styles.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): Page helper and LVGL calls below are from the 2025 firmware (LVGL 9 names) -->

**Goal:** Go from one label to a screen you'd be proud of: a header, a row of values
laid out neatly, button labels, and fonts that fit.

## You need

- Your app from [[lvgl-hello]]

## Steps

1. **The standard frame.** The firmware's `Page` helper stacks three areas, top to
   bottom. Replace your `switch_to_foreground()`:

   ```python
       def switch_to_foreground(self):
           super().switch_to_foreground()
           self.page = Page()
           self.page.create_infobar(["My App", "v1"])                 # header: left, right
           self.page.create_content()                                 # the middle
           self.page.create_menubar(["+1", "Reset", "", "", "Home"])  # one label per button
           self.build(self.page.content)
           self.page.replace_screen()
   ```

   The order matters: header, then content, then the button bar.

2. **A container for a row.** Make a plain object to hold things side by side, and let
   LVGL arrange them:

   ```python
       def build(self, parent):
           row = lvgl.obj(parent)
           row.set_size(lvgl.pct(100), lvgl.SIZE_CONTENT)
           row.set_flex_flow(lvgl.FLEX_FLOW.ROW)
           row.set_flex_align(lvgl.FLEX_ALIGN.SPACE_EVENLY,
                              lvgl.FLEX_ALIGN.CENTER, lvgl.FLEX_ALIGN.CENTER)
           row.align(lvgl.ALIGN.CENTER, 0, 0)

           self.boxes = []
           for title in ("Presses", "Seconds", "Mode"):
               self.boxes.append(self.make_box(row, title))
   ```

3. **A box with a title and a big number.** Each one is a container too, stacking its
   two labels in a column:

   ```python
       def make_box(self, parent, title):
           box = lvgl.obj(parent)
           box.set_size(lvgl.SIZE_CONTENT, lvgl.SIZE_CONTENT)
           box.set_flex_flow(lvgl.FLEX_FLOW.COLUMN)
           box.set_flex_align(lvgl.FLEX_ALIGN.CENTER,
                              lvgl.FLEX_ALIGN.CENTER, lvgl.FLEX_ALIGN.CENTER)

           name = lvgl.label(box)
           name.set_text(title)
           name.set_style_text_font(lvgl.font_montserrat_14, 0)

           value = lvgl.label(box)
           value.set_text("0")
           value.set_style_text_font(lvgl.font_montserrat_28, 0)
           return value          # the label you'll change later
   ```

4. **Which fonts are there?** Only the fonts compiled into the firmware exist. At `>>>`:

   ```python
   import lvgl
   [f for f in dir(lvgl) if f.startswith("font_")]
   ```

   Swap sizes in `make_box` and see how much fits.

5. **Fill it in.** Let **{{ facts.buttons.app_1_label }}** count, and show it:

   ```python
       def run_foreground(self):
           if {{ facts.buttons.app_1 }}:
               self.presses = getattr(self, "presses", 0) + 1
               self.boxes[0].set_text(str(self.presses))
           if {{ facts.buttons.home }}:
               self.badge.display.clear()
               self.switch_to_background()
   ```

   And let go of it all in `switch_to_background()`: `self.page = None`,
   `self.boxes = []`.

6. Save, **Ctrl+D**, and open your app.

<!-- TODO(photo): the finished three-box screen -->

**✅ Done when** your screen has a header, three neatly spaced boxes, button labels at
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
pick from the list in step 4, and why a bigger font costs more flash.

## Stuck?

| Symptom | Fix |
|---|---|
| `AttributeError: ... font_montserrat_28` | Not compiled in. Pick one from step 4's list. |
| Boxes overlap or pile up in a corner | The row needs `set_flex_flow`, and must be the boxes' parent. |
| Boxes have borders and shadows you don't want | That's the default style. `box.set_style_border_width(0, 0)` removes the border. |
| Menu labels don't line up with the buttons | Count the entries: one per button, `""` for unused ones. |

## Have fun!

- Put an image in one of the boxes (see [[eink-images]]).
- Make one value {{ facts.display.third_color }} (see [[use-red]]).
- Turn the boxes into a column instead: one word changes.
- Show your sensor reading in the first box (see [[real-units]]).
