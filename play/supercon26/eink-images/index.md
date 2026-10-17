---
id: eink-images
title: Convert and dither an image for a three-color e-ink panel
label: Images on a 3-color panel
topic: display
workshop: false
needs: [lvgl-hello]
time: 30 min
touches: [apps/userA.py, ui/graphics.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): image format and size the firmware's graphics.create_image() accepts (2025: PNG from images/) -->

**Goal:** Turn any picture into {{ facts.display.colors }}, with dithering so it still
looks like the picture, and show it from your app.

## You need

- Your app from [[lvgl-hello]]
- Python 3 on your laptop, with Pillow: `pip install pillow`
- A picture: a logo, a face, a sticker. Simple, high-contrast images work best.

## Steps

1. **Save this script** on your laptop as `eink.py`:

   ```python
   """Make an image for a black/white/red e-ink panel.
   Usage: python eink.py in.jpg out.png WIDTH HEIGHT [--no-dither]"""
   import sys
   from PIL import Image

   src, dst, w, h = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
   dither = Image.Dither.NONE if "--no-dither" in sys.argv else Image.Dither.FLOYDSTEINBERG

   palette = Image.new("P", (1, 1))
   palette.putpalette([0, 0, 0,  255, 255, 255,  255, 0, 0] + [0, 0, 0] * 253)

   img = Image.open(src).convert("RGB")
   img.thumbnail((w, h))                         # fit inside w × h, keep the shape
   out = img.quantize(palette=palette, dither=dither)
   out.save(dst, optimize=True)
   print(f"{dst}: {out.size[0]} x {out.size[1]}")
   ```

   <!-- TODO(verify): the panel's real "red" (pure 255,0,0, or a darker shade?) -->

2. **Convert it twice**, to compare. Pick a size that fits your layout (the whole screen
   is {{ facts.display.width }} × {{ facts.display.height }}):

   ```bash
   python eink.py me.jpg me.png 120 120
   python eink.py me.jpg me_flat.png 120 120 --no-dither
   ```

   Open both on your laptop. The dithered one is made of dots; the flat one is
   blocks of solid color. Which looks more like your picture?

3. **Copy it to the badge.** In Thonny, upload `me.png` into `images/` on the badge.

4. **Show it.** In your app's `switch_to_foreground()`, after the page's content area
   exists:

   ```python
   from ui import graphics    # at the top of the file

           self.img = graphics.create_image("images/me.png", self.page.content)
           self.img.align(lvgl.ALIGN.CENTER, 0, 0)
   ```

   And `self.img = None` in `switch_to_background()`.

5. Save, **Ctrl+D**, open your app. Compare it with the screen on your laptop.

6. **Try the other one**, and a photo vs. a drawing. Which survive three colors best?

<!-- TODO(photo): the same photo dithered and flat, on the badge -->

**✅ Done when** your own picture shows on the badge in three colors, and you've seen
it with and without dithering.

## What just happened

The panel has three colors, and no in-between. **Quantizing** picks, for each pixel,
the nearest of the three. Without dithering, every light-gray pixel turns white and
every dark one black, so soft photos turn into blobs.

**Dithering** (here, Floyd–Steinberg) spreads the error around: if a pixel was
"rounded" too light, its neighbors are nudged darker. From a distance, a pattern of
black and white dots *looks* gray. Newspapers have done this for a century.

Sizing on the laptop matters too. Shrinking the image there means the badge reads a
small file and decodes a small picture into RAM (see [[out-of-memory]]).

Red is special: it's the slowest color to draw (see [[use-red]]). An image with a
little red costs a full red refresh, just like one with a lot.

<!-- TODO(diagram): one row of grays → quantized (blobs) vs. dithered (dots), shown side by side -->

## Stuck?

| Symptom | Fix |
|---|---|
| `OSError: [Errno 2] ENOENT` | Wrong path. Check `os.listdir('images')` at `>>>`. |
| `MemoryError` | The image is too big. Convert it smaller. |
| Image doesn't show, no error | The firmware may not read this format. Check what's already in `images/` and match it. |
| Pillow says `Image.Dither` doesn't exist | Your Pillow is old. `pip install -U pillow`. |
| Skin tones go all red | Red is the nearest color to them. Convert to black and white only: remove the red from the palette. |

## Have fun!

- Make a two-color version (drop red) and compare.
- Turn your photo into high-contrast line art first (any photo editor's "threshold"),
  then convert it.
- Put your picture on your name badge: [[name-badge]], change B.
- Sticker of the day: put a few converted images in a folder and show a random one each time the app opens (`os.listdir()` and `random.choice`).
