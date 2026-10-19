---
id: firmware-diagram
title: "How apps run: main.py, the menu, and the life of an app"
label: How apps run
topic: write-app
workshop: false
needs: [map-firmware]
time: 30 min
touches: [main.py, hardware/badge.py, apps/base_app.py, apps/app_menu.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): file, class and method names below are from the 2025 firmware -->

**Goal:** Sketch how the badge's apps fit together (what `main.py` makes, what runs at
the same time, how an app reaches the hardware), then follow one app through its life
and learn the rules every app has to follow.

## You need

- Paper and a pen (this works best by hand)
- The official folder on your laptop (see [[map-firmware]]), open in a text editor

## Steps

1. **Start at `main.py`.** It's what runs when the badge starts up. (Something runs
   before it; that's in [[resets]].) Skim it before you draw anything. Don't change it.
   Look for:
   - the `import` lines near the top. Each one points at a file or folder from [[map-firmware]].
   - a list of apps. That's where the menu comes from.
   - a loop at the bottom that runs forever. That's what's running whenever you're *not*
     at `>>>`, and why **Ctrl+C** is needed to get there.

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

6. **Follow one app through its life.** Back in `apps/base_app.py`, find each method
   below and write down who calls it and when. Fill in the table under "What just
   happened" as you go.
   - `__init__`: called by `main.py`, once
   - `start()` and `stop()` <!-- TODO(verify): does this year's BaseApp have stop()? -->
   - `switch_to_foreground()` and `switch_to_background()`: search `apps/app_menu.py` for
     who calls them
   - `run()`: the loop from step 3. Which of the next two does it call, and when?
   - `run_foreground()` and `run_background()`: what decides how often each one runs?

7. **Mark what's yours.** Shade the boxes for files you're meant to edit
   ({{ facts.firmware.user_apps }}). Everything else, you *can* edit, but [[backup]] first.

8. Compare with the reference diagram below. Anything you missed? Anything you found
   that it doesn't show?

**✅ Done when** you can point at your drawing and answer: which code decides what's on
the screen? How does your app reach the LEDs? How many tasks take turns on the
processor? And which of your app's methods runs while another app is open?

## What just happened

The firmware is built in layers:

| Layer | What it is | Files |
|---|---|---|
| Start-up | Runs once, when the badge starts | `boot.py`, `main.py` |
| Scheduler | Takes turns between tasks | `asyncio` (built into MicroPython) |
| Apps | Menus, name tag, *your* apps | `apps/` |
| Hardware objects | One Python object per device | `hardware/` |
| MicroPython + drivers | Talk to the chip's pins | Built into the firmware (C) |

Each app only talks *down* the stack, through `self.badge`. Apps don't call each other
directly. The dashed outline matters most: one processor, many tasks, taking turns
(see [[asyncio-basics]]).

### The life of an app

| Method | Called by | When |
|---|---|---|
| `__init__` | `main.py` | once, at start-up |
| `start()` | `main.py` | once; creates the app's task, which runs `run()` |
| `switch_to_foreground()` | the menu | once, when you open the app; it gets the screen |
| `run_foreground()` | `run()` | over and over, every `foreground_sleep_ms`, while the app is open |
| `switch_to_background()` | your app | once, when the user wants to leave; it gives up the screen |
| `run_background()` | `run()` | over and over, every `background_sleep_ms`, *whichever app is open* |
| `stop()` | <!-- TODO(verify) --> | <!-- TODO(verify) --> |

So your app is always in one of two states: **foreground** (on screen) or
**background**. You'll watch that happen in [[first-app]].

### An app that lives in the background

`run_background()` runs whatever app is on screen, so an app can do all its work there
and use the foreground as little more than an on/off switch: a timer that counts down
on the LEDs while you use other apps, a logger that reads a sensor every minute, a
listener for messages from other badges. Its `run_foreground()` can be as short as
"toggle on or off, then `switch_to_background()`."

<!-- TODO(verify): is it OK to call switch_to_background() on the first foreground call, before the screen is drawn? -->

The background has a few rules of its own: no screen (show status with the LEDs
instead), the slowest `background_sleep_ms` that works, and timestamps instead of
counting calls, because background calls come less regularly (see [[on-time]]).

### The rules every app follows

1. **Return quickly.** `run_foreground()` and `run_background()` do one small thing and
   return. A few milliseconds per call (see [[on-time]]).
2. **Never wait inside a call.** No `time.sleep()`, no `while` loop waiting for a button
   or a network reply. Every other task is frozen until you return (see [[hog-the-cpu]]).
3. **Keep what you need for next time in `self`.** Locals vanish when you return (see [[fsm]]).
4. **Don't ask to be called too often.** Every call costs every other app a little time.
   Pick the slowest `foreground_sleep_ms` and `background_sleep_ms` that work.
   <!-- TODO(verify): the firmware's default periods, and whether there's a minimum -->
5. **Only the foreground app draws on the screen.**
6. **Share the rest.** LEDs, SAO pins and the I2C bus are shared on the honor system
   (see [[share-hardware]]).
7. **Always let the user leave.** Whatever your app is doing, the home button
   ({{ facts.buttons.home_label }}) calls `switch_to_background()`.

<!-- TODO(diagram): reference block diagram. Top: main.py. Middle (dashed "tasks"): menus, nametag, userA–D, usb_debug, Badge task, LVGL task, main heartbeat. Bottom: display, buttons, LEDs, SAO I2C, radio. Arrows: creates / runs / uses. -->
<!-- TODO(diagram): app state machine: created → background ⇄ foreground, with which method runs in each state and on each arrow -->

## Stuck?

| Symptom | Fix |
|---|---|
| Lost in a long file | Search for `import`, `def ` and `class ` first; skip everything else. |
| Can't tell what an object is | Find its `import` line at the top of the file. That's the file it comes from. |
| Too many boxes | Leave out the apps you don't care about. One app box plus "…and more" is fine. |
| Can't find who calls a method | Search every file in `apps/` for its name. The menu calls most of them. |

## Have fun!

- From the REPL, after **Ctrl+C**: `from apps.base_app import BaseApp`, then
  `[a.name for a in BaseApp.all_apps]`. Does it match your drawing?
- Add the network code (`net/`, if there is one) to your diagram. Which task reads the radio?
- A focus timer that lives in the background: 25 minutes of work, with one more LED lit
  green as each part passes, then 5 minutes of break in blue. Opening the app starts or
  stops it, then goes straight home (see [[fsm]], [[on-time]] and [[all-leds]]).
