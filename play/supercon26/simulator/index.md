---
id: simulator
title: "Run your app in the simulator, with a real debugger"
label: Run it in the simulator
topic: advanced
workshop: false
needs: [drive-app]
time: 30 min
touches: [apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(simulator): this page is written ahead of the simulator. Every command, file
     name and key binding below is a placeholder; replace them once it exists. -->

**Goal:** Run your app on your laptop instead of the badge, stop it on any line, and
look at every variable, including the local ones the badge can never show you.

## You need

- Python 3 on your laptop, and your project folder from [[mount-and-run]]
- Your app from [[first-app]], already split up for testing as in [[drive-app]]
- The badge simulator <!-- TODO(simulator): where to get it, how to install it -->

## Steps

1. **Run your app in the simulator.** From your project folder:

   ```bash
   python sim.py {{ facts.firmware.user_app }}      # TODO(simulator): real command
   ```

   A window shows the badge's screen and LEDs. Your app is on the menu, just like on
   the badge. The keyboard stands in for the buttons.

   <!-- TODO(simulator): which keys are which buttons; screenshot of the window -->

2. **Use it like the badge.** Open your app, press its buttons, go home. The `print`
   and `log` lines from [[better-prints]] come out in your terminal.

3. **Stop on a line.** Add one line where you want to look, in `run_foreground()`:

   ```python
           breakpoint()
   ```

   Run the simulator again and open your app. Everything stops, and your terminal shows
   `(Pdb)`: Python's debugger, waiting for you.

4. **Look around.** At `(Pdb)`, type:

   ```
   p self.ticks         # print one value
   pp self.__dict__     # everything in your app, laid out neatly
   locals()             # every local variable in this method: the badge can't do this
   where                # how you got here: the traceback, without a crash
   ```

5. **Step through it.**

   ```
   n                    # next line
   s                    # step into a call
   c                    # continue until the next breakpoint
   ```

   Change a value and carry on: `self.ticks = 99`, then `c`.

6. **Stop where it crashes.** Take the `breakpoint()` out, put back the error from
   [[post-mortem]] (`1 / 0` on a button), and run the simulator under the debugger:

   ```bash
   python -m pdb sim.py {{ facts.firmware.user_app }}     # TODO(simulator): real command
   ```

   Type `c` to start it. When the error happens, the debugger stops *in the line that
   failed*, with every local variable still there. Compare that with what you could see
   in [[post-mortem]].

   <!-- TODO(simulator): if the simulator catches task exceptions itself, document its own "stop on error" switch instead -->

7. **Or use your editor.** VS Code (and most editors) can run the same thing with
   breakpoints you click in the margin, and a panel that shows every variable.

   <!-- TODO(simulator): a launch.json for VS Code -->

8. **Check it on the badge.** When it works in the simulator, copy it to the badge
   (see [[mount-and-run]]) and try it for real.

**✅ Done when** you've stopped your app on a line in the simulator, read a local
variable, and stepped to the next line.

## What just happened

The simulator runs your app in **CPython**, the Python on your laptop, with stand-ins
for the badge's hardware: a window for the screen and LEDs, keys for the buttons. Your
app's code doesn't change. It still calls `self.badge.display` and `self.badge.leds`;
they just lead somewhere else.

That buys you the one thing MicroPython can't do: a **debugger**. Python on a laptop
keeps every call's local variables around, so it can stop anywhere and show you all of
them. On the badge, you saw only what survived in objects (see [[post-mortem]]).

What the simulator **can't** tell you:

- **Timing.** Your laptop is far faster. An app that's fine here can still hog the
  badge (see [[hog-the-cpu]] and [[on-time]]).
- **Memory.** Your laptop has gigabytes; the badge doesn't (see [[out-of-memory]]).
- **Real hardware.** A sensor that answers in the simulator may not on the I2C bus.
- **MicroPython's differences.** A few things that work in CPython don't on the badge.

So: find the *logic* bugs here, where it's easy, and the *timing and hardware* bugs on
the badge.

<!-- TODO(diagram): your app in the middle; on the badge it talks to real hardware through badge_obj, in the simulator to stand-ins -->

## Stuck?

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: machine` (or `lvgl`) | You ran your app directly. Run it through the simulator, which provides those. |
| `(Pdb)` never appears | The line with `breakpoint()` never ran. Is it in the method you think? |
| The simulator freezes at `(Pdb)` | That's the debugger waiting for you. Type `c`. |
| It works here but not on the badge | Timing, memory, or a MicroPython difference: see "What just happened". |

<!-- TODO(simulator): real problems people hit -->

## Have fun!

- Put a breakpoint in `run_background()` and watch how often it really runs.
- Make an error happen only on the 50th press, then use the debugger to find it.
- Run your tests from [[unit-tests]] against the simulator.
