---
id: use-red
title: Use the third color on purpose (and what it costs)
label: Use red on purpose
topic: display
workshop: false
needs: [eink-images]
time: 20 min
touches: [apps/userA.py, hardware/display.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): how the firmware maps LVGL colors to the panel's {{ facts.display.third_color }} (nearest color? a fixed hex?) -->

**Goal:** Highlight the one thing that matters on your screen with
{{ facts.display.third_color }}, and measure what it costs in refresh time.

## You need

- Your app, with a screen from [[app-screen]] or [[lvgl-hello]]
- A stopwatch (your phone)
- [[eink-images]] done, so you've seen how {{ facts.display.third_color }} shows up

## Steps

1. **Time a refresh without red.** Open your app and press the button that changes your
   label. Time it from the first flash to the last. Do it three times.

2. **Make one thing red.** Pick the most important label on your screen, and color it
   when you create it:

   ```python
           RED = lvgl.color_hex(0xFF0000)
           self.label.set_style_text_color(RED, 0)
   ```

3. Save, **Ctrl+D**, and time three refreshes again. How much slower? Count the
   flashes too: is there an extra phase?

4. **Red only when it matters.** Make the label red only when the value needs
   attention, and black the rest of the time:

   ```python
           color = RED if self.value > 30 else lvgl.color_black()
           self.label.set_style_text_color(color, 0)
   ```

   Now most updates are fast, and the slow red one *means* something.

5. **Other ways to stand out without red.** Try each and compare from across the room:
   - **inverse:** white text on a black box (`set_style_bg_color`, `set_style_bg_opa`)
   - **size:** a bigger font for the key number (see [[app-screen]])
   - **a border** around it (`set_style_border_width`)

**✅ Done when** you've measured the refresh with and without red, and your screen uses
red for exactly one thing.

## What just happened

On a three-color panel, each pixel has black, white *and* {{ facts.display.third_color }}
particles. The colored ones are bigger and slower, so the panel needs a longer
**waveform** to move them: extra phases, more flashing, more time (see [[eink-refresh]]).
Many panels can only do a fast partial refresh in black and white, and need a full,
slow refresh for any red at all.

So red has a price, and a design rule follows: **one red thing per screen, and only
when it means something** (a warning, the current turn, the thing to look at first).
If everything is highlighted, nothing is.

## Stuck?

| Symptom | Fix |
|---|---|
| The text comes out black, not red | The firmware rounds colors to the nearest the panel has. Try pure `0xFF0000`. |
| Everything is pinkish or dotted | Something is being dithered. Use pure colors for text. |
| Red appears where you didn't ask | A style or theme default. Check the parent's styles. |

## Have fun!

- A red border that appears only when a timer runs out.
- Measure: is a screen with *a little* red as slow as one that's mostly red?
- Read the panel's datasheet ({{ facts.display.datasheet }}): how long does it say each
  waveform takes?
- A status sign: a button cycles through "Ask me about ___", "Need coffee" and "Heads down", with the key words in red. E-ink keeps the sign up even while the badge sleeps (see [[sleep-with-image]]).
- A forest fire: trees (black) grow at random on a canvas, lightning sets one alight, and fire (red) spreads to its neighbors and burns out. Plant them too densely and the whole forest burns. (See [[draw-pixels]].)
