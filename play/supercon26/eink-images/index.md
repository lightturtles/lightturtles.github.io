---
id: eink-images
title: Convert and dither an image for a three-color e-ink panel
label: Images on a 3-color panel
topic: display
workshop: false
needs: [lvgl-hello]
time: 30 min
touches:
  - lib/epd.py#EPaperDisplay.draw_png    # draw_png(path, row, col): straight into the framebuffers
  - lib/large_png.py#_read_palette_png   # palette or grayscale PNGs only, not interlaced
  - lib/large_png.py#_color_kind         # red if R ≥ 128 and G, B < 128; black if all < 128; else white
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Turn any picture into {{ facts.display.colors }}, with dithering so it still
looks like the picture, and show it from your app.

## You need

- Your app from [[first-app]] or [[lvgl-hello]]
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

2. **Convert it twice**, to compare. Pick a size that fits your layout (the whole screen
   is {{ facts.display.width }} × {{ facts.display.height }}):

   ```bash
   python eink.py me.jpg me.png 120 120
   python eink.py me.jpg me_flat.png 120 120 --no-dither
   ```

   Open both on your laptop. The dithered one is made of dots; the flat one is
   blocks of solid color. Which looks more like your picture?

3. **Copy it to the badge.** In Thonny, upload `me.png` and `me_flat.png` into
   `/data/graphics/` on the badge, next to the badge's own pictures.

4. **Show it.** In your app (with `from lib.epd import display` at the top), draw it
   when the app opens:

   ```python
       def run(self):
           if self.launched:
               display.clear()
               display.draw_png("/data/graphics/me.png", row=200, col=330)
               display.update()
   ```

   `row` and `col` are where the picture's top-left corner goes, in pixels from the top
   and from the left. (Note the order: row first.) Using LVGL too? Draw the picture
   *after* `lvgl.refr_now(...)`, or LVGL paints over it.

5. Save, **Ctrl+D**, open your app. Compare it with the screen on your laptop.

6. **Try the other one** (change the file name), and a photo vs. a drawing. Which
   survive three colors best?

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

The badge does the same thing for any color it finds in the PNG's palette: red if it's
mostly red, black if it's dark, and white otherwise (`_color_kind()` in
`lib/large_png.py`). That's no dithering at all, so do the work on your laptop, where
it's free, and hand the badge a picture that only has the three colors in it.

Sizing on the laptop matters too. The badge reads the whole (compressed) file into RAM
before it decodes it a row at a time, so a smaller picture loads faster and uses less
memory (see [[out-of-memory]]).

The badge's own repo has another way to do the conversion, with ImageMagick:
`magick in.png -remap firmware/scripts/palette.gif out.png` (add `+dither` for the
flat version).

Red is special: it's the slowest color to draw (see [[use-red]]). An image with a
little red costs a full red refresh, just like one with a lot.

<!-- TODO(diagram): one row of grays → quantized (blobs) vs. dithered (dots), shown side by side -->

## Stuck?

| Symptom | Fix |
|---|---|
| `OSError: [Errno 2] ENOENT` | Wrong path. Check `os.listdir('/data/graphics')` at `>>>`. |
| `ValueError: save the png as a palette image` | It's a full-color PNG. Run it through `eink.py` (or the `magick` command). |
| `ValueError: turn off interlacing ...` | Your editor saved an interlaced PNG. Re-save it without, or run it through `eink.py`. |
| `MemoryError` | The image is too big. Convert it smaller. |
| Image doesn't show, no error | Did you call `display.update()`? Did LVGL draw over it? |
| Part of it is missing | It runs off the screen ({{ facts.display.width }} × {{ facts.display.height }}). Check `row` and `col`. |
| Pillow says `Image.Dither` doesn't exist | Your Pillow is old. `pip install -U pillow`. |
| Skin tones go all red | Red is the nearest color to them. Convert to black and white only: remove the red from the palette. |

## Have fun!

- Make a two-color version (drop red) and compare.
- Turn your photo into high-contrast line art first (any photo editor's "threshold"),
  then convert it.
- Put your picture on your name badge: [[name-badge]], change B.
- Sticker of the day: put a few converted images in a folder and show a random one each time the app opens (`os.listdir()` and `random.choice`). Gallery (`apps/gallery.py`) does exactly this.
