---
id: name-badge
title: Edit the name badge app (text, image, sensor, widget)
label: Edit the base app
topic: modify-app
workshop: true
needs: [update-firmware]
time: 20–40 min
touches: [apps/nametag.py]     # TODO: facts.name_badge.file
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): every line quoted from the app below; swap in this year's once the firmware is out -->

**Goal:** Change the badge's own name badge app and see your change on the screen.
Start with one line of text; go as far as showing a live sensor reading.

## You need

- Your badge, on the latest firmware (see [[update-firmware]])
- A fresh [[backup]]. You're about to edit a file on the badge.

## Steps

1. **The easy way first.** On the badge, open **{{ facts.name_badge.app }}** from the menu
   and set your name. No laptop needed.

   <!-- TODO(verify): how this year's app sets the name (on-badge keyboard? config app?) -->

2. **Open the app's code.** In Thonny's **Files** view, double-click
   `{{ facts.name_badge.file }}` in the bottom (badge) pane. The tab's title says
   `[ {{ facts.name_badge.file }} ]` with brackets: you're editing the copy *on the badge*.

3. **Pick a change** from the list below. Each one is a little bigger than the last. Do
   **A** first, then as many of the others as you like.

4. Save with **Ctrl+S** (**Cmd+S**). That writes the file to the badge's flash.

5. Restart the badge's program: click in the shell and press **Ctrl+D**. Open
   **{{ facts.name_badge.app }}** again and look for your change.

### A. Change some text

Search (**Ctrl+F**) for `{{ facts.name_badge.text }}`. Change the words between the
quotes, and nothing else. Keep both quotes.

Then try `{{ facts.name_badge.find }}`: it sets {{ facts.name_badge.what }}. Change it to
`{{ facts.name_badge.replace }}`.

### B. Swap the image

Search for `{{ facts.name_badge.image }}`. That's the picture the app shows. See what
else is on the badge:

```python
import os
os.listdir('images')
```

Change the file name to another image from that list. Want your *own* picture? It
has to be converted for the e-ink first: see [[eink-images]].

### C. Show a sensor reading

This is the workshop's project. You'll need your sensor connected and a working
conversion from [[real-units]]. Three additions to the app:

1. At the top of the file, with the other imports:

   ```python
   import time
   import lvgl
   ```

2. Where the app builds its screen (search for `lvgl.label(`; it's usually in
   `switch_to_foreground()`), add a label of your own. `parent` is whatever the
   app's other labels are created in:

   ```python
           self.temp_label = lvgl.label(parent)
           self.temp_label.align(lvgl.ALIGN.BOTTOM_MID, 0, -10)
           self.temp_label.set_text("--")
           self.shown = None
           self.last_read = 0
   ```

3. In `run_foreground()`, read the sensor every 5 seconds, and only change the
   screen when the text changes:

   ```python
           now = time.ticks_ms()
           if time.ticks_diff(now, self.last_read) > 5000:
               self.last_read = now
               raw = self.badge.{{ facts.sao.i2c_attr }}.readfrom_mem({{ facts.sensor.address }}, {{ facts.sensor.register }}, {{ facts.sensor.bytes }})
               text = f"{to_units(raw):.0f} {{ facts.sensor.units }}"
               if text != self.shown:
                   self.temp_label.set_text(text)
                   self.shown = text
   ```

   `to_units()` is the function you wrote in [[real-units]]. Paste it near the top
   of the file, below the imports, with any imports it needs (`import struct`).

### D. Change a widget

Swap a label for something else LVGL can draw: a bar that fills up, a box with a
border, a second line of text in a different font. Start with [[lvgl-hello]] to see
how widgets are made, then find the app's `lvgl.` lines and add or change one.

<!-- TODO(photo): name badge before and after each of A–D -->

**✅ Done when** the badge shows your name with at least one change you made in code.

## What just happened

Saving in Thonny wrote a new copy of the file to the badge, but the old version was
still loaded in RAM. Python reads a file when it's **imported**, and the badge only
imports its apps once, at startup. So a change takes effect after a restart (see
[[resets]]).

Your edit also changed what kind of file this is (see [[map-firmware]]):
`{{ facts.name_badge.file }}` used to match the folder, and now it's **yours**. Back it up.
When an update changes the same file, you'll have to choose between your version and
theirs (see [[update-firmware]]).

Change C follows the **e-ink rule**: read often if you like, but only touch the screen
when what it shows has changed. Rounding to whole degrees (`:.0f`) means fewer changes,
so fewer slow refreshes. [[eink-updates]] has more on that.

<!-- TODO(diagram): editor → Ctrl+S → flash (file) → Ctrl+D → import → RAM (running app) -->

## Stuck?

| Symptom | Fix |
|---|---|
| Nothing changed | Did you save (no `*` on the tab)? Did you restart (**Ctrl+D**)? |
| The tab title has no brackets | You opened the laptop's copy. Open the file from the bottom (badge) pane. |
| Badge shows an error, or a blank screen | Read the traceback in the shell: see [[break-and-restore]]. |
| Can't find the line | The firmware may have changed. Search for `font`, `label` or `.png` instead, or ask a helper. |
| `NameError: to_units` | Paste your function from [[real-units]] into the file, above `class App`. |
| `OSError: [Errno 19] ENODEV` | The sensor didn't answer. Check it with [[i2c-scan]]. |
| Image is missing or garbled | Check the file name with `os.listdir('images')`. Your own image must be converted first ([[eink-images]]). |

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
- See exactly what you changed: [[badge-diff]].
