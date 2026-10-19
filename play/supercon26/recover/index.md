---
id: recover
title: Rescue a badge you can't get into
label: Boot rescue
topic: setup
workshop: false
needs: [start-fresh, resets]
time: 20 min
touches: [main.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Get back to `>>>` on a badge that drops off USB before you can press
**Ctrl+C**, then stop it from happening again.

## You need

- Your badge, connected (see [[repl]]), and charged: you'll need the battery
- `mpremote` (see [[mount-and-run]])
- A [[backup]]

## First: is this the right lesson?

Most broken badges don't need rescuing. If the badge prints a traceback and stops, or
freezes but answers **Ctrl+C**, you can already get in: see [[break-and-restore]] and
[[hog-the-cpu]]. This lesson is for when the badge **disappears from USB** before you
can type anything:

- code that goes into **deep sleep** at start-up (easy to do by accident in
  [[sleep-with-image]])
- code that calls `machine.reset()` at start-up, so the badge restarts over and over
- a `boot.py` that turns off or reconfigures USB

## Steps

1. **Make a badge that sleeps at boot** (so you can practice the rescue). In
   `{{ facts.firmware.user_app }}`, add these as the very first lines and save:

   ```python
   import machine, time
   time.sleep(3)                 # your window to get in
   machine.deepsleep(15_000)     # sleep 15 s, then start over
   ```

   Press **{{ facts.power.reset_button }}**. The badge starts, goes to sleep, the USB port
   vanishes, and 15 seconds later it all happens again. Thonny can't keep up.

2. **Catch it in the window.** Close Thonny. In a terminal, run a command over and over
   until one gets through:

   ```bash
   until mpremote exec "import os; os.rename('main.py', 'main_off.py')"; do sleep 0.2; done
   ```

   Each try fails until the port comes back. Then `mpremote` connects, interrupts the
   badge, and renames `main.py` before your sleep line runs again.

   <!-- TODO(verify): on Windows, use a PowerShell loop; and whether mpremote reconnects fast enough inside a 3 s window -->

3. **Check it worked.** Press **{{ facts.power.reset_button }}**. The badge boots straight to
   `>>>`, with no menu and no apps, and you have all the time you want. (It's the same
   blank badge you met in [[resets]], but this time it stays that way.)

4. **Fix the real problem.** Remove the lines from step 1 (or put the file back from
   your backup or the folder, as in [[break-and-restore]]).

5. **Put `main.py` back** and restart:

   ```bash
   mpremote exec "import os; os.rename('main_off.py', 'main.py')" + reset
   ```

**✅ Done when** you've rescued a badge that sleeps at boot, without help.

## What just happened

At every reset, MicroPython runs `boot.py`, then `main.py` (see [[resets]]). If
something in that chain turns off USB (by sleeping, resetting, or reconfiguring it),
there's never a moment when your laptop is connected *and* the badge is listening.
**Ctrl+C** can't help, because nothing hears it.

The rescue is to **make that moment**, or find a longer one:

- **Race it.** Most start-up code takes a moment before it does the damage. A loop that
  retries `mpremote` the instant the port appears will usually win.
- **Wake it.** A sleeping badge can be woken by its wake button
  ({{ facts.sleep.wake_label }}), or the reset button, which restarts the race.
{% if facts.firmware.safe_mode %}- **Safe mode.** This badge has one: {{ facts.firmware.safe_mode }}. It skips the apps for you.
{% endif %}
Renaming `main.py` turns a race you have to win every time into one you only have to
win once.

If none of that works, the files can always be wiped and replaced from the official
folder (see [[start-fresh]]), as long as the badge can be reached at all. Your
[[backup]] gets your work back.

<!-- TODO(diagram): power on → boot.py → main.py → deep sleep → (15 s) → power on…; the short window before sleep where mpremote gets in -->

## Stuck?

| Symptom | Fix |
|---|---|
| `mpremote` never gets through | Make the window longer: hold the badge in reset, release it, and start the loop at once. Or use the wake button. |
| `could not enter raw repl` | It got the port but not the prompt. Keep the loop running; the next try usually works. |
| The port never appears at all | Plug into a different USB port or cable; try {{ facts.power.reset_button }} while plugged in. |
| Nothing works, ever | Ask a helper. They can reflash MicroPython, and your [[backup]] gets your work back. |

## Have fun!

Add a guard to the top of `main.py`: if a button is held at startup (see
[[read-button]]), `raise SystemExit` before any app is imported. You've just invented
safe mode. (Back up `main.py` first, and test the guard *before* you need it.)
