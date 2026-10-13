---
id: live-data
title: Replace a print with live data (sensor, battery, or WiFi)
label: Show real data
tier: core
difficulty: 7
group: apps
icon: gauge
needs: [first-app]
time: 25 min
touches: [apps/userA.py, hardware/badge.py, hardware/board.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Make your app report something real from the world, without slowing down
the rest of the badge.

## You need

- Your app from [[first-app]]
- **One** of these:
  - **A. Battery voltage:** nothing extra
  - **B. An I2C sensor** on the SAO port: find its address with [[i2c-scan]]
  - **C. Something from the web:** the badge on WiFi (see [[wifi-join]])

## Steps

1. **Try it at `>>>` first**, with the badge stopped (**Ctrl+C**). Pick your option:

   **A. Battery voltage**

   ```python
   from machine import ADC, Pin
   adc = ADC(Pin({{ facts.battery.adc_pin }}), atten=ADC.ATTN_11DB)
   adc.read_uv() / 1_000_000 * {{ facts.battery.divider }}      # volts at the pin × the divider ratio
   ```

   Plug and unplug USB and read it again. Does it change?

   **B. I2C sensor**

   ```python
   from hardware.badge import badge_obj
   i2c = badge_obj.{{ facts.sao.i2c_attr }}     # the firmware's SAO I2C bus
   i2c.scan()                     # your sensor's address should be listed
   i2c.readfrom_mem({{ facts.sensor.address }}, {{ facts.sensor.register }}, {{ facts.sensor.bytes }})   # address, register, bytes
   ```

   That's the raw reading from the {{ facts.sensor.name }}. <!-- TODO: its conversion to real units -->

   **C. Web data**

   ```python
   import requests
   r = requests.get("{{ facts.wifi.test_url }}")
   r.text
   ```

   Notice how long that took.

2. **Set up once, in `__init__`.** Creating the ADC or finding the bus only needs to
   happen once. For option A:

   ```python
   from machine import ADC, Pin   # at the top of the file

       def __init__(self, name, badge):
           super().__init__(name, badge)
           self.background_sleep_ms = 5000
           self.ticks = 0
           self.adc = ADC(Pin({{ facts.battery.adc_pin }}), atten=ADC.ATTN_11DB)

       def read_value(self):
           return self.adc.read_uv() / 1_000_000 * {{ facts.battery.divider }}
   ```

   For option B, keep `self.i2c = badge.{{ facts.sao.i2c_attr }}` and put the `readfrom_mem` in
   `read_value()`. For option C, put the `requests.get` in `read_value()`.

3. **Read in the tick.** Replace the tick's `print`:

   ```python
       def run_background(self):
           self.ticks += 1
           print(f"[{self.name}] {self.read_value():.2f} V")
   ```

4. **Read in the foreground too, but not every call.** `run_foreground()` runs many
   times a second, so check the clock and read every 2 seconds:

   ```python
   import time   # at the top of the file

       def run_foreground(self):
           now = time.ticks_ms()
           if time.ticks_diff(now, getattr(self, "last_read", 0)) > 2000:
               self.last_read = now
               print(f"[{self.name}] {self.read_value():.2f} V")
           # ...your buttons, as before
   ```

5. Save, **Ctrl+D**, and watch the numbers in both states.

6. **Option C only: feel the stutter.** With your app in the foreground, press buttons
   while a web request runs. The badge can't respond until the request is done. Read
   the web data much less often: once a minute is plenty.

**✅ Done when** your app prints a live value that changes when the world does: warm
the sensor with your finger, unplug USB, or wait for the web data to change.

## What just happened

**Set up once, read often.** Making the ADC, finding the I2C bus or joining WiFi is
slow, so you do it in `__init__`. Reading is quick (except over the web), so it goes in
the tick.

**Reads take time, and while one runs, nothing else does.** An ADC read takes
microseconds and an I2C read about a millisecond, so neither matters. A web request
takes half a second or more. That's a full [[hog-the-cpu]]-style freeze, just short
enough to feel like a stutter. Reading less often is the simple fix. A real fix needs a
library that `await`s while it waits for the network, which is a stretch skill.

`ticks_ms()` and `ticks_diff()` are how badge code tracks time without waiting. Note when
you last did something, and on each call, check whether enough time has passed. You'll
use this pattern in every app.

## Stuck?

| Symptom | Fix |
|---|---|
| Badge stutters every time you read | The read blocks. Read less often, or see [[hog-the-cpu]]. |
| `OSError: [Errno 19] ENODEV` (I2C) | Sensor not found at that address. Re-run [[i2c-scan]]. |
| `OSError: -202` or similar (web) | Not connected, or no DNS. Check `wlan.isconnected()`; see [[wifi-join]]. |
| Battery reads ~0 V, or huge | Wrong pin or divider ratio. Check `{{ facts.firmware.pins_file }}`. |
| The value jumps around a little | That's noise. Average a few readings, or round more. |

## Have fun!

- Show the minimum and maximum since the app started.
- Use two sources at once: battery *and* temperature.
- Log readings to a file with a timestamp, then plot them on your laptop.
