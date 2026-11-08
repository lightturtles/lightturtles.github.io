---
id: out-of-memory
title: Running out of memory (gc.mem_free, MemoryError, and what eats RAM)
label: Running out of memory
topic: write-app
workshop: false
needs: [first-app]
time: 20 min
touches:
  - main.py#main                     # prints micropython.mem_info() with every 60 s heartbeat
  - lib/epd.py#EPaperDisplay.__init__   # the big buffers: LVGL's draw buffer and the two framebuffers
  - lib/large_png.py#show_png        # decodes a PNG row by row, straight into the framebuffers
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** See how much RAM your code has, run out on purpose, and learn the habits that
keep your app from running out by accident.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])

## Steps

1. **How much is free?** Press **Ctrl+C**, then:

   ```python
   import gc, micropython
   gc.collect()
   gc.mem_free()          # bytes free for Python
   gc.mem_alloc()         # bytes in use
   micropython.mem_info()
   ```

   Write down the free number. That's after the badge's own apps, the screen and
   LVGL took their share. (The badge prints the same `mem_info()` report by itself,
   with every `Main 60s heartbeat`.)

2. **Run out on purpose.** Grab memory 100 kB at a time until it fails:

   ```python
   hog = []
   while True:
       hog.append(bytearray(100_000))
       print(len(hog) * 100, "kB")
   ```

   It stops with `MemoryError`. How far did you get? Compare with step 1.

3. **Give it back:**

   ```python
   hog = None
   gc.collect()
   gc.mem_free()
   ```

   Back to where you started. Memory is only freed once nothing points at it, and
   `gc.collect()` makes that happen now rather than later.

4. **Strings add up.** Each `+=` on a string makes a whole new string:

   ```python
   gc.collect(); before = gc.mem_free()
   s = ""
   for i in range(2000):
       s += "x"
   before - gc.mem_free()      # how much did 2000 letters cost?
   ```

   Now the cheap way: collect the pieces in a list and `"".join(parts)` once at the end.
   Measure it the same way.

5. **Screens are big.** The badge's display code keeps the whole screen in RAM, more
   than once. Work out what it holds ({{ facts.display.width }} × {{ facts.display.height }} pixels):

   ```python
   {{ facts.display.width }} * {{ facts.display.height }} * 2     # LVGL's drawing buffer: 2 bytes per pixel
   {{ facts.display.width }} * {{ facts.display.height }} // 8    # one framebuffer: 1 bit per pixel (there's a black one and a red one)
   ```

   Over a megabyte for LVGL alone, made once at start-up and reused forever. PNGs, on
   the other hand, are decoded a row at a time straight into the framebuffers
   (`lib/large_png.py`), so even a full-screen picture never sits in RAM whole.

6. **Watch your app.** In your app's `run()`, print `gc.mem_free()` every 50 calls (as in [[first-app]]).
   Does it slowly go down and then jump back up? That's normal: garbage piles up, then
   gets collected. Does it go down and *never* come back? Something is keeping
   everything (a list that only grows?).

7. Press **Ctrl+D** to get the badge back.

**✅ Done when** you've caused a `MemoryError`, freed the memory again, and can name two
things that use a lot of RAM.

## What just happened

Python finds memory for you on the **heap** and gets it back with the **garbage
collector** (`gc`): every so often, it finds objects nothing points at any more and
frees them. On your laptop, the heap is gigabytes. On the badge, it's what you
measured in step 1, shared with every app.

The badge's ESP32-S3 has PSRAM, extra RAM chips next to the processor, and MicroPython
puts its heap there: several megabytes, where a plain ESP32 has a few hundred kB.

**`MemoryError` doesn't always mean "full."** The heap can have plenty free in total,
but in small scattered pieces (**fragmentation**). A request for one big block then
fails. Big buffers are best made once, early (in `__init__`), and reused.

**Habits that help:**

- Make big things once and reuse them (`bytearray`, buffers, images).
- Build strings with a list and `join`, or f-strings, not `+=` in a loop.
- Keep lists from growing forever: a `deque((), 100)` drops the oldest items for you.
- Drop what you don't need (`self.page = None` once you've drawn it).
- Read big files a piece at a time instead of `f.read()` all at once.

## Stuck?

| Symptom | Fix |
|---|---|
| Step 2 takes a long time | There's a lot of PSRAM. Try `bytearray(1_000_000)` each time. |
| `MemoryError` when an app opens | It's making something big. Check images and long lists. |
| Badge resets instead of `MemoryError` | That's a crash in C code that ran out (often WiFi or LVGL). Free memory before starting them. |
| `mem_info()` output is confusing | Look only at `free:` and `max free sz` (the largest single block). |

## Have fun!

- Find the biggest single `bytearray` you can make. Is it the same as `mem_free()`?
- How much RAM does importing a module cost? Measure before and after `import`.
- `micropython.mem_info(1)` draws a map of the heap. Can you spot the fragments?
- A literary clock: each minute, show a quote from a book that mentions the current time, read from a big file one line at a time so the whole file never has to fit in RAM. Set the clock with [[ntp-time]], update it from `run()` (see [[on-time]]), and sleep overnight with [[sleep-with-image]].
