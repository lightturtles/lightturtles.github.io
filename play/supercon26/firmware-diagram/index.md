---
id: firmware-diagram
title: Draw how the badge's code fits together (boot → main.py → apps → hardware)
label: Diagram the firmware
tier: core
difficulty: 5
group: firmware-internals
icon: sitemap
needs: [map-firmware]
time: 20 min
touches: [boot.py, main.py, hardware/badge.py, apps/base_app.py, apps/app_menu.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): file and class names below are from the 2025 firmware -->

**Goal:** Sketch the badge's firmware as boxes and arrows: what starts what, what runs
at the same time, and which code talks to which piece of hardware.

## You need

- Paper and a pen (this works best by hand)
- The official folder on your laptop (see [[map-firmware]]), open in a text editor

## Steps

1. **Start at power-up.** Open `boot.py` and `main.py`. MicroPython runs `boot.py`,
   then `main.py`. Draw a box for each, with an arrow from one to the next. (`boot.py`
   may be empty; draw it anyway.)

2. **Find what `main.py` creates.** Scroll to `async def main()`. Every line that looks
   like `Something(...)` makes an object. Draw a box for each one under `main.py`, with
   an arrow labeled *creates*:
   - `Badge(...)`: one object that holds all the hardware
   - the apps: `nametag.App(...)`, `userA.App(...)` … `userD.App(...)`, and the others
   - the menus: `app_menu.AppMenu(...)`

3. **Find what runs at the same time.** In the same function, look for `.start()` and
   `aio.run(...)`. Open `apps/base_app.py` and find `start()`: it calls
   `aio.create_task(self.run())`. That means **every app gets its own task**. Draw a
   dashed outline around everything that runs as a task:
   - each app (its `run()` loop)
   - the `Badge` object (open `hardware/badge.py`; it creates a task too: what does it do?)
   - LVGL's screen updater (`hardware/lvgl_setup.py`, `lvgl_task_handler`)
   - `main()` itself: its `while True` loop prints a heartbeat every 60 seconds

4. **Find the hardware.** In `hardware/badge.py`, look at `__init__`. Each `self.x = ...`
   is one piece of hardware the apps can reach as `self.badge.x`. Add a row of boxes
   along the bottom of your page: {{ facts.badge.devices }}. Draw *uses* arrows from `Badge` to each.

5. **Find how an app reaches the hardware.** Open `{{ facts.firmware.user_app }}` or
   `{{ facts.name_badge.file }}`. Search for `self.badge.`. Each hit is an arrow from that
   app, through `Badge`, to a hardware box.

6. **Mark what's yours.** Shade the boxes for files you're meant to edit
   ({{ facts.firmware.user_apps }}). Everything else, you *can* edit, but [[backup]] first.

7. Compare with the reference diagram below. Anything you missed? Anything you found
   that it doesn't show?

**✅ Done when** you can point at your drawing and answer: which file runs first? Which
code decides what's on the screen? How does your app reach the LEDs? How many tasks
take turns on the processor?

## What just happened

The firmware is built in layers:

| Layer | What it is | Files |
|---|---|---|
| Start-up | Runs once at power-up | `boot.py`, `main.py` |
| Scheduler | Takes turns between tasks | `asyncio` (built into MicroPython) |
| Apps | Menus, name tag, *your* apps | `apps/` |
| Hardware objects | One Python object per device | `hardware/` |
| MicroPython + drivers | Talk to the chip's pins | Built into the firmware (C) |

Each app only talks *down* the stack, through `self.badge`. Apps don't call each other
directly. The menu switches between them by calling `switch_to_foreground()` and
`switch_to_background()`. You'll see that from the inside in [[first-app]].

The dashed outline matters most. One processor, many tasks: they take turns, and
[[asyncio-basics]] shows how.

<!-- TODO(diagram): reference block diagram. Top: boot.py → main.py. Middle (dashed "tasks"): menus, nametag, userA–D, usb_debug, Badge task, LVGL task, main heartbeat. Bottom: display, buttons, LEDs, SAO I2C, radio. Arrows: creates / runs / uses. -->

## Stuck?

| Symptom | Fix |
|---|---|
| Lost in a long file | Search for `import`, `def ` and `class ` first; skip everything else. |
| Can't tell what an object is | Find its `import` line at the top of the file. That's the file it comes from. |
| Too many boxes | Leave out the apps you don't care about. One app box plus "…and more" is fine. |

## Have fun!

- From the REPL, after **Ctrl+C**: `from apps.base_app import BaseApp`, then
  `[a.name for a in BaseApp.all_apps]`. Does it match your drawing?
- Add the network code (`net/`, if there is one) to your diagram. Which task reads the radio?
