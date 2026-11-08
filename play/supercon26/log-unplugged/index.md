---
id: log-unplugged
title: "Logs without a laptop: survive an error, keep a crash log, show it on screen"
label: Logs without a laptop
topic: watch
workshop: false
needs: [better-prints]
time: 30 min
touches:
  - apps/base_app.py#BaseApp.arun   # catches errors in run(), prints them, and calls run() again
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

1. **Make an error that happens sometimes.** In `run()`, fail on the 30th call, like a
   sensor that occasionally doesn't answer:

   ```python
       def run(self):
           # ...what your run() already does, then:
           if self.calls == 30:
               raise ValueError("bad sensor read")
   ```

   Save, **Ctrl+D**, and open your app. After three seconds or so, the shell prints
   `{{ facts.firmware.user_app_name }} hit an exception bad sensor read` and a traceback, and then the app carries on.
   The firmware caught it: `arun()` in `apps/base_app.py` wraps every call to `run()`
   in a `try`. That's a safety net, but a coarse one. Everything in `run()` after the
   error was skipped, and the only record is in a shell nobody is watching.

2. **Catch it yourself, log it, carry on.** Wrap just the risky part in `try`/`except`:

   ```python
           try:
               if self.calls == 30:
                   raise ValueError("bad sensor read")
           except Exception as e:
               log.exception("call %d failed, carrying on", self.calls, exc_info=e)
   ```

   `log.exception` logs at `ERROR` level, with the traceback (`exc_info=e` says which
   one). The rest of `run()` still happens.

3. **Send the errors to a file too.** Add a second handler that only takes `ERROR` and
   up, and appends them to a file on the badge. Put this near the top of your file,
   after `basicConfig`:

   ```python
   class CrashFile(logging.Handler):
       """Appends each record to crash.log, and closes the file straight away."""
       def emit(self, record):
           if record.levelno >= self.level:
               with open("crash.log", "a") as f:
                   f.write(self.format(record) + "\n")

   crash_file = CrashFile()
   crash_file.setLevel(logging.ERROR)
   crash_file.setFormatter(logging.Formatter())
   logging.getLogger().addHandler(crash_file)
   ```

   Now everything still goes to the shell, and errors *also* go into `crash.log`.
   (The library has a `FileHandler` too, but it keeps the file open, so what it writes
   may not reach flash before you look, or before the battery runs out.)

4. **Run it unplugged.** Unplug the badge (it's on battery), open your app, and wait a
   minute. Then plug in, press **Ctrl+C**, and read the file:

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
               log.exception("call %d failed, carrying on", self.calls, exc_info=e)
               self.last_error = repr(e)
   ```

   and in `run()`, after the `try`, light the last LED red while `self.last_error` is set
   (not the first: the display uses that one)
   (see [[one-led]]). Clear `self.last_error` (and the LED) when the user presses
   **{{ facts.buttons.app_2_label }}**.

   Or, if your app has a screen (see [[lvgl-hello]]), show it in a label when the app
   opens: `"Oops: ValueError('bad sensor read')"`.

7. Take the error out of `run()`, and delete `crash.log`
   (`import os; os.remove("crash.log")`).

**✅ Done when** an error in your app gets logged to `crash.log` while the badge is
unplugged, the app keeps running, and the badge shows you that something went wrong.

## What just happened

An exception travels up the calls until something catches it. In `run()`, without a
`try` of your own, that's `arun()` in `apps/base_app.py`: it prints the error and calls
you again next time, but the rest of that call is lost. In a task you started yourself
(see [[firmware-diagram]]), nothing catches it, and the task dies. With a `try` of your
own, the error stops right where it happened, and you decide what comes next.

**Catch around the risky part, not around everything.** A sensor read or a web
request can fail for reasons outside your control, and carrying on is the right
answer. A typo in your own code is a bug, and a `try` around the whole method would
log it once a second forever and hide it. Catch narrowly, and log what you caught.

Logging sends each line to every **handler** on the logger. You now have two: the
shell, which takes everything, and a file, which only takes errors. (A handler is a
small class with an `emit()` method, so you can write your own, as you did.) That split is
the point. A file of every tick would fill the flash and wear it out; a file of
errors is short, and it's exactly what you want to read afterwards.

## Stuck?

| Symptom | Fix |
|---|---|
| `crash.log` is empty | The handler's level is above the messages. Check `setLevel(logging.ERROR)` and that you used `log.exception` or `log.error`. |
| `AttributeError: 'NoneType' object has no attribute 'format'` | The handler has no formatter. Add `crash_file.setFormatter(logging.Formatter())`. |
| The error is logged without its traceback | Pass the exception: `log.exception("...", exc_info=e)`. |
| `crash.log` is huge | Your error happens every tick. Fix the bug, or only log the first few. |
| `OSError: 28` | The filesystem is full. Delete old logs; keep step 5. |
| Every line in the file appears twice | The handler was added twice (`__init__` adds it?). Add it once, at the top of the file. |
| `{{ facts.firmware.user_app_name }} hit an exception` still prints | The error is outside your `try`. Read the traceback for the line. |

## Have fun!

- Count errors instead of logging each one, and log a summary every 10 minutes.
- Put the time of day in the crash log (set the clock first: [[ntp-time]]).
- Keep a log of something good, too: how many people your badge met (see [[espnow-nearby]]).
