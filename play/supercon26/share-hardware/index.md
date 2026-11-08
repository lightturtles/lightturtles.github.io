---
id: share-hardware
title: Two apps fight over the LEDs; fix it by sharing one LED object
label: Share the LEDs
topic: write-app
workshop: false
needs: [first-app, all-leds]
time: 25 min
touches:
  - lib/led_bar.py#leds                    # the firmware's one shared LED object
  - lib/led_bar.py#LedBar.menu_display     # the menu redraws every LED every 10 ms
  - lib/app_switcher.py#AppSwitcher.arun   # opening an app turns all the LEDs off
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** See what happens when two pieces of code use the same hardware at once, then
fix it so they share properly.

## You need

- Your app from [[first-app]] in `{{ facts.firmware.user_app }}` (you're about to replace it)
- The "work that keeps going after you leave" idea from [[firmware-diagram]]

## Steps

Only one app is open at a time, so two apps' `run()` methods never collide. But an app
can start a task that keeps running after you leave it, and then they can.

1. **App A: red, on the first LED.** Replace `{{ facts.firmware.user_app }}` with:

   ```python
   """Blinks LED 0 red, from a task that keeps going after you leave the app."""

   import asyncio
   from machine import Pin
   import neopixel

   from apps.base_app import BaseApp


   class MyApp(BaseApp):
       def __init__(self):
           super().__init__("{{ facts.firmware.user_app_name }}")
           self.np = neopixel.NeoPixel(Pin({{ facts.leds.pin }}), {{ facts.leds.count }})
           self.task = None

       def run(self):
           if self.launched and self.task is None:
               self.task = asyncio.create_task(self.blink())
               print(f"[{self.name}] blinking")

       async def blink(self):
           on = False
           while True:
               on = not on
               self.np[0] = (32, 0, 0) if on else (0, 0, 0)
               self.np.write()
               await asyncio.sleep_ms(1000)
   ```

2. **App B: blue, on the last LED.** Save a copy as `{{ facts.firmware.user_app_2 }}`, and change
   four things: the class name (`MyApp2`), the name (`"{{ facts.firmware.user_app_name }} 2"`), the LED
   and color (`self.np[{{ facts.leds.count }} - 1] = (0, 0, 32)`), and the period (`700`).

3. Save both, **Ctrl+D**. Open **{{ facts.firmware.user_app_name }}** from the menu: the red LED blinks. Go back
   to the menu, open **{{ facts.firmware.user_app_name }} 2**, and stay there. Both tasks are running now.
   Watch the LEDs. They each blink their own LED, so why are they never on together?

4. **Find the bug.** Each app made its *own* `NeoPixel` object, so each has its own list
   of {{ facts.leds.count }} colors. App A's list says the last LED is off, and
   `np.write()` sends *the whole list*. Every write undoes the other app's LED.

5. **Fix it: use the one shared LED object.** The firmware already made one:
   `leds`, in `lib/led_bar.py`. In both apps, delete the `from machine import Pin`,
   `import neopixel` and `self.np = ...` lines, and use the shared one:

   ```python
   from lib.led_bar import leds
   # ...and everywhere you had self.np, write leds
   ```

6. Save both files, **Ctrl+D**, and open both apps again as in step 3. Both LEDs blink on
   their own schedules now, and sometimes they're on together.

7. **Now go back to the menu.** What happens to your blinks? The menu redraws *every*
   LED every 10 ms to show where you are, so you'll barely see them.

8. **Write down the rule.** Add a comment at the top of each app: "LED 0 belongs to
   {{ facts.firmware.user_app_name }}; the last LED belongs to {{ facts.firmware.user_app_name }} 2; the menu gets them all while it's
   showing." You've just **partitioned** the LEDs.

**✅ Done when** both apps blink their own LED without disturbing each other.

## What just happened

The firmware only manages one thing for you: which app is *open*. Everything else is
shared on the honor system. Python is happy to let two pieces of code make two objects
for the same pins, and the hardware does whatever it was told *last*.

You used the two standard fixes together:

- **One object per device.** A module is only loaded once, so every app that imports
  `lib.led_bar` gets the *same* `leds`. Now there's one list of colors, and each write
  includes everyone's changes.
- **A partition.** Each app agreed to touch only its own LEDs. Nothing enforces it.
  It's a rule you wrote down.

The firmware itself doesn't follow your partition, though. The menu takes every LED
while it's showing, opening an app turns them all off, and the display code uses the
first LED to show its progress (and turns them all off at the start and end of each
refresh). That's the third fix, an
**owner**: one piece of code that's the only one allowed to touch the device. Other code
*asks* it (sets a variable, or pushes onto a queue), and it decides who wins. Here, the
switcher is an owner that doesn't take requests. The same idea applies to the SAO pins,
the I2C bus and WiFi.

`leds` has an owner built in, too: `leds.set_sequence()` hands an animation to the
`leds.update()` task in `main.py`, and the menu pauses it (see [[animate-leds]]).

<!-- TODO(diagram): before: app A task → np(A) ┐ app B task → np(B) ┘→ LEDs (conflict). After: app A task ┐ app B task ┘→ leds → LEDs, with the menu's menu_display() also writing to leds -->

## Stuck?

| Symptom | Fix |
|---|---|
| Only one LED blinks at all | Each task starts the first time its app is opened. Open both apps since the last **Ctrl+D**. |
| Both blink at first, then one stops | Opening an app turns all the LEDs off once; the next blink turns its LED back on. If one stays off, check for an error in the shell. |
| `ImportError: no module named 'lib.led_bar'` | Spelling: `lib.led_bar`, with an underscore. |
| LEDs still fight | One app still has its own `neopixel.NeoPixel(...)`. Search both files for it. |

## Have fun!

- **Write an owner.** Make a module, `lib/my_leds.py`, with a dict of requests
  (`{"{{ facts.firmware.user_app_name }}": (32, 0, 0)}`) and one task that shows the *most recent* request
  on all LEDs. Now apps ask instead of write.
- **Priority:** a "notification" task that takes over every LED for 2 seconds, then
  hands them back.
- Do the same for the SAO I2C bus: two apps reading two sensors on one bus.
