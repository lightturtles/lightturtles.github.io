---
id: better-prints
title: "Print and log: tags, levels, timestamps, and printing on change"
label: Print and log
topic: watch
workshop: false
needs: [first-app]
time: 25 min
touches: [apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Turn a shell full of noise into a log you can read: who printed it, when, how
important it is, and only when something changed.

## You need

- Your app from [[first-app]]
- `mpremote` (see [[mount-and-run]]), to install a library

## Steps

1. **Make some noise.** Add `print(self.ticks)` to `run_foreground()`, save, **Ctrl+D**,
   and open your app. The shell scrolls too fast to read, and you can't tell your
   lines from the badge's.

2. **Tag every line** with who printed it, and print `name=value`, not a bare number:

   ```python
   print(f"[{self.name}] ticks={self.ticks}")
   ```

   That's the whole idea behind logging. The next steps just make it easier.

3. **Get the `logging` library.** First check whether the badge already has it:

   ```python
   import logging
   ```

   If that's an `ImportError`, install it from your laptop. The badge doesn't need WiFi:

   ```bash
   mpremote mip install logging
   ```

   It lands in `{{ facts.firmware.lib_dir }}/` on the badge.

   <!-- TODO(verify): whether this year's firmware includes logging already -->

4. **Log instead of printing.** At the top of your app's file:

   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   log = logging.getLogger("{{ facts.firmware.user_app_name }}")
   ```

   And in your methods:

   ```python
           log.debug("ticks=%d", self.ticks)            # detail you only want sometimes
           log.info("button pressed")                    # normal events
           log.warning("sensor read took %d ms", ms)    # odd, but not broken
           log.error("no reply from the sensor")         # broken
   ```

   Save, **Ctrl+D**. Each line now says how important it is and who said it:
   `DEBUG:{{ facts.firmware.user_app_name }}:ticks=4`.

5. **Turn it down without deleting anything.** The level is the volume knob. Change
   `DEBUG` to `INFO` and the `debug` lines disappear; the rest stay. Before your demo,
   set it to `WARNING`. Leave the `log` calls where they are.

6. **Add a timestamp,** relative to start-up, so you can see *when* and how far apart:

   ```python
   import time

   class Since(logging.Formatter):
       def format(self, record):
           t = time.ticks_ms() / 1000
           return f"{t:8.3f} {record.levelname:7} [{record.name}] {record.message}"

   logging.basicConfig(level=logging.DEBUG)
   logging.getLogger().handlers[0].setFormatter(Since())
   ```

   Read two lines' times and you know how long passed between them. (The library can
   also print `%(asctime)s`, the time of day, but the badge's clock says the year 2000
   until something sets it: see [[ntp-time]].)

   <!-- TODO(verify): micropython-lib logging's LogRecord attributes (record.message) and handler setup -->

7. **Log on change, not every call.** Most values don't change most of the time. Put
   this in `{{ facts.firmware.lib_dir }}/watch.py`:

   ```python
   _seen = {}

   def watch(name, value, out=print):
       r = repr(value)
       if _seen.get(name) != r:
           _seen[name] = r
           out(f"{name} = {r}")
   ```

   Then in your app:

   ```python
   from watch import watch
   ...
           watch("userA.state", self.state, log.info)
   ```

   The first call always logs, so you see the starting value. After that, one line per
   change, instead of fifty per second. Because it compares `repr()`s, a list that
   changes in place still counts as a change.

8. **Measure what printing costs.** Time 100 prints:

   ```python
   t0 = time.ticks_us()
   for i in range(100):
       print("x" * 40)
   time.ticks_diff(time.ticks_us(), t0) // 100      # µs per print
   ```

   That's time your app isn't returning (see [[on-time]]).

**✅ Done when** your log shows tagged, timestamped lines at the right level, and a
watched value logs only when it changes.

## What just happened

A log line is a message to your future self. Four things make it useful: **who** (the
logger's name), **how important** (the level), **when** (the timestamp), and **what
changed** (`name = value`, on change). Without them, a log is a wall of numbers.

`logging` is the same library as on a laptop, cut down to fit. Learning it here means
you already know it in desktop Python, and anyone reading your code knows what
`log.warning` means. It costs a little RAM, and a call below the current level costs
almost nothing: the message is never built.

Printing isn't free. Every character goes down the USB serial line, and if the laptop
is slow to read, `print` waits. Print in a tight loop and you can *create* the
stutter you're trying to find. Logging on change and turning the level down keep the
cost low and the log short.

Unplugged, the log goes nowhere. To keep a record without a laptop, see
[[log-unplugged]]. To turn a log into a graph, see [[log-and-plot]].

## Stuck?

| Symptom | Fix |
|---|---|
| `ImportError: no module named 'logging'` | Step 3. Check the file is in `{{ facts.firmware.lib_dir }}/` on the badge. |
| Nothing logs at all | The level is too high. `basicConfig(level=logging.DEBUG)`. |
| Every line prints twice | `basicConfig` ran twice and added two handlers. Call it in one place only. |
| `watch` logs every call | The value really is different each time (a timestamp in it?). Watch something simpler, like a count or a state. |
| The badge got slower | Too many log lines. Log on change, or raise the level. |

## Have fun!

- Give each part of your app its own logger (`logging.getLogger("userA.sensor")`) and
  turn just one of them up.
- Use `watch` to print a state machine's transitions: `watch("state", self.state)` (see [[fsm]]).
- Log how long each `run_foreground()` takes, but only when it's over 10 ms (see [[on-time]]).
