---
id: simulator
title: "Run your app in the simulator, on your laptop"
label: Run it in the simulator
topic: advanced
workshop: false
needs: [drive-app]
time: 30 min
touches:
  - firmware/sim/sim.py        # badge-simulator branch: fakes machine, neopixel, the panel and the SAO bus; mounts firmware/badge at /
  - firmware/sim/SIMULATOR.md  # build steps, keys, options, known gaps
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(simulator): the simulator lives on the badge-simulator branch of a fork, not in
     the official repo (yet). Confirm where attendees should get it before sharing this page. -->

**Goal:** Run the badge's firmware, with your app in it, on your laptop: a window with
the screen, the LEDs and the buttons. Change a file, restart in a second, and never
copy anything to a badge until it works.

## You need

- A laptop running Linux (the simulator's build has only been checked on Ubuntu),
  git, Python 3, and about 15 minutes for a one-time build
- Your app from [[first-app]]

## Steps

1. **Get the simulator.** It's the official firmware plus a `firmware/sim/` folder:

   ```bash
   git clone -b badge-simulator https://github.com/nathancharlesjones/2026-Billboard_Badge
   cd 2026-Billboard_Badge
   ```

2. **Build its MicroPython, once.** The simulator runs on
   [lvgl_micropython](https://github.com/lvgl-micropython/lvgl_micropython)'s Unix port:
   MicroPython and LVGL, compiled for your laptop. Follow the **Build** section of
   `firmware/sim/SIMULATOR.md`. It installs a list of packages, clones lvgl_micropython
   into `firmware/sim/`, and compiles it (about 10 minutes the first time).

3. **Run it.** From the repo's top folder:

   ```bash
   firmware/sim/badge-sim
   ```

   A window shows the badge: the e-ink, the LEDs, and the buttons. The shell output
   (`Importing libraries...`, the menu's `Selected app` lines, your `print`s) comes out
   in your terminal. Press **Ctrl+C** there to stop it.

4. **Use it like the badge.** The keyboard stands in for the buttons:

   | Key | Button |
   |---|---|
   | **Left** / **Right** | Menu − / Menu + |
   | **A** / **B** | User A / User B |
   | **Space** | Boot |

   (You can also click the buttons in the window.) Open Nametag and Gallery.

5. **Add your app.** The simulator runs the files in `firmware/badge/` as the badge's
   whole filesystem. Copy your app in, and run again:

   ```bash
   cp my_app.py firmware/badge/apps/
   firmware/sim/badge-sim
   ```

   It's in the menu. Open it, press its buttons, watch its messages in the terminal.

6. **Edit, restart, repeat.** Change your app in your editor, then **Ctrl+C** and run
   `badge-sim` again. That's the whole loop: no copying, no resetting a badge.

7. **Make a crash and read it.** Put the error from [[log-unplugged]] (or a `1 / 0` on a
   button) into your app. The traceback in your terminal is the same one the badge
   would print, with the same file names and line numbers (see [[break-and-restore]]).

8. **Try the options** (all in `SIMULATOR.md`):
   - `--real-refresh`: the e-ink takes as long as the real one. Does your app still
     feel right?
   - `--scale 0.7`: a smaller window.
   - Delete `firmware/sim/data/` to "factory reset" the simulated badge.
   - `python3 firmware/sim/sao_example.py` in a second terminal plugs an emulated I2C
     device into the SAO bus. Scan for it (see [[i2c-scan]]).

9. **Check it on the badge.** When it works in the simulator, copy it to the badge
   (see [[mount-and-run]]) and try it for real.

**✅ Done when** your app runs in the simulator's menu, you've changed it and seen the
change after a restart, and you've read a traceback from it.

## What just happened

The simulator runs the badge's **own firmware files**, unchanged, in a real MicroPython
on your laptop. Only the edges are swapped: `machine.Pin`, the LEDs' `neopixel`, the
e-ink's SPI bus and the SAO bus are stand-ins that talk to the window (or, for the SAO
bus, to programs on your laptop). Everything above them, from `main.py` to your app, is
the real thing.

That makes the edit-run loop fast and safe: nothing to copy, nothing to break on a real
badge, and the same tracebacks. It's the place to find **logic** bugs.

What the simulator **can't** tell you:

- **Timing.** Your laptop is far faster. Pure-Python work like LVGL's drawing and PNG
  decoding runs much quicker than on the badge. An app that's fine here can still
  hog the badge (see [[hog-the-cpu]] and [[on-time]]).
- **Memory.** It has a huge heap; the badge doesn't (see [[out-of-memory]]).
- **Real hardware.** WiFi, ESP-NOW and the SAO GPIO pins aren't simulated, and an
  emulated I2C device is only as good as its emulator.
- **LVGL differences.** It's a different build of MicroPython + LVGL from the badge's.
  Most code runs the same, but not all: LVGL's default theme here is the dark one
  (white on black), it has more font sizes than the badge, and a few things the badge's
  LVGL exposes (like `inv_p`) are missing.
- **E-ink realism.** No flashing, no ghosting.
- **Not quite stock firmware.** The branch fixes a few firmware bugs so it can run, and
  sorts the menu into a fixed order (see "Firmware changes" in `SIMULATOR.md`).

And it has no debugger: it's MicroPython, so there's no `breakpoint()` or `pdb`. Use
the habits from [[better-prints]] and [[drive-app]] here too.

<!-- TODO(diagram): your app in the middle; on the badge it talks to real hardware through lib/, in the simulator the same lib/ files talk to stand-ins -->

## Stuck?

| Symptom | Fix |
|---|---|
| `badge-sim: ... lvgl_micropy_unix: not found` | The build didn't finish, or it's somewhere else. Set `LVGL_MICROPY` to the interpreter's path (see `SIMULATOR.md`). |
| `Segmentation fault` when it exits | Harmless: a bug in lvgl_micropython's shutdown. |
| Your app isn't in the menu | Is it in `firmware/badge/apps/`, and does its class inherit from `BaseApp`? Read the start-up messages. |
| The screen is black with white text | That's the simulator's LVGL theme. Set your screen's colors yourself if it matters (`set_style_bg_color`, `set_style_text_color`). |
| It works here but not on the badge | Timing, memory, or an LVGL difference: see "What just happened". |

## Have fun!

- Run your tests from [[unit-tests]] in the simulator's MicroPython instead of CPython:
  `MICROPYPATH=firmware/badge/lib firmware/sim/lvgl_micropython/build/lvgl_micropy_unix tests/test_timer_logic.py`.
- Write an emulated SAO for your sensor (copy `sao_example.py`), and develop
  [[sensor-badge]] without the sensor.
- Make an error happen only on the 50th press, and find it from the traceback alone.
