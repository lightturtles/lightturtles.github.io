---
id: app-screen
title: "Lay out a real screen: header, image, and your live data"
label: Build your screen
tier: core
difficulty: 8
group: display
icon: image
needs: [lvgl-hello, live-data]
time: 30 min
touches: [apps/userA.py, ui/page.py, ui/graphics.py, ui/styles.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): Page / graphics helpers below are from the 2025 firmware -->

**Goal:** Turn your app into something worth showing off: a header, a picture, a
button bar, and your live data on screen.

## You need

- Your app, with [[lvgl-hello]] and [[live-data]] done
- An image on the badge. Use `{{ facts.display.sample_image }}` (it's already on the badge), or copy the
  workshop's image to `images/` on the badge. <!-- TODO: provide a workshop image sized and colored for the e-ink -->

## Steps

1. **Imports** at the top of your file (keep the ones you have):

   ```python
   import time
   import lvgl
   from ui.page import Page
   from ui import graphics
   ```

2. **Lay out the screen.** Replace `switch_to_foreground()`:

   ```python
       def switch_to_foreground(self):
           super().switch_to_foreground()
           self.page = Page()
           self.page.create_infobar(["My Badge App", "v1"])           # header: left, right
           self.page.create_content()
           self.page.create_menubar(["Refresh", "", "", "", "Home"])  # button labels

           self.logo = graphics.create_image("{{ facts.display.sample_image }}", self.page.content)
           self.logo.align(lvgl.ALIGN.LEFT_MID, 10, 0)

           self.value_label = lvgl.label(self.page.content)
           self.value_label.set_style_text_font(lvgl.font_montserrat_28, 0)
           self.value_label.align_to(self.logo, lvgl.ALIGN.OUT_RIGHT_MID, 20, 0)
           self.value_label.set_text("--")
           self.shown = None          # what's on screen right now
           self.last_read = 0

           self.page.replace_screen()
   ```

   The order matters: the header, then the content, then the button bar, top to bottom.

3. **Let go of it when you leave:**

   ```python
       def switch_to_background(self):
           self.page = None
           self.logo = None
           self.value_label = None
           super().switch_to_background()
   ```

4. **Show the data, only when it changes.** In `run_foreground()`:

   ```python
       def run_foreground(self):
           now = time.ticks_ms()
           refresh = {{ facts.buttons.app_1 }}      # "Refresh"
           if refresh or time.ticks_diff(now, self.last_read) > 5000:
               self.last_read = now
               text = f"{self.read_value():.1f} V"
               if text != self.shown:              # the e-ink rule
                   self.value_label.set_text(text)
                   self.shown = text
           if {{ facts.buttons.home }}:            # "Home"
               self.badge.display.clear()
               self.switch_to_background()
   ```

5. Save, **Ctrl+D**, and open your app. Change the world (warm the sensor, unplug USB)
   and wait for the screen to catch up.

6. **Tune it.** Round more (`:.1f` → `:.0f`) and see how often the screen refreshes.
   Is that better or worse for your data?

<!-- TODO(photo): the finished screen on a real badge -->

**✅ Done when** your screen shows a header, an image, button labels, and a value that
updates on its own.

## What just happened

`Page` stacks three areas top to bottom: an **info bar**, a **content** area that
stretches to fill the space, and a **menu bar** whose labels line up with the
buttons. You placed widgets inside the content area, and placed the label *relative
to the image* (`align_to(self.logo, OUT_RIGHT_MID, ...)`), so moving the image moves the
label too.

`self.shown` remembers what's on the screen, so you only call `set_text()` when the
text changes. Rounding helps too: `3.71 V` → `3.72 V` → `3.71 V` is three refreshes,
but `3.7 V` is none. On e-ink, **how you format the data decides how often the screen
flashes**.

`graphics.create_image()` reads the image file and hands its bytes to LVGL, which
decodes it. The e-ink can only show {{ facts.display.colors }}, so photos get reduced to those.
Simple, high-contrast images look best.

## Stuck?

| Symptom | Fix |
|---|---|
| `OSError: [Errno 2] ENOENT` | The image path is wrong. Check it with `os.listdir('images')` at `>>>`. |
| Label sits on top of the image | `align_to` needs the image created *first*. Check the order. |
| Value never updates | Is `self.last_read` set in `switch_to_foreground()`? Is the app in the foreground? |

<!-- TODO(verify): image missing with no error (unsupported format/size?); do menu bar labels line up with the buttons? -->

## Have fun!

- Add a second value under the first (battery *and* temperature).
- Color the header {{ facts.display.third_color }}, the screen's third color.
- Draw a bar that fills with the value: `lvgl.bar(...)`, `.set_range(...)`, `.set_value(...)`.
- Show a QR code to your site: `lvgl.qrcode(...)`, if this build has it. <!-- TODO(verify) -->
