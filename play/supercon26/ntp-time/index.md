---
id: ntp-time
title: Set the badge's clock over the internet (NTP), and show the local time
label: Set the clock
topic: wifi
workshop: false
needs: [wifi-join]
time: 20 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Set the badge's clock from the internet, convert it to Pasadena time, and
show it.

## You need

- Your badge on WiFi (see [[wifi-join]])

## Steps

1. **What time does the badge think it is?** At `>>>`:

   ```python
   import time
   time.localtime()
   ```

   Probably the year 2000: the clock started from zero when the badge powered up.

2. **Ask the internet:**

   ```python
   import ntptime
   ntptime.host = "{{ facts.clock.ntp_host }}"
   ntptime.settime()
   time.localtime()
   ```

   That's the right time, in **UTC** (London in winter, give or take).

3. **Convert to local time.** The badge doesn't know about time zones, so add the
   offset yourself. Pasadena is UTC{{ facts.clock.utc_offset_h }} hours right now:

   ```python
   OFFSET_H = {{ facts.clock.utc_offset_h }}
   def local():
       return time.localtime(time.time() + OFFSET_H * 3600)

   y, mo, d, h, mi, s, wd, yd = local()
   f"{h:02d}:{mi:02d}"
   ```

4. **Show it in your app.** Only the minutes matter on e-ink, so check each call, but
   change the screen once a minute:

   ```python
           y, mo, d, h, mi, *_ = local()
           text = f"{h:02d}:{mi:02d}"
           if text != getattr(self, "shown", None):
               self.shown = text
               self.label.set_text(text)       # your label from lvgl-hello
   ```

5. **Watch it drift.** Leave the badge on for an hour, then compare `time.localtime()`
   before and after another `ntptime.settime()`. How far off was it?

**✅ Done when** your badge shows the right local time.

## What just happened

**NTP** (Network Time Protocol) asks a time server for the current time, and corrects
for how long the reply took to arrive. `ntptime.settime()` writes the answer into the
chip's **RTC** (real-time clock), which then keeps counting on its own.

The RTC counts in **UTC**, one time for the whole planet. Time zones and daylight
saving are just offsets, decided by governments and changed now and then, so tiny
devices usually leave them to you.

**A daylight-saving trap, right on time:** US clocks fall back at 2 a.m. on Sunday,
November 1, 2026. Pasadena goes from UTC−7 (PDT) to UTC−8 (PST) in the middle of the
weekend. A hard-coded offset will be an hour off on Sunday.
<!-- TODO(verify): Supercon 2026 dates vs. Nov 1 -->

The RTC's crystal isn't perfect: it drifts by seconds a day. Re-sync now and then
(once a day is plenty), whenever WiFi is around.

## Stuck?

| Symptom | Fix |
|---|---|
| `OSError: [Errno 110] ETIMEDOUT` | The time server didn't answer. Try again, or another `ntptime.host` (e.g. `time.google.com`). |
| `OSError: -202` | Not on WiFi, or no DNS. See [[wifi-join]]. |
| An hour off | Daylight saving: check the offset. |
| Year 2000 again after a reset | A hard reset or power cycle restarts the clock. Sync after every boot. |

## Have fun!

- Handle daylight saving: if the date is on or after November 1, 2026, at 9:00 UTC, use −8.
- A countdown to the next talk, or to the badge hacking demos.
- Sync at boot in your app's `__init__`, if WiFi is up (see [[save-settings]] to store the network).
- A "word clock": "quarter past ten" instead of 10:15.
- Now / Next: fetch the con schedule (see [[web-data]]), show the current and next talk, and turn the screen red 5 minutes before the next one starts (see [[use-red]]).
