---
id: pass-data
title: Pass data between tasks (shared variables, Event, ThreadSafeFlag, queues)
label: Passing data between tasks
topic: write-app
workshop: false
needs: [fsm]
time: 30 min
touches: [apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Get data from one part of the badge to another safely, and know which tool
to reach for: a plain variable, an `Event`, a `ThreadSafeFlag`, or a queue.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- [[asyncio-basics]] and [[fsm]] done

## Steps

1. **A shared variable.** Press **Ctrl+C**, then paste this (paste mode, **Ctrl+E**,
   if the indentation goes wrong). One task makes "readings", another shows them:

   ```python
   import asyncio, random
   asyncio.new_event_loop()

   latest = None          # shared between the two tasks

   async def sensor():
       global latest
       for i in range(10):
           latest = random.randint(20, 30)
           await asyncio.sleep_ms(300)

   async def screen():
       for i in range(6):
           print("showing", latest)
           await asyncio.sleep_ms(500)

   async def both():
       await asyncio.gather(sensor(), screen())

   asyncio.run(both())
   ```

   The screen sees *a* recent reading, not every one. For a thermometer, that's fine.

2. **Lost events.** Now pretend `sensor` reports button presses instead. Change the
   sleep to 100 ms. Count: how many values did `screen` never show? If each one was a
   press, those presses are gone.

3. **A queue keeps every item.** Use a `deque` (a list that's quick at both ends) as a
   queue. The producer appends; the consumer takes everything waiting:

   ```python
   from collections import deque
   q = deque((), 20)             # holds up to 20 items

   async def sensor():
       for i in range(10):
           q.append(i)
           await asyncio.sleep_ms(100)

   async def screen():
       for i in range(6):
           while q:
               print("got", q.popleft())
           await asyncio.sleep_ms(500)

   asyncio.run(both())
   ```

   Nothing lost. If `screen` falls more than 20 behind, the oldest items fall off.
   (Want an error instead? `deque((), 20, 1)` raises `IndexError` when it's full.)

4. **An Event wakes a task up.** Polling every 500 ms is slow to react. An `Event` lets
   a task sleep until there's something to do:

   ```python
   ev = asyncio.Event()

   async def sensor():
       for i in range(5):
           await asyncio.sleep_ms(700)
           q.append(i)
           ev.set()                 # "there's something new"

   async def screen():
       for i in range(5):
           await ev.wait()          # sleeps until set()
           ev.clear()
           while q:
               print("got", q.popleft())

   asyncio.run(both())
   ```

   Each item prints the moment it arrives.

5. **From outside asyncio: ThreadSafeFlag.** Interrupt handlers and radio callbacks
   don't run as tasks, and mustn't touch an `Event`. They get a `ThreadSafeFlag`
   instead:

   ```python
   flag = asyncio.ThreadSafeFlag()
   # in the interrupt handler:  flag.set()
   # in a task:                 await flag.wait()   (clears itself)
   ```

   You'll use this for real in [[interrupts]].

6. **In an app.** Your app's methods aren't `async`, so they can't `await`. They don't
   need to: `run_foreground()` checks the queue each call (`while q: ...`), and the
   task on the other end does the `await`ing. That's the shape of [[espnow-in-app]].

7. Press **Ctrl+D** to get the badge back.

**✅ Done when** you've lost data with a shared variable, then kept all of it with a
queue, and can say which tool fits: a temperature, a button press, and a message
from an interrupt.

## What just happened

**Why shared variables are usually safe here.** asyncio is cooperative: a task only
gives up the processor at an `await`. Between two `await`s, nobody else runs, so
nobody can see a half-updated value. On a desktop with threads, that's not true, and
you'd need locks.

**Which tool, when:**

| You want | Use | Because |
|---|---|---|
| the *latest* value (temperature, battery) | a shared variable | old values don't matter |
| *every* item, in order (presses, messages) | a queue (`deque`) | nothing gets overwritten |
| to *wake* a task when something happens | `asyncio.Event` | it sleeps instead of polling |
| to wake a task from an interrupt or callback | `asyncio.ThreadSafeFlag` | it's safe to `set()` from outside the scheduler |

**The one trap:** an `await` in the middle of an update. If a task changes two
variables with an `await` between them, another task can run in the gap and see one
new value and one old one. Do the whole update, then `await`.

<!-- TODO(diagram): producer task → queue → consumer; Event as a doorbell between them; ISR → ThreadSafeFlag → task -->

## Stuck?

| Symptom | Fix |
|---|---|
| `NameError` in `both()` | `both()` uses the latest `sensor` and `screen` you defined; paste all three again. |
| `screen` waits forever | Nothing called `ev.set()`, or `sensor` finished first. That's fine at the REPL: **Ctrl+C**. |
| `IndexError` on `append` | You made it with the overflow flag (`, 1`), and it's full. Make it bigger, or take items out faster. |
| `TypeError` making the deque | MicroPython's `deque` needs both arguments: `deque((), 20)`. |

## Have fun!

- Make two producers share one queue. Tag each item with who sent it.
- What happens if the consumer is faster than the producer? Slower? Print `len(q)`.
