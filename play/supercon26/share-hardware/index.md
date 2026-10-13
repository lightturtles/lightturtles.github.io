---
id: share-hardware
title: Two apps fight over the LEDs; fix it by sharing one LED object
label: Share the LEDs
tier: developmental
difficulty: 8
group: apps
icon: handshake
needs: [first-app, all-leds]
time: 25 min
touches: [apps/userA.py, apps/userB.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** See what happens when two apps use the same hardware at once, then fix it
so they share properly.

## You need

- Your app from [[first-app]] in `{{ facts.firmware.user_app }}`
- A second user app file, `{{ facts.firmware.user_app_2 }}`. [[backup]] it first.

## Steps

1. **App A: red, on the first LED.** Add to `{{ facts.firmware.user_app }}`:

   ```python
   from machine import Pin
   import neopixel

   class App(BaseApp):
       def __init__(self, name, badge):
           super().__init__(name, badge)
           self.background_sleep_ms = 1000
           self.np = neopixel.NeoPixel(Pin({{ facts.leds.pin }}), {{ facts.leds.count }})
           self.on = False

       def run_background(self):
           self.on = not self.on
           self.np[0] = (32, 0, 0) if self.on else (0, 0, 0)
           self.np.write()
   ```

2. **App B: blue, on the last LED.** Put the same thing in `{{ facts.firmware.user_app_2 }}`, but
   with `self.background_sleep_ms = 700`, `self.np[{{ facts.leds.count }} - 1]`, and
   `(0, 0, 32)`.

3. Save both, **Ctrl+D**, and stay on the menu (both apps run in the background). Watch
   the LEDs. They each blink their own LED, so why do they keep turning each other off?

4. **Find the bug.** Each app made its *own* `NeoPixel` object, so each has its own list
   of {{ facts.leds.count }} colors. App A's list says the last LED is off, and
   `np.write()` sends *the whole list*. Every write undoes the other app's LED.

5. **Fix it: one shared LED object.** Make a new file, `apps/leds.py`:

   ```python
   """The badge's LEDs. Every app imports this instead of making its own."""
   from machine import Pin
   import neopixel

   np = neopixel.NeoPixel(Pin({{ facts.leds.pin }}), {{ facts.leds.count }})
   ```

   In both apps, delete the `self.np = ...` line and use the shared one:

   ```python
   from apps import leds
   # ...and everywhere you had self.np, write leds.np
   ```

6. Save all three files, **Ctrl+D**. Both LEDs blink on their own schedules now.

7. **Write down the rule.** Add a comment at the top of `apps/leds.py`: "LED 0 belongs to
   app A; the last LED belongs to app B." You've just **partitioned** the
   LEDs.

**✅ Done when** both apps blink their own LED without disturbing each other.

## What just happened

The firmware only manages one piece of hardware for you: the **screen**, which belongs
to the foreground app. Everything else is shared on the honor system. Python is happy
to let two apps make two objects for the same pins, and the hardware does whatever it
was told *last*.

You used the two standard fixes together:

- **One object per device.** A module is only loaded once, so every app that imports
  `apps.leds` gets the *same* `np`. Now there's one list of colors, and each write
  includes everyone's changes.
- **A partition.** Each app agreed to touch only its own LEDs. Nothing enforces it.
  It's a rule you wrote down.

Sometimes you can't split the hardware: there's one buzzer, and an I2C transaction
can't be half yours. Then you need an **owner**: one background task that's the only
code allowed to touch the device. Other apps *ask* it (set a variable, or push onto a
queue), and it decides who wins. The same applies to the SAO pins, the I2C bus and WiFi.

<!-- TODO(diagram): before: app A → np(A) ┐ app B → np(B) ┘→ LEDs (conflict). After: app A ┐ app B ┘→ leds.np → LEDs -->

## Stuck?

| Symptom | Fix |
|---|---|
| Only one app's LED blinks at all | Both apps need to be in the background. Go back to the menu. |
| `ImportError: no module named 'apps.leds'` | Is the file at `apps/leds.py` *on the badge*? |
| LEDs still fight | One app still has its own `neopixel.NeoPixel(...)`. Search both files for it. |

<!-- TODO(verify): does the firmware animate the LEDs itself? If so, add a Stuck? row -->

## Have fun!

- **Write an owner.** Give `apps/leds.py` a dict of requests (`{"{{ facts.firmware.user_app_name }}": (32, 0, 0)}`)
  and a background app that shows the *most recent* request on all LEDs. Now apps ask
  instead of write.
- **Priority:** a "notification" app that takes over every LED for 2 seconds, then
  hands them back.
- Do the same for the SAO I2C bus: two apps reading two sensors on one bus.
