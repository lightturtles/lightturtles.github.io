---
id: eink-refresh
title: "Why is e-ink so slow? Time a refresh; see ghosting; unplug it"
label: How e-ink works
tier: developmental
difficulty: 6
group: display
icon: stopwatch
needs: [lvgl-hello]
time: 15 min
touches: [hardware/display.py, hardware/lvgl_setup.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Measure how slow the screen really is, see its quirks with your own eyes,
and know why it's built that way.

## You need

- Your app from [[lvgl-hello]]
- A phone with a stopwatch (or slow-motion video)

## Steps

1. **Time a full refresh by eye.** Open your app and press **{{ facts.buttons.app_1_label }}** to change the
   label. Count, or film it in slow motion: how long from the first flash until the
   screen settles? How many times does it flash, and in what colors?

2. **Time it in code.** At `>>>`, with your app's screen showing (**Ctrl+C** while it's
   in the foreground):

   ```python
   import lvgl, time
   from apps.base_app import BaseApp
   app = [a for a in BaseApp.all_apps if a.name == "{{ facts.firmware.user_app_name }}"][0]

   app.label.set_text("timing...")
   t0 = time.ticks_ms()
   lvgl.refr_now(None)        # force LVGL to draw and send it now
   time.ticks_diff(time.ticks_ms(), t0)
   ```

   <!-- TODO(verify): does refr_now block until the e-ink BUSY pin releases, or return once the data is sent? -->

   Compare with your stopwatch number.

3. **Partial refresh.** <!-- TODO(verify): does the display/driver support partial refresh, and how is it switched on? -->
   Switch on partial refresh and time it the same way.

4. **Ghosting.** Change the label 10 times in a row with partial refreshes:

   ```python
   for i in range(10):
       app.label.set_text("ghost " * (i % 3 + 1))
       lvgl.refr_now(None)
   ```

   Look closely at the screen. Can you see faint traces of earlier text? Do one full
   refresh <!-- TODO(verify): how to force one --> and look again.

5. **Unplug it.** Power the badge off completely ({{ facts.power.power_off }}, and
   unplug USB). The image stays. Leave it overnight if you like.

**✅ Done when** you have a number for how long a refresh takes, you've seen ghosting,
and you've seen the image stay with the power off.

## What just happened

Each pixel of an e-ink display is a tiny capsule of **charged pigment particles**
({{ facts.display.colors }}) floating in clear fluid. A voltage across the capsule pulls
one color to the front. Particles have to physically *move*, and that's why it's slow.

A **full refresh** drives every pixel through a sequence of voltages (the
**waveform**), often flashing black and white to "shake" the particles loose before
setting the final color. The third color has heavier particles and needs a longer
waveform, which is why three-color screens are the slowest. A **partial refresh** only
drives the pixels that changed, with a short waveform. It's faster, but particles
don't fully settle, and the leftovers are **ghosting**.

Once the particles are in place, they stay there with **no power at all**. That's
why e-ink is perfect for a name badge, and why your app should change the screen
as rarely as possible: every refresh costs time, battery and a flash.

<!-- TODO(diagram): one e-ink capsule, cross-section: top electrode, black/white/third-color particles, bottom electrode; voltage arrow pulling one color to the top -->

## Stuck?

| Symptom | Fix |
|---|---|
| `AttributeError: ... 'label'` | Your app wasn't in the foreground when you pressed Ctrl+C, so its label doesn't exist. |
| `IndexError` finding your app | Print `[a.name for a in BaseApp.all_apps]` and use the exact name. |
| `refr_now` returns instantly but the screen keeps flashing | The driver sends the image and lets the display finish on its own. Your stopwatch time is the real one. |

## Have fun!

- What's the fastest you can update a *small* area (one digit) without ghosting
  getting bad?
- Read the display's [datasheet]({{ facts.display.datasheet }}): what refresh time does it promise? Does
  yours match? What happens when it's cold?
