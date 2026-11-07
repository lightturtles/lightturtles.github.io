---
id: name-badge
title: Edit the name badge app (text, image, sensor, widget)
label: Edit the base app
topic: modify-app
workshop: true
needs: [firmware-diagram, backup]
time: 20–40 min
touches:
  - apps/nametag.py#NametagApp.run   # the PNG path, the plate, the two empty labels, the inv_p trick
  - lib/epd.py#EPaperDisplay.update  # every update() is a full e-ink refresh
  - lib/app_switcher.py#AppSwitcher.arun   # launched is True only on the first run() after you pick the app
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Change the badge's own name badge app and see your change on the screen.
Start with your name; go as far as showing a live sensor reading.

## You need

- Your badge, on the latest firmware (see [[update-firmware]])
- A fresh [[backup]]. You're about to edit a file on the badge.

## Steps

1. **See it as it comes.** Open **{{ facts.name_badge.app }}** from the menu (see
   [[use-badge]]). A big "HELLO I am" sticker, with a blank where your name goes.
   There's no way to type a name on the badge, so you'll put it in the code.

2. **Open the app's code.** In Thonny's **Files** view, double-click
   `{{ facts.name_badge.file }}` in the bottom (badge) pane. The tab's title says
   `[ {{ facts.name_badge.file }} ]` with brackets: you're editing the copy *on the badge*.

3. **Pick a change** from the list below. Each one is a little bigger than the last. Do
   **A** first, then as many of the others as you like.

4. Save with **Ctrl+S** (**Cmd+S**). That writes the file to the badge's flash.

5. Restart the badge's program: click in the shell and press **Ctrl+D**. Open
   **{{ facts.name_badge.app }}** again from the menu and look for your change.

### A. Write your name

Search (**Ctrl+F**) for `{{ facts.name_badge.find }}`. Put your name between the quotes,
and change nothing else:

```python
            hello.set_text("Ada")
```

A few lines down, `world.set_text("")` is a second line under your name. Put something
there too: your handle, your pronouns, what you're hacking on.

Too long to fit? Find `_FONT = lvgl.font_montserrat_48` near the top and try `24`
instead of `48`.

### B. Swap the image

Search for `{{ facts.name_badge.image }}`. That's the picture behind your name. See what
else is on the badge:

```python
import os
os.listdir('/data/graphics')
```

Change the file name to another picture from that list. (`SayItWithMe_blank.png` is
another blank sticker.) Your name is placed for the "HELLO I am" picture, so on other
pictures it may land in an odd spot. `_NAME_TOP` and `_NAME_BOTTOM`, near the top of the
file, set where it goes.

Want your *own* picture? It has to be 960×672 and converted to the panel's three colors
first: see [[eink-images]].

### C. Show a sensor reading

This is the workshop's project. You'll need your sensor connected and its library on
the badge ([[use-a-library]]). The examples use the {{ facts.sensors.aht20.name }};
swap in your sensor's library and class (`bh1750.BH1750`, `lis3dh.LIS3DH`,
`cap1203.CAP1203`).

1. **At the top of the file**, below the other imports:

   ```python
   import time
   from lib.sao import i2c
   import aht20                    # your sensor's library
   ```

2. **Put the reading on the second line.** Find `world.set_text("")` and replace that one
   line with these:

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
                   leds.fill((0, 1, 1))
                   self.world.set_text(text)
                   self.plate.invalidate()         # redraw just the name plate
                   lvgl.refr_now(display.lv_display)
                   display.update()
                   leds.fill((0, 1, 0))
   ```

   <!-- TODO(verify) on a real badge: the plate redraw after set_text (no stray pixels when the text gets shorter) -->

### D. Change a widget

Give your name a red border. Find `plate.set_style_pad_all(8, 0)` and add two lines
under it (`_RED` is already defined at the top of the file):

```python
            plate.set_style_border_width(4, 0)
            plate.set_style_border_color(_RED, 0)
```

Then try something else LVGL can draw: a bar that fills up with your sensor's reading,
or a third line in a different font. [[lvgl-hello]] shows how widgets are made.

<!-- TODO(photo): name badge before and after each of A–D -->

**✅ Done when** the badge shows your name, put there by your code.

## What just happened

Saving in Thonny wrote a new copy of the file to the badge, but the old version was
still loaded in RAM. Python reads a file when it's **imported**, and the badge only
imports its apps once, at start-up. So a change takes effect after a restart (see
[[resets]]).

`run()` is called over and over, about 10 times a second, while the app is on screen.
`self.launched` is `True` only the first time after you pick the app from the menu, so
the stock app draws once and then does nothing. Change C adds the "then" part.

Change C also follows the **e-ink rule**: read as often as you like, but only touch the
screen when what it shows has changed. Every `display.update()` redraws the whole panel,
which takes seconds and makes it flash. That's why it checks once a minute, and only
redraws when the text is different.

Your edit also changed what kind of file this is (see [[map-firmware]]):
`{{ facts.name_badge.file }}` used to match the folder, and now it's **yours**. Back it up.
When an update changes the same file, you'll have to choose between your version and
theirs (see [[update-firmware]]).

<!-- TODO(diagram): editor → Ctrl+S → flash (file) → Ctrl+D → import → RAM (running app) -->

## Stuck?

| Symptom | Fix |
|---|---|
| Nothing changed | Did you save (no `*` on the tab)? Did you restart (**Ctrl+D**)? Did you open **{{ facts.name_badge.app }}** again? |
| The tab title has no brackets | You opened the laptop's copy. Open the file from the bottom (badge) pane. |
| The badge stops at `>>>` after **Ctrl+D** | A typo the badge can't even read (`SyntaxError`). Read the traceback: see [[break-and-restore]]. |
| The shell says `Nametag hit an exception` | A mistake in a line that ran. The line under it says which. See [[break-and-restore]]. |
| LEDs stay cyan and the screen doesn't change | Same thing: look for `hit an exception` in the shell. |
| `ImportError: no module named 'aht20'` | Your sensor's library isn't in `/lib` (see [[add-a-library]]). |
| `OSError: [Errno 19] ENODEV` | The sensor didn't answer. Check it with [[i2c-scan]]. |
| Your name runs off the sticker | Use a smaller font (A), or a shorter name. |
| Image missing or garbled | Check the file name with `os.listdir('/data/graphics')`. Your own image must be converted first ([[eink-images]]). |

## Prefer the command line?

```bash
mpremote edit :{{ facts.name_badge.file }}    # opens it in $EDITOR, saves back to the badge
mpremote soft-reset
```

Don't edit the files in the official folder itself. It's your reference for what
"unchanged" looks like.

## Have fun!

- Make the change and its opposite a few times. How long does each round trip take?
  [[mount-and-run]] makes it shorter.
- Show the sensor's minimum and maximum since the app started.
- Make **User A** refresh the reading right away (`UserA.pressed()` is already imported).
- See exactly what you changed: [[badge-diff]].
