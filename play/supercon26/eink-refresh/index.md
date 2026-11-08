---
id: eink-refresh
title: "Why is e-ink so slow? Time a refresh; see ghosting; unplug it"
label: Why e-ink is slow
topic: display
workshop: false
needs: [lvgl-hello]
time: 15 min
touches:
  - lib/epd.py#EPaperDisplay.run             # waits for update(), copies the framebuffers, refreshes
  - lib/epd.py#EPaperDisplay.global_update   # prints its own timings: sending, then refreshing
  - lib/epd.py#EPaperDisplay._send_images    # sends the 4 pictures over SPI, without an await
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Measure how slow the screen really is, see what the badge does while it
waits, and know why e-ink is built that way.

## You need

- Your app from [[lvgl-hello]]
- A phone with a stopwatch (or slow-motion video)

## Steps

1. **Time a refresh by eye.** Open your app and press **{{ facts.buttons.app_1_label }}** to change the
   label. Count, or film it in slow motion: how long from the first flash until the
   screen settles? How many times does it flash, and in what colors?

2. **Let the badge time it.** Watch the shell while it refreshes. The display task
   prints its own timings:

   ```
   Viper split & reverse ms: 34   <- ms to cut the picture in half and flip its bits
   Updating display to new image
   228                            <- ms to send the picture to the panel
   display working
   Done updating display
   34704                          <- ms for the panel to refresh
   ```

   Those are a real badge's numbers: preparing and sending the picture takes a quarter
   of a second, and the panel takes about 35 seconds. Compare the total with your
   stopwatch.

3. **Read how it's done.** Open `lib/epd.py` and find `global_update()`. It's a recipe:
   reset the panel, send the black and the red pictures (`_send_images()`), power up
   the panel's voltage pump (`_dcdc_soft_start()`), tell it to refresh, wait for its
   BUSY pins, and power down again. Most steps end in `await aio.sleep_ms(...)`, so other
   tasks run while the panel works.

4. **Is the badge busy meanwhile?** Add the call counter from [[first-app]] to your app,
   with a message every 10 calls instead of 50. Press **{{ facts.buttons.app_1_label }}**, and watch the
   messages while the screen refreshes. Do they keep coming? Is there a gap? Look at
   `run()` and `_send_images()`: which parts have no `await`?

5. **Unplug it.** Power the badge off completely ({{ facts.power.power_off }}, and
   unplug USB). The image stays. Leave it overnight if you like.

**✅ Done when** you have a number for how long a refresh takes, you know which part
of it holds up the rest of the badge, and you've seen the image stay with the power off.

## What just happened

Each pixel of an e-ink display is a tiny capsule of **charged pigment particles**
({{ facts.display.colors }}) floating in clear fluid. A voltage across the capsule pulls
one color to the front. Particles have to physically *move*, and that's why it's slow.

A **full refresh** drives every pixel through a sequence of voltages (the
**waveform**), often flashing black and white to "shake" the particles loose before
setting the final color. The third color has heavier particles and needs a longer
waveform, which is why three-color screens are the slowest. A **partial refresh** only
drives the pixels that changed, with a short waveform. It's faster, but particles
don't fully settle, and the leftovers are **ghosting**. This badge's firmware only does
full refreshes: every `display.update()` sends the whole screen, both colors.

Getting the picture *to* the panel takes a little time too. The panel is really two
halves, each with its own controller, and the firmware sends them 4 pictures (black and
red, left and right) over SPI, after cutting the framebuffers in half and flipping the
bits of every byte (in fast "viper" code). Those parts have no `await`, so for that
quarter of a second nothing else on the badge runs (see [[hog-the-cpu]]). The 35
seconds the panel takes, on the other hand, are all `await`s: the rest of the badge
carries on.

Once the particles are in place, they stay there with **no power at all**. That's
why e-ink is perfect for a name badge, and why your app should change the screen
as rarely as possible: every refresh costs time, battery and a flash.

<!-- TODO(diagram): one e-ink capsule, cross-section: top electrode, black/white/third-color particles, bottom electrode; voltage arrow pulling one color to the top -->

## Stuck?

| Symptom | Fix |
|---|---|
| No timings in the shell | Nothing asked for a refresh. Did your app call `display.update()`? |
| Two presses, one refresh | The second `update()` came during the first refresh, and was dropped (see [[draw-pixels]]). |
| The timings are much shorter than your stopwatch | The panel keeps settling after the firmware says it's done. Your stopwatch is the real one. |

## Have fun!

- Does a picture with no red refresh any faster (see [[use-red]])?
- Find the panel's datasheet (a 9.7" Pervasive Displays panel; `lib/epd.py` names the
  driver it was ported from): what refresh time does it promise? Does yours match?
  What happens when it's cold?
