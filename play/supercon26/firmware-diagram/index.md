---
id: firmware-diagram
title: "How apps run: main.py, the menu, and the life of an app"
label: How apps run
topic: write-app
workshop: false
needs: [map-firmware]
time: 30 min
touches:
  - main.py#main                      # creates the four firmware tasks, then the 60 s heartbeat
  - lib/app_switcher.py#AppSwitcher   # finds the apps at import; arun() is the menu and runs the open app
  - apps/base_app.py#BaseApp.arun     # calls run(), catches its exceptions, sleeps sleep_ms
  - apps/template.py
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Sketch how the badge's apps fit together (what `main.py` starts, what runs at
the same time, how an app reaches the hardware), then follow one app through its life
and learn the rules every app has to follow.

## You need

- Paper and a pen (this works best by hand)
- The official folder on your laptop (see [[map-firmware]]), open in a text editor

## Steps

1. **Start at `main.py`.** It's what runs when the badge starts up. (Something runs
   before it; that's in [[resets]].) Skim it before you draw anything. Don't change it.
   Look for:
   - the `import` lines near the top. Each `from lib.… import …` points at a file in `lib/`.
   - `async def main()`, and the `while True` loop at its bottom. That loop runs
     forever (it prints `Main 60s heartbeat` and a memory report once a minute), and
     it's why **Ctrl+C** is needed to get to `>>>`.

2. **Find what gets made at import.** Each `lib/` module makes its piece of hardware the
   moment it's imported, as a module-level object. Draw a box for each one under
   `main.py`, with an arrow labeled *imports*:
   - `switcher` (`lib/app_switcher.py`, the last line): the menu, and the list of apps
   - `display` (`lib/epd.py`): the e-ink screen, and LVGL
   - `leds` (`lib/led_bar.py`): the row of {{ facts.leds.count }} LEDs
   - `UserA`, `UserB`, `MenuPlus`, `MenuMinus`, `Boot` (`lib/button.py`)

3. **Find where the apps come from.** Open `lib/app_switcher.py` and read
   `AppSwitcher.__init__`. It lists every `.py` file in `/apps`, imports them all, and
   makes **one object of every class that inherits from `BaseApp`**. (It skips
   `base_app` and `template`.) Draw a box for each app the switcher makes: Workshops,
   Sat Talks, Sun Talks (all three are in `apps/schedule.py`), Gallery and Nametag.

4. **Find what runs at the same time.** Back in `main()`, find the four
   `aio.create_task(...)` lines. Each one starts a **task** (see [[asyncio-basics]]).
   Draw a dashed outline around each:
   - `button_scan()`: reads all five buttons, every millisecond
   - `display.run()`: waits for an app to ask for a refresh, then sends the picture to the e-ink
   - `leds.update()`: plays LED animations, if anyone set one
   - `switcher.arun()`: the menu, *and* the open app
   - and `main()` itself, with its heartbeat

   Notice what's *not* there: the apps don't get tasks of their own.

5. **Follow the switcher's loop.** Read `AppSwitcher.arun()`. It's in one of two modes:
   - **Selecting** (the menu): it shows your place on the LEDs, moves on **Menu +/−**,
     and opens the selected app on **User A** or **User B**. It sets that app's
     `launched = True`.
   - **Running an app**: each time round, it checks **Menu +/−** (to go back to the
     menu), then does `await self.apps[self.active_idx].arun()`, then sets `launched`
     back to `False`.

   So **only the open app runs**. Every other app is just an object, waiting.

6. **Follow one app through its life.** Open `apps/base_app.py` and `{{ facts.firmware.template_app }}`.
   Fill in the table under "What just happened" as you go: who calls each method,
   and when?

7. **Find how an app reaches the hardware.** Open `{{ facts.name_badge.file }}`. Look at its
   `import` lines: `from lib.epd import display`, `from lib.led_bar import leds`, and
   so on. Each is an arrow from the app straight to a hardware box. There's no object in
   between: an app imports what it needs.

8. **Mark what's yours.** Shade the boxes for files you're meant to edit
   ({{ facts.firmware.user_apps }}). Everything else, you *can* edit, but [[backup]] first.

**✅ Done when** you can point at your drawing and answer: which code decides what's on
the screen? How does your app reach the LEDs? How many tasks take turns on the
processor? And what runs while you're looking at the menu?

## What just happened

The firmware is built in layers:

| Layer | What it is | Files |
|---|---|---|
| Start-up | Runs once, when the badge starts | `boot.py`, `main.py` |
| Scheduler | Takes turns between tasks | `asyncio` (built into MicroPython) |
| Apps | The menu's apps, *your* apps | `apps/` |
| Hardware modules | One module per device, each with ready-made objects | `lib/` |
| MicroPython + drivers | Talk to the chip's pins | Built into the firmware (C) |

