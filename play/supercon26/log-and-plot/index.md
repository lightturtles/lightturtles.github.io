---
id: log-and-plot
title: Save the badge's output and plot it (Thonny's Plotter, CSV)
label: Plot it
topic: watch
workshop: false
needs: [better-prints]
time: 25 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Watch a number change as a live graph, and save the badge's output to a file
on your laptop for later.

## You need

- Thonny, connected to the badge (see [[repl]])
- Something that changes: your sensor (see [[real-units]]), free memory, or a button

## Steps

1. **Print numbers the Plotter can read.** At `>>>` (**Ctrl+C** first), print one line
   of `name: value` pairs, over and over:

   ```python
   import time, gc
   for i in range(300):
       print(f"mem_kB: {gc.mem_free() // 1024}  i: {i % 50}")
       time.sleep(0.1)
   ```

2. **Open the Plotter.** **View → Plotter**. It draws each number as a line, live, with
   the names as a legend. Watch the sawtooth: that's `i % 50`.

   <!-- TODO(screenshot): Thonny Plotter with two lines and the legend -->

3. **Plot something real.** Swap in your sensor reading and hold the sensor in your
   fingers. Or `btn.value()` from [[read-button]], and press it.

4. **Save the output.** From the command line, `mpremote` can copy everything the
   badge prints into a file:

   ```bash
   mpremote repl --capture log.txt
   ```

   Let the badge run (press **Ctrl+D** to restart it, if you like), then **Ctrl+]** to
   stop. `log.txt` has everything.

5. **Print CSV for spreadsheets.** For data you'll keep, print comma-separated lines
   with a time column:

   ```python
   t0 = time.ticks_ms()
   print("t_s,mem_kB")
   for i in range(100):
       print(f"{time.ticks_diff(time.ticks_ms(), t0) / 1000:.1f},{gc.mem_free() // 1024}")
       time.sleep(0.5)
   ```

   Capture it as in step 4, delete any lines that aren't data, rename it `log.csv`,
   and open it in a spreadsheet. Insert a chart.

6. **Or plot it in Python** on your laptop:

   ```python
   import csv, matplotlib.pyplot as plt
   rows = list(csv.DictReader(open("log.csv")))
   plt.plot([float(r["t_s"]) for r in rows], [float(r["mem_kB"]) for r in rows])
   plt.xlabel("seconds"); plt.ylabel("free kB"); plt.show()
   ```

**✅ Done when** you've watched a value change live in the Plotter, and you have a saved
log you can open on your laptop.

## What just happened

The Plotter watches the shell for lines that contain numbers. Words become the names
of the lines, and each number is the next point. Your code doesn't need to know
there's a graph: it just prints.

A graph shows things a column of numbers hides: a slow leak (memory that only goes
down), noise (a sensor that jitters), a stutter (a gap in the timestamps), or a
pattern you'd never spot by reading.

Saving the output turns a debugging session into **data** you can compare later:
before and after a fix, today and tomorrow, your badge and a friend's.

## Stuck?

| Symptom | Fix |
|---|---|
| The Plotter is empty | Your lines need numbers. Lines with only words are ignored. |
| Lines jump to zero | Something printed a line with different names. Print only your data while plotting. |
| Log lines from [[better-prints]] get plotted too | Their timestamps are numbers. Raise the log level (`logging.WARNING`) while you plot. |
| `--capture` isn't recognized | Update mpremote: `pipx upgrade mpremote`. Or copy the shell's text from Thonny. |
| The spreadsheet puts everything in one column | Check the separator: it should be a comma, with no spaces. |

## Have fun!

- Log your sensor for an hour while you're in a talk, then plot it. When did the room
  warm up?
- Log the gap between your app's calls (see [[on-time]]) while you use the badge. What
  makes the spikes?
- Log on the badge itself, to a file, while it's unplugged, then copy the file over
  (see [[log-unplugged]]).
