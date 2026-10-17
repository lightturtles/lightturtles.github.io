---
id: qr-code
title: Show a QR code on your badge
label: Show a QR code
topic: display
workshop: false
needs: [app-screen]
time: 20 min
touches: [apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): is LVGL's qrcode widget compiled into this build? (dir(lvgl) has 'qrcode') -->

**Goal:** Put a QR code for your website, socials or contact card on your badge, so
people can scan it from across the table.

## You need

- Your app, with a screen from [[app-screen]]
- A phone with a camera, to test

## Steps

1. **Is it built in?** At `>>>`:

   ```python
   import lvgl
   hasattr(lvgl, "qrcode")
   ```

   `True`: carry on. `False`: see *No QR widget?* below.

2. **Make the code** in your screen layout:

   ```python
           URL = "https://example.com/me"          # yours
           size = min({{ facts.display.width }}, {{ facts.display.height }}) - 40
           self.qr = lvgl.qrcode(self.page.content)
           self.qr.set_size(size)
           self.qr.set_dark_color(lvgl.color_black())
           self.qr.set_light_color(lvgl.color_white())
           self.qr.update(URL, len(URL))
           self.qr.align(lvgl.ALIGN.CENTER, 0, 0)
   ```

   And `self.qr = None` in `switch_to_background()`.

3. Save, **Ctrl+D**, open your app, and scan it with your phone's camera.

4. **Make it scan from further away.** Try a shorter link (a link shortener helps),
   and compare how far back you can stand. Then try the code at a few sizes.

5. **Add a caption** under it, so people know what they'll get:

   ```python
           cap = lvgl.label(self.page.content)
           cap.set_text("my site")
           cap.align_to(self.qr, lvgl.ALIGN.OUT_BOTTOM_MID, 0, 4)
   ```

<!-- TODO(photo): the badge's QR code being scanned by a phone -->

**✅ Done when** a phone scans the code on your badge and opens your link.

## What just happened

A QR code stores text as a grid of black and white squares (**modules**), with extra
**error correction** so it still scans if part of it is damaged or dirty. More text
means more modules, so each one is smaller on the same screen, and the code is harder
to scan from far away. That's why short links scan better.

E-ink is great for QR codes: sharp black and white, readable in sunlight, and it stays
on screen with the power off (see [[sleep-with-image]]).

The light border around the code (the **quiet zone**) matters: scanners need it to find
the edges. Don't put anything right up against the code.

## No QR widget?

Generate the code on your laptop instead and show it as an image:

```bash
pip install qrcode pillow
python -c "import qrcode; qrcode.make('https://example.com/me', border=2).save('qr.png')"
```

Then copy `qr.png` to `images/` on the badge and show it as in [[eink-images]]. It's
already black and white, so it needs no dithering.

## Stuck?

| Symptom | Fix |
|---|---|
| Phone won't scan it | Make it bigger, the link shorter, or move the phone back a little. |
| `TypeError` on `update` | Some versions take just the text: `self.qr.update(URL)`. |
| The code is cut off | It's bigger than the content area. Make `size` smaller. |

## Have fun!

- A contact card: a QR with `MECARD:N:Your Name;EMAIL:you@example.com;;` adds you to
  a phone's contacts.
- A WiFi code: `WIFI:T:WPA;S:network;P:password;;` joins a phone to a network.
- Cycle between two codes on a button.
