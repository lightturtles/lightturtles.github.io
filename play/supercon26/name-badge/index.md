---
id: name-badge
title: Edit the name badge app (your name, one line of code)
label: Edit the base app
topic: modify-app
workshop: true
needs: [backup]
time: 15 min
touches:
  - apps/nametag.py#NametagApp.run   # the PNG path (line 30), the two empty labels (52, 57), _FONT (14)
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Change one line of the badge's own name badge app and see your change on the
screen.

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

3. **Make a change** from the list below. Do **A** first.

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

### B. Swap the picture

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

<!-- TODO(photo): name badge before and after A, and after B -->

**✅ Done when** the badge shows your name, put there by your code.

## What just happened

Saving in Thonny wrote a new copy of the file to the badge, but the old version was
still loaded in RAM. Python reads a file when it's **imported**, and the badge only
imports its apps once, at start-up. So a change takes effect after a restart (see
[[resets]]).

Your edit also changed what kind of file this is (see [[map-firmware]]):
`{{ facts.name_badge.file }}` used to match the folder, and now it's **yours**. Back it up.
When an update changes the same file, you'll have to choose between your version and
theirs (see [[update-firmware]]).

Next: put a live sensor reading on that second line, in [[sensor-badge]].

<!-- TODO(diagram): editor → Ctrl+S → flash (file) → Ctrl+D → import → RAM (running app) -->

## Stuck?

| Symptom | Fix |
|---|---|
| Nothing changed | Did you save (no `*` on the tab)? Did you restart (**Ctrl+D**)? Did you open **{{ facts.name_badge.app }}** again? |
| The tab title has no brackets | You opened the laptop's copy. Open the file from the bottom (badge) pane. |
| The badge stops at `>>>` after **Ctrl+D** | You probably deleted a quote. Read the traceback (see [[break-and-restore]]), or put the line back the way it was. |
| The shell says `Nametag hit an exception` | A mistake in a line that ran. The line under it says which. See [[break-and-restore]]. |
| Your name runs off the sticker | Use a smaller font (see A), or a shorter name. |
| Picture missing or garbled | Check the file name with `os.listdir('/data/graphics')`. Your own picture must be converted first ([[eink-images]]). |

## Prefer the command line?

```bash
mpremote edit :{{ facts.name_badge.file }}    # opens it in $EDITOR, saves back to the badge
mpremote soft-reset
```

Don't edit the files in the official folder itself. It's your reference for what
"unchanged" looks like.

## Have fun!

- Give your name a red border. Find `plate.set_style_pad_all(8, 0)` and add two lines
  under it (`_RED` is already defined at the top of the file):

  ```python
              plate.set_style_border_width(4, 0)
              plate.set_style_border_color(_RED, 0)
  ```

  More things LVGL can draw are in [[lvgl-hello]].
- Make the change and its opposite a few times. How long does each round trip take?
  [[mount-and-run]] makes it shorter.
- See exactly what you changed: [[badge-diff]].
