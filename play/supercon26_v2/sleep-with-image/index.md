---
id: sleep-with-image
title: Deep sleep with your image still showing; wake on a button
label: Sleep with your image showing
topic: display
workshop: false
needs: [eink-refresh]
time: 25 min
touches: [main.py, hardware/display.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): the wake button ({{ facts.sleep.wake_label }}) is on an RTC-capable GPIO (0–21 on the ESP32-S3), and the display needs no shutdown command before sleep -->

**Goal:** Put the badge into deep sleep, using almost no power, while the e-ink keeps
showing your name. Press a button to wake it up.

## You need

- Your badge, with something on the screen worth keeping (your name badge, a QR code)
- It's easiest to try this on battery. Over USB, sleeping drops the connection.

## Steps

1. **Get the screen right first.** Open the app whose screen you want to keep, and wait
   for the refresh to finish.

2. **Turn off what the e-ink doesn't need.** At `>>>` (**Ctrl+C**), switch the LEDs off.
   They keep their last color, and their power, while the chip sleeps:

   ```python
   from machine import Pin
   import neopixel
   np = neopixel.NeoPixel(Pin({{ facts.leds.pin }}), {{ facts.leds.count }})
   np.fill((0, 0, 0)); np.write()
   ```

3. **Choose a wake button.** Wake the chip when button **{{ facts.sleep.wake_label }}**
   is pressed (it reads 0 when pressed):

   ```python
   import esp32, machine
   wake = Pin({{ facts.sleep.wake_pin }}, Pin.IN, Pin.PULL_UP)
   esp32.wake_on_ext0(pin=wake, level=esp32.WAKEUP_ALL_LOW)
   ```

4. **Go to sleep:**

   ```python
   machine.deepsleep()
   ```

   The USB connection drops. The screen stays exactly as it was.

5. **Wake it.** Press **{{ facts.sleep.wake_label }}**. The badge starts up from the
   beginning, as if you'd pressed **{{ facts.power.reset_button }}**. Reconnect, and check
   why it woke:

   ```python
   import machine
   machine.reset_cause() == machine.DEEPSLEEP_RESET
   ```

6. **Make it a menu item.** Put steps 2–4 in a function in your app, and call it on a
   button from `run_foreground()`. Now "sleep" is one press away.

**✅ Done when** the badge sleeps with your image still on the screen, and a button
wakes it.

## What just happened

In **deep sleep**, almost the whole chip is switched off: the processors, the RAM,
the radio. Only a tiny low-power corner (the **RTC** domain) stays awake, watching a
timer or a few pins. That's why waking up is a full restart: RAM was off, so all your
variables are gone.

<!-- TODO(verify): measured sleep current on this badge, for a "days on one battery" number -->

The e-ink doesn't care: its pixels stay put with no power at all (see
[[eink-refresh]]). So a sleeping badge still shows your name, for days, on a battery
that would last hours awake.

Only **RTC GPIOs** can wake the chip, because only they're connected to the part that
stays on. On the ESP32-S3, that's GPIO 0–21. A button wired anywhere else can't wake it.

`deepsleep(ms)` also takes a time: the badge wakes on its own after that many
milliseconds. Wake every minute, update the screen, sleep again: that's how e-ink
clocks and weather displays run for months.

## Stuck?

| Symptom | Fix |
|---|---|
| It wakes up straight away | The wake button reads 0 already (held, or no pull-up). Check `wake.value()` is 1 before sleeping. |
| Button doesn't wake it | Not an RTC pin, or the wrong `level`. Try `esp32.WAKEUP_ANY_HIGH` if it reads 1 when pressed. |
| The screen went blank | The display was told to clear on shutdown, or the refresh hadn't finished. Wait longer before step 4. |
| LEDs stay lit while asleep | Turn them off first (step 2). |
| Thonny shows errors after sleep | Normal: the USB port vanished. Reconnect (**Stop/Restart**). |

## Have fun!

- Sleep for 10 minutes at a time, and show the time of the last wake (see [[ntp-time]]).
- Count wakes in a file, and show the number when it wakes up (see [[save-settings]]).
- Show a QR code while asleep (see [[qr-code]]): a business card that lasts all weekend.
- A screensaver: draw something new before each sleep: generative art, a fractal, a city skyline, an aquarium (see [[draw-pixels]]).
