---
id: fsm
title: Break your app's work into states (finite state machines)
label: Break work into states
topic: write-app
workshop: false
needs: [hog-the-cpu, asyncio-basics]
time: 30 min
touches: [apps/userA.py, apps/base_app.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Turn a job that "waits for things" into a state machine that does one small
step per call, so your app never freezes the badge.

## You need

- Your app from [[first-app]], and the sliced counter from [[hog-the-cpu]]
- The LED setup from [[one-led]] (we'll use the first LED)

## Steps

1. **Write it the blocking way first, on paper.** Here's a "doorbell": press
   **{{ facts.buttons.app_1_label }}**, the LED flashes 5 times, then it ignores the
   button for a while so nobody can spam it:

   ```python
   # Don't type this in: it freezes the badge for several seconds.
   if button pressed:
       for i in range(5):
           led on;  wait
           led off; wait
       ignore the button for a while
   ```

   Every *wait* is a place the badge would freeze. Circle them.

2. **Name the states.** Each circled wait becomes "a state where we're waiting for
   something." Here there are three:

   | State | What it's waiting for | What moves it on |
   |---|---|---|
   | `IDLE` | a button press | **{{ facts.buttons.app_1_label }}** → `FLASHING` |
   | `FLASHING` | enough flashes | 10 calls done → `COOLDOWN` |
   | `COOLDOWN` | time to pass | 20 calls done → `IDLE` |

   <!-- TODO(diagram): three circles IDLE → FLASHING → COOLDOWN → IDLE, with the arrows labeled as in the table -->

3. **Write it as one step per call.** In `{{ facts.firmware.user_app }}`:

   ```python
   from machine import Pin
   import neopixel

   IDLE, FLASHING, COOLDOWN = 0, 1, 2

   class App(BaseApp):
       def __init__(self, name, badge):
           super().__init__(name, badge)
           self.foreground_sleep_ms = 100        # one call every 0.1 s, roughly
           self.np = neopixel.NeoPixel(Pin({{ facts.leds.pin }}), {{ facts.leds.count }})
           self.state = IDLE
           self.count = 0

       def run_foreground(self):
           if self.state == IDLE:
               if {{ facts.buttons.app_1 }}:
                   print("ding dong")
                   self.state, self.count = FLASHING, 0

           elif self.state == FLASHING:
               on = self.count % 2 == 0
               self.np[0] = (32, 32, 0) if on else (0, 0, 0)
               self.np.write()
               self.count += 1
               if self.count == 10:
                   self.state, self.count = COOLDOWN, 0

           elif self.state == COOLDOWN:
               self.count += 1
               if self.count == 20:
                   self.state = IDLE

           if {{ facts.buttons.home }}:           # works in every state
               self.np[0] = (0, 0, 0); self.np.write()
               self.switch_to_background()
   ```

   <!-- TODO(verify): foreground_sleep_ms is the 2025 name for the foreground period -->

4. Save, **Ctrl+D**, open your app, press **{{ facts.buttons.app_1_label }}**. Try going home
   in the middle of the flashing. It works, because no state ever waits.

5. **Add a state.** Make a long press different from a short one, or add a `PAUSED`
   state on **{{ facts.buttons.app_2_label }}**. Draw it in your table *first*, then code it.

**✅ Done when** your app has at least three states, you can draw them, and the home
button works in every one.

## What just happened

A **finite state machine** (FSM) is a program written as: "which state am I in, and
what moves me to the next one?" Instead of waiting *inside* your code, you remember
*where you were* in a variable (`self.state`) and return. The badge calls you again,
and you pick up where you left off.

**Where state lives.** Local variables vanish when your method returns, so anything
you need next call goes somewhere that lasts:

| Where | Lasts | Use it for |
|---|---|---|
| a local (`n = 0`) | until `return` | scratch work in one call |
| an instance variable (`self.n`) | as long as the app | this app's state |
| a module variable (`n` at the top of a file) | until reset | one thing shared by every app that imports the file (see [[share-hardware]]) |

**The rules of cooperative scheduling**, now that you've broken all of them once:

1. **Return quickly.** A few milliseconds per call. Measure it (see [[on-time]]).
2. **Never wait inside a call.** No `time.sleep()`, no `while` waiting for a button or a
   network reply. Make it a state instead.
3. **Keep state in `self`**, not in locals.
4. **Every state handles "leave."** If one state ignores the home button, users get stuck.

Counting calls is a rough clock: if the badge is busy, calls come late, and your
flashes stretch. [[on-time]] fixes that with real timestamps.

## Stuck?

| Symptom | Fix |
|---|---|
| Nothing happens on the button | Is the `if` inside the `IDLE` branch? Check the indentation. |
| It flashes forever | The count check never matches: you reset `count` in the wrong place, or used `>` where you needed `==` (or the other way round). |
| `NameError: IDLE` | The state names must be at the top of the file, outside the class. |
| The LED stays on after going home | Turn it off before `switch_to_background()`. |

## Have fun!

- Print the state every time it changes: a one-line trace of your FSM.
- Rewrite the counter from [[hog-the-cpu]] as an FSM: `IDLE`, `COUNTING`, `SHOWING_RESULT`.
- Games are FSMs too: rock-paper-scissors is `WAITING`, `COUNTDOWN`, `REVEAL`.
- A reaction game: `WAIT` (a random delay) → `GO` → `RESULT`. The e-ink is far too slow to say "GO!", so the LEDs do it and the screen shows your time (see [[on-time]] and [[eink-refresh]]).
- A choose-your-own-adventure story: each page is a state and each button is a choice. Keep the story in a dict (or a JSON file) so you can add pages without touching the code.
