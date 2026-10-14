---
id: better-prints
title: "Better print debugging: tags, timestamps, and printing on change"
label: Better print debugging
topic: debugging
workshop: false
needs: [first-app]
time: 20 min
touches: [apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Turn a shell full of noise into a log you can read: who printed it, when, and
only when something changed.

## You need

- Your app from [[first-app]]

## Steps

1. **Make some noise.** Add `print(self.ticks)` to `run_foreground()`, save, **Ctrl+D**,
   and open your app. The shell scrolls too fast to read, and you can't tell your
   lines from the badge's.

2. **Tag every line** with who printed it. You've been doing this already:

   ```python
   print(f"[{self.name}] ticks={self.ticks}")
   ```

   `name=value` beats a bare number: you'll know what it was a week from now.

3. **Add a timestamp,** relative to startup, so you can see *when* and how far apart:

   ```python
   import time      # at the top

   T0 = time.ticks_ms()
   def log(tag, *args):
       t = time.ticks_diff(time.ticks_ms(), T0) / 1000
       print(f"{t:8.3f} [{tag}]", *args)
   ```

   Now use `log(self.name, "ticks", self.ticks)` everywhere. Read two lines' times and
   you know how long passed between them.

4. **Print on change, not every call.** Most values don't change most of the time:

   ```python
       def watch(self, name, value):
           last = self.__dict__.setdefault("_seen", {})
           if last.get(name) != value:
               last[name] = value
               log(self.name, f"{name}={value}")
   ```

   In `run_foreground()`: `self.watch("state", self.state)`. One line per change,
   instead of fifty per second.

5. **A switch to turn it off.** At the top of the file:

   ```python
   DEBUG = True
   def log(tag, *args):
       if not DEBUG:
           return
       # ...as before
   ```

   Set `DEBUG = False` for your demo; leave the `log` calls where they are.

6. **Measure what printing costs.** Time 100 prints:

   ```python
   t0 = time.ticks_us()
   for i in range(100):
       print("x" * 40)
   time.ticks_diff(time.ticks_us(), t0) // 100      # µs per print
   ```

   That's time your app isn't returning (see [[on-time]]).

**✅ Done when** your log shows tagged, timestamped lines, only when something changes.

## What just happened

A print is a message to your future self. Three things make it useful: **who** (the
tag), **when** (the timestamp), and **what changed** (name=value, on change). Without
them, a log is a wall of numbers.

Printing isn't free. Every character goes down the USB serial line, and if the laptop
is slow to read, `print` waits. Print in a tight loop and you can *create* the
stutter you're trying to find. Printing on change keeps the cost low and the log short.

Unplugged, the prints go nowhere. To keep a record without a laptop, write to a file
instead (the crash log in [[post-mortem]]), or save the output on your laptop and plot
it ([[log-and-plot]]).

## Stuck?

| Symptom | Fix |
|---|---|
| `NameError: log` | Define it at the top of the file, outside the class. |
| `watch` prints every call | The value is a new object each time (a list?). Compare something simpler, like its length. |
| Timestamps jump backwards | You defined `T0` twice (two files?). Keep `log` in one module in `{{ facts.firmware.lib_dir }}/` and import it. |
| The badge got slower | Too many prints. Print on change, or turn `DEBUG` off. |

## Have fun!

- Add levels: `log.info()`, `log.warn()`, with `DEBUG` hiding only `info`.
- Put `log` in `{{ facts.firmware.lib_dir }}/log.py` and use it from every app.
- Print a state machine's transitions: `self.watch("state", self.state)` (see [[fsm]]).
