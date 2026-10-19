---
id: log-unplugged
title: "Logs without a laptop: survive an error, keep a crash log, show it on screen"
label: Logs without a laptop
topic: watch
workshop: false
needs: [better-prints]
time: 30 min
touches: [apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Your badge spends the conference on your lanyard, not on a USB cable. Make
your app carry on after an error, write down what went wrong in a file, and tell you
about it on the badge itself.

## You need

- Your app from [[first-app]], logging as in [[better-prints]]
- A [[backup]]

## Steps

1. **Make an error that happens sometimes.** In `run_background()`, fail on the third
   tick, like a sensor that occasionally doesn't answer:

   ```python
       def run_background(self):
           self.ticks += 1
           if self.ticks == 3:
               raise ValueError("bad sensor read")
   ```

   Save, **Ctrl+D**. After tick 3 the traceback prints and the ticks stop: the error
   killed your app's task (see [[post-mortem]]).

2. **Catch it, log it, carry on.** Wrap just the risky part in `try`/`except`:

   ```python
       def run_background(self):
           self.ticks += 1
           try:
               if self.ticks == 3:
                   raise ValueError("bad sensor read")
           except Exception as e:
               log.exception("tick %d failed, carrying on", self.ticks)
   ```

   `log.exception` logs at `ERROR` level, with the traceback. Tick 3 logs an error,
   and tick 4 happens anyway.

   <!-- TODO(verify): micropython-lib logging has Logger.exception (else: log.error(...) and sys.print_exception(e)) -->

3. **Send the errors to a file too.** Add a second handler that only takes `ERROR` and
   up, and writes to the badge's filesystem:

   ```python
   crash_file = logging.FileHandler("crash.log")
   crash_file.setLevel(logging.ERROR)
   logging.getLogger().addHandler(crash_file)
   ```

   Now everything still goes to the shell, and errors *also* go into `crash.log`.

   <!-- TODO(verify): micropython-lib logging has FileHandler, and handlers honor setLevel -->

4. **Run it unplugged.** Unplug the badge (it's on battery) for a minute, then plug in
   and read the file:

   ```python
   print(open("crash.log").read())
   ```

   Or copy it to your laptop: `mpremote cp :crash.log .`

5. **Keep it small.** Flash is small, and wears out if you write to it constantly. Log
   errors, not every tick, and start a fresh file when it gets big. At the top of your
   file, before adding the handler:

   ```python
   import os

   try:
       if os.stat("crash.log")[6] > 20_000:         # bytes
           os.rename("crash.log", "crash.old.log")  # keep one old file, lose the oldest
   except OSError:
       pass                                         # no log yet
   ```

6. **Show it on the badge.** No laptop, no shell: put the error where you can see it.
   With LEDs, light one red while there's an unread error:

   ```python
           except Exception as e:
               log.exception("tick %d failed, carrying on", self.ticks)
               self.last_error = repr(e)
   ```

   and in `run_background()`, after the `try`, set an LED from `self.last_error` (see
   [[one-led]]). Clear `self.last_error` when the user opens the app.

   Or, if your app has a screen (see [[lvgl-hello]]), show it in a label when the app
   opens: `"Oops: ValueError('bad sensor read')"`.

7. Take the error out of `run_background()`, and delete `crash.log`
   (`import os; os.remove("crash.log")`).

**✅ Done when** an error in your app gets logged to `crash.log` while the badge is
unplugged, the app keeps running, and the badge shows you that something went wrong.

## What just happened

An exception travels up the calls until something catches it. Without a `try`, that's
asyncio, and your task dies. With one, the error stops in your own code, and your task
lives on.

**Catch around the risky part, not around everything.** A sensor read or a web
request can fail for reasons outside your control, and carrying on is the right
answer. A typo in your own code is a bug, and a `try` around the whole method would
log it once a second forever and hide it. Catch narrowly, and log what you caught.

Logging sends each line to every **handler** on the logger. You now have two: the
shell, which takes everything, and a file, which only takes errors. That split is
the point. A file of every tick would fill the flash and wear it out; a file of
errors is short, and it's exactly what you want to read afterwards.

## Stuck?

| Symptom | Fix |
|---|---|
| `crash.log` is empty | The handler's level is above the messages. Check `setLevel(logging.ERROR)` and that you used `log.exception` or `log.error`. |
| `crash.log` is huge | Your error happens every tick. Fix the bug, or only log the first few. |
| `OSError: 28` | The filesystem is full. Delete old logs; keep step 5. |
| Every line in the file appears twice | The handler was added twice (the module was imported twice, or `__init__` adds it). Add it once, at the top of the file. |
| The app still dies | The error is outside your `try`. Read the traceback for the line. |

## Have fun!

- Count errors instead of logging each one, and log a summary every 10 minutes.
- Put the time of day in the crash log (set the clock first: [[ntp-time]]).
- Keep a log of something good, too: how many people your badge met (see [[espnow-nearby]]).
