---
id: asyncio-basics
title: Run two asyncio tasks that take turns, from the REPL
label: Take turns with asyncio
tier: core
difficulty: 5
group: firmware-internals
icon: shuffle
needs: [repl]
time: 15 min
touches: [apps/base_app.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Watch two pieces of code share one processor, and see what happens when one
of them refuses to share.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])

## Steps

1. Click in the shell and press **Ctrl+C** to stop the badge's own program.

2. Start with a clean slate, so the badge's stopped tasks don't wake up again:

   ```python
   import asyncio, time
   asyncio.new_event_loop()
   ```

3. Paste this in one go (in Thonny, use **Ctrl+E** for paste mode first if the
   indentation goes wrong). It defines two tasks: one prints every second, the other
   every 0.3 seconds.

   ```python
   async def tick():
       for i in range(5):
           print("tick", i)
           await asyncio.sleep(1)

   async def tock():
       for i in range(15):
           print("        tock", i)
           await asyncio.sleep(0.3)

   async def both():
       await asyncio.gather(tick(), tock())
   ```

4. Run them together:

   ```python
   asyncio.run(both())
   ```

   The ticks and tocks interleave, about three tocks per tick. Both loops are
   "running at once" on one processor.

5. **Now break it.** Redefine `tock` with `time.sleep` instead of `await asyncio.sleep`:

   ```python
   async def tock():
       for i in range(15):
           print("        tock", i)
           time.sleep(0.3)
   ```

   Run `asyncio.run(both())` again. Now all 15 tocks print in a row, and `tick` only
   gets a turn once `tock` is done (or almost). `time.sleep` waits *without letting
   anyone else run*.

6. **Break it completely.** Replace the whole body of `tock` with `while True: pass`
   and run again. Nothing prints at all after the first tick, ever. Press **Ctrl+C**.

7. **Find the same pattern in the badge.** Open `apps/base_app.py` and find
   `async def run(self)`. It's a loop just like yours:

   ```python
   while True:
       if self.active_foreground:
           self.run_foreground()                       # your code runs here...
           await aio.sleep_ms(self.foreground_sleep_ms) # ...then everyone else gets a turn
   ```

   Every app is a task like `tick`. `run_foreground()` is a plain method (no `async`), so
   it can't `await`. It gets its turn, and the next turn only comes once it **returns**.

8. Press **Ctrl+D** to get the badge back.

**✅ Done when** you can make one task stall the other on purpose, and explain why
`time.sleep` and `asyncio.sleep` behave differently.

## What just happened

**asyncio** is **cooperative multitasking**: tasks take turns, and a task only gives up
the processor when it says so, at an `await`. There's no referee that can step in and
pause it. That's what *cooperative* means.

`await asyncio.sleep(1)` says "wake me in a second, and let the others run meanwhile."
`time.sleep(1)` says "do nothing for a second," and that includes not letting anyone
else run.

On the badge, `main.py` runs dozens of tasks this way: every app, the menu, the button
reader, the screen updater. They only *look* simultaneous because each one takes a
short turn and hands the processor back. One greedy task freezes them all. You'll do
that on purpose in [[hog-the-cpu]].

<!-- TODO(diagram): timeline with two lanes (tick, tock); blocks of "running" separated at each await; second timeline where tock's time.sleep blocks tick -->

## Stuck?

| Symptom | Fix |
|---|---|
| `IndentationError` when pasting | Use paste mode: **Ctrl+E**, paste, **Ctrl+D**. |
| Menu messages or heartbeats show up mixed in with yours | You skipped `asyncio.new_event_loop()`, so the badge's own tasks woke up. Ctrl+C, then start from step 2. |
| `asyncio.run(...)` returns right away | You defined `both()` without `await`ing `gather`. |
| Typing does nothing during step 6 | That's the point! **Ctrl+C**. |

## Have fun!

- Add a third task. Give each a different period. Can you predict the print order?
- Make `tock` wait for `tick` using an `asyncio.Event`: `tick` calls `ev.set()`, and
  `tock` does `await ev.wait()`.
- Time how long `tock` really sleeps: print `time.ticks_ms()` each pass. Is it exactly
  300 ms?
