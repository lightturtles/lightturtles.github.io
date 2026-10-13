---
id: all-leds
title: Light all the LEDs from the REPL
label: Light all the LEDs
tier: developmental
difficulty: 2
group: lights
icon: rainbow
needs: [one-led]
time: 15 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Control the whole row of LEDs at once: one color, then a rainbow, then a moving light.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- The `np` object from [[one-led]] (run those setup lines again if you reset)

## Steps

1. Fill every LED with one color:

   ```python
   np.fill((0, 16, 16))
   np.write()
   ```

2. Do the same thing with a loop, so each LED can get its own color:

   ```python
   for i in range(len(np)):
       np[i] = (i * 4, 0, 32 - i * 4)
   np.write()
   ```

3. Make a rainbow. This helper turns a position on the color wheel (0–255)
   into a color:

   ```python
   def wheel(pos, bright=32):
       pos = pos % 256
       if pos < 85:
           r, g, b = 255 - pos * 3, pos * 3, 0
       elif pos < 170:
           pos -= 85
           r, g, b = 0, 255 - pos * 3, pos * 3
       else:
           pos -= 170
           r, g, b = pos * 3, 0, 255 - pos * 3
       return (r * bright // 255, g * bright // 255, b * bright // 255)
   
   for i in range(len(np)):
       np[i] = wheel(i * 256 // len(np))
   np.write()
   ```

4. Make it move:

   ```python
   import time
   offset = 0
   while True:
       for i in range(len(np)):
           np[i] = wheel(i * 256 // len(np) + offset)
       np.write()
       offset += 8
       time.sleep(0.05)
   ```

   Press **Ctrl+C** to stop.

<!-- TODO(video): a few seconds of the rainbow scrolling -->

**✅ Done when** a rainbow scrolls along the badge.

## What just happened

`len(np)` asks the object how many LEDs it has, so your loops work no matter how
many there are. `np.fill(...)` is a shortcut for the loop in step 2.

Each pass of the `while` loop computes all {{ facts.leds.count }} colors, sends them
with one `np.write()`, then waits. Shorter sleep = faster animation.

While that loop runs, the badge can't do anything else: no buttons, no screen.
That's fine at the REPL, but an app has to share the processor
(see [[animate-nonblocking]]).

## Stuck?

| Symptom | Fix |
|---|---|
| `NameError: name 'np' isn't defined` | You reset since setting it up. Re-run the setup from [[one-led]]. |
| `IndentationError` when pasting | Paste the whole block at once. In Thonny, try **Ctrl+E** (paste mode) first. |
| Colors look washed out or white | Lower `bright`. Mixing all three at high values looks white. |
| Badge resets when everything is bright | Too much current for the battery. Lower the brightness, or plug in USB. |

## Have fun!

- A "Knight Rider" light that bounces end to end.
- Fade all LEDs in and out together (a "breathing" effect).
- A progress bar: light one more LED each second.
