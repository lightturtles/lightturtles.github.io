---
id: sensor-badge
title: Show your sensor's reading on your name badge
label: Your sensor on your badge
topic: modify-app
workshop: true
needs: [name-badge, use-a-library]
time: 20 min
touches:
  - apps/nametag.py#NametagApp.run   # world.set_text("") (line 57), the plate, the inv_p trick
  - lib/epd.py#EPaperDisplay.update  # every update() is a full e-ink refresh
  - lib/app_switcher.py#AppSwitcher.arun   # launched is True only on the first run() after you pick the app
  - lib/sao.py#i2c
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Put a live reading from your sensor on your name badge, under your name, and
keep it up to date.

## You need

- Your name on the badge, from [[name-badge]]
- Your sensor connected, and its library on the badge ([[use-a-library]])
- `{{ facts.name_badge.file }}` open in Thonny from the badge, as in [[name-badge]]

The examples use the {{ facts.sensors.aht20.name }}. Swap in your sensor's library and
class: {% for s in facts.sensors %}`{{ s[1].driver }}.{{ s[1].class }}`{% unless forloop.last %}, {% endunless %}{% endfor %}.

## Steps

1. **At the top of the file**, below the other imports:

   ```python
   import time
   from lib.sao import i2c
   import aht20                    # your sensor's library
   ```

2. **Put the reading on the second line.** Find `world.set_text(...)` (the second line
   under your name) and replace that one line with these:

   ```python
               self.sensor = aht20.AHT20(i2c)          # your sensor's class
               self.shown = self.sensor.text()
               self.last_read = time.ticks_ms()
               world.set_text(self.shown)
               self.world, self.plate = world, plate   # keep them, to change later
   ```

   Save, **Ctrl+D**, and open **{{ facts.name_badge.app }}**. You should see the reading
   under your name. It won't change yet.

3. **Keep it fresh.** At the very end of `run()`, add an `elif` lined up with
   `if self.launched:`. It runs every time the app is called *after* the first:

   ```python
           elif time.ticks_diff(time.ticks_ms(), self.last_read) > 60_000:
               self.last_read = time.ticks_ms()
               text = self.sensor.text()
               if text != self.shown:              # only touch the e-ink if it changed
                   self.shown = text
                   self.world.set_text(text)
                   self.plate.invalidate()         # redraw just the name plate
                   lvgl.refr_now(display.lv_display)
                   display.update()
   ```

   <!-- TODO(verify) on a real badge: the plate redraw after set_text (no stray pixels when the text gets shorter) -->

4. Save, **Ctrl+D**, open **{{ facts.name_badge.app }}**, and change what your sensor
   senses (breathe on it, cover it, tilt it, touch it). Within a minute, the screen
   catches up.

<!-- TODO(photo): name badge with a sensor reading under the name -->

**✅ Done when** your badge shows your name and a reading from your sensor, and the
reading changes on its own.

## What just happened

`run()` is called over and over, about 10 times a second, while the app is on screen.
`self.launched` is `True` only the first time after you pick the app from the menu, so
the stock app draws once and then does nothing. Step 3 added the "then" part. (The
whole picture of how the badge runs its apps is in [[firmware-diagram]].) Anything
it needs later (the sensor, the label, when it last read) has to live in `self`, because
local variables are gone as soon as `run()` returns.

It also follows the **e-ink rule**: read as often as you like, but only touch the screen
when what it shows has changed. Every `display.update()` redraws the whole panel, which
takes about half a minute and makes it flash. (The first LED blinks red while it does;
that's the display code saying "wait".) That's why it checks once a minute, and only redraws
when the text is different. `text()` rounds the reading, so tiny wobbles don't count as
a change.

`plate.invalidate()` tells LVGL that only the name plate needs drawing again, so the
picture behind it is left alone. [[eink-updates]] has more on updating the screen well.

## Stuck?

| Symptom | Fix |
|---|---|
| `ImportError: no module named 'aht20'` | Your sensor's library isn't in `/lib` (see [[add-a-library]]). |
| `OSError: [Errno 19] ENODEV` | The sensor didn't answer. Check it with [[i2c-scan]]. |
| `SyntaxError` in `lib/sao.py` | Your badge still has the firmware it came with, and MicroPython can't read that `lib/sao.py`. Do [[update-firmware]] (or upload just the new `lib/sao.py`). |
| The badge stops at `>>>` after **Ctrl+D** | Usually indenting: the `elif` must line up with `if self.launched:`. Read the traceback (see [[break-and-restore]]). |
| `Nametag hit an exception ... no attribute 'last_read'` | The `elif` ran before the first draw finished. Check step 2 went in *inside* `if self.launched:`. |
| The reading never changes | Wait a full minute. Then check: is the text actually different? (`self.sensor.text()` at the REPL) |
| The screen flashes every minute | That's an e-ink refresh, and it means the reading changed. Make it check less often (`60_000` is in ms). |
| The reading runs off the sticker | Use a smaller font (see [[name-badge]]). |

## Have fun!

- Show the sensor's minimum and maximum since the app started.
- Make **User A** refresh the reading right away (`UserA.pressed()` is already imported).
- Show it on the LEDs too, so it changes instantly between screen updates (see [[all-leds]]).
- Then share your badge app with a neighbor: [[share-apps]].