Each app talks *down* the stack, by importing from `lib/`. Apps don't call each other.
The dashed outlines matter most: one processor, five tasks, taking turns (see
[[asyncio-basics]]). Your app runs *inside* one of them, the switcher's.

### The life of an app

| What | Called by | When |
|---|---|---|
| `__init__(self)` | `AppSwitcher.__init__` | once, at start-up, when `main.py` imports `lib.app_switcher`. It gets no arguments. |
| `self.launched = True` | the switcher | when you open the app from the menu |
| `arun()` | the switcher's loop | over and over, while the app is open. It calls `run()`, then sleeps `self.sleep_ms` (100 ms unless you change it). |
| `run()` | `arun()` | each time round. On the first call after you open the app, `self.launched` is `True`; after that, `False`. |
| *(leaving)* | nobody | When you press **{{ facts.buttons.home_label }}**, the switcher just stops calling your app. No method of yours runs. |

So `run()` is where your app does everything. Use `if self.launched:` for "just
opened: draw the screen", and the rest of `run()` for "still open: check the buttons."

One more thing `arun()` does: it wraps `run()` in `try`/`except`. If your `run()`
raises an error, the traceback is printed, and `run()` is called again 100 ms later.
A broken app prints the same error over and over instead of crashing the badge.

### Work that keeps going after you leave

Only the open app runs, so an app that should keep working from the menu (a timer that
counts down on the LEDs, a logger that reads a sensor every minute, a listener for
messages from other badges) starts **its own task** the first time it's opened:

```python
import asyncio

    def run(self):
        if self.launched and self.task is None:   # self.task = None in __init__
            self.task = asyncio.create_task(self.keep_going())
```

That task keeps running whatever's open, until the badge restarts. It follows the
same rules as everything else (below), plus: no screen, and the slowest period that
works. The LEDs are tricky too: the menu redraws all of them every 10 ms while it's
showing (see [[share-hardware]]).

### The rules every app follows

1. **Return quickly.** `run()` does one small thing and returns. A few milliseconds per
   call (see [[on-time]]).
2. **Never wait inside a call.** No `time.sleep()`, no `while` loop waiting for a button
   or a network reply. Every other task is frozen until you return (see [[hog-the-cpu]]).
3. **Keep what you need for next time in `self`.** Locals vanish when you return (see [[fsm]]).
4. **Don't ask to be called too often.** Every call costs every other task a little time.
   Pick the slowest `self.sleep_ms` that works. (Too slow and you'll miss short button
   taps: a press only counts if `run()` checks it before the button is let go.)
5. **Only the open app draws on the screen.**
6. **Share the rest.** LEDs, SAO pins and the I2C bus are shared on the honor system
   (see [[share-hardware]]).
7. **Let the user leave.** The switcher handles **{{ facts.buttons.home_label }}** for you, but only between
   calls to your app. If `run()` never returns, nobody can leave.

<!-- TODO(diagram): reference block diagram. Top: main.py. Middle (dashed "tasks"): button_scan, display.run, leds.update, switcher.arun (containing the open app's arun → run), main heartbeat. Left: the app objects (Workshops, Sat Talks, Sun Talks, Gallery, Nametag, yours). Bottom: display, buttons, LEDs, SAO I2C. Arrows: imports / creates / runs / uses. -->
<!-- TODO(diagram): app life: created → (menu: idle) → opened (launched=True, first run) → open (run every sleep_ms) → back to menu (no call) -->

## Stuck?

| Symptom | Fix |
|---|---|
| Lost in a long file | Search for `import`, `def ` and `class ` first; skip everything else. |
| Can't tell what an object is | Find its `import` line at the top of the file. That's the file it comes from. |
| Too many boxes | Leave out the apps you don't care about. One app box plus "…and more" is fine. |
| Can't find who calls a method | Search every file in `lib/` and `apps/` for its name. The switcher calls most of them. |
| Two `base_app.py` files | `apps/base_app.py` and `lib/base_app.py` are nearly the same. The switcher uses the one in `apps/`, so your app should too. |

## Have fun!

- From the REPL, after **Ctrl+C**: `from lib.app_switcher import switcher`, then
  `[a.name for a in switcher.apps]`. Does it match your drawing? Which one is open?
  Try `switcher.active_idx` and `switcher.selecting_mode`.
- Open `/data/user_apps.py` on the badge. Who wrote it, and when?
- A focus timer that keeps running from the menu: 25 minutes of work, with one more LED lit
  green as each part passes, then 5 minutes of break in blue. Opening the app starts or
  stops its task (see [[fsm]], [[on-time]] and [[all-leds]]).
