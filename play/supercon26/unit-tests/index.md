---
id: unit-tests
title: "Test your app: automatic checks for its logic, on your laptop and on the badge"
label: Test your app
topic: advanced
workshop: false
needs: [drive-app]
time: 35 min
touches: [lib/]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Pull your app's decisions out into plain functions, write a few checks that
prove they're right, and run all of them in a second, on your laptop or on the badge,
every time you change something.

## You need

- Python 3 on your laptop, and your project folder from [[mount-and-run]]
- [[drive-app]] done: you've split "which button" from "what it does"

## Steps

1. **Find the logic.** Every app has two kinds of code: code that *talks to hardware*
   (reads a button, lights an LED, draws a label) and code that *decides* (which state
   comes next, how many LEDs to light, what to show). Only the second kind is worth
   testing on a laptop, and it's where most bugs live.

   Take the focus timer from [[firmware-diagram]]: 25 minutes of work with one more LED
   lit as each part passes, then 5 minutes of break. The decisions are "how many LEDs?"
   and "what state now?".

2. **Move it into a file with no hardware in it.** Make
   `{{ facts.firmware.folder }}/{{ facts.firmware.lib_dir }}/timer_logic.py`:

   ```python
   OFF, WORK, BREAK = 0, 1, 2
   WORK_MS, BREAK_MS = 25 * 60_000, 5 * 60_000

   def leds_lit(elapsed_ms, n_leds):
       """How many LEDs to light, elapsed_ms into a work period."""
       return min(n_leds, elapsed_ms * n_leds // WORK_MS)

   def next_state(state, elapsed_ms):
       """The state after this one, given how long it's lasted."""
       if state == WORK and elapsed_ms >= WORK_MS:
           return BREAK
       if state == BREAK and elapsed_ms >= BREAK_MS:
           return WORK
       return state
   ```

   No `import machine`, no `self.badge`: just numbers in, numbers out. Your app imports
   it and calls these, and does the LED-lighting itself.

3. **Write the checks.** Make `tests/test_timer_logic.py` in your project folder (next
   to `{{ facts.firmware.folder }}/`, not inside it):

   ```python
   from timer_logic import *

   def test_no_leds_at_start():
       assert leds_lit(0, 8) == 0

   def test_all_leds_at_the_end():
       assert leds_lit(WORK_MS, 8) == 8

   def test_never_more_leds_than_there_are():
       assert leds_lit(WORK_MS * 2, 8) == 8

   def test_work_turns_into_break():
       assert next_state(WORK, WORK_MS) == BREAK

   def test_work_stays_work_until_its_time():
       assert next_state(WORK, WORK_MS - 1) == WORK

   def test_off_stays_off():
       assert next_state(OFF, 10**9) == OFF


   def run(names):
       failed = 0
       for name, test in sorted(names.items()):
           if name.startswith("test_"):
               try:
                   test()
                   print("ok  ", name)
               except AssertionError:
                   failed += 1
                   print("FAIL", name)
       print(f"{failed} failed" if failed else "all passed")

   if __name__ == "__main__":
       run(globals())
   ```

   Each `test_` function checks one thing, with `assert`. The `run` at the bottom calls
   every one of them and says which failed.

4. **Run them on your laptop.**

   ```bash
   PYTHONPATH={{ facts.firmware.folder }}/{{ facts.firmware.lib_dir }} python tests/test_timer_logic.py
   ```

   (On Windows: `set PYTHONPATH=...` first.) Six `ok` lines in well under a second.

5. **Break it on purpose.** In `leds_lit`, remove the `min(n_leds, ...)`. Run the tests
   again. Which one fails? That's the bug a demo would have found for you, an hour into
   a talk.

6. **Run the same tests on the badge.** Same file, real MicroPython:

   ```bash
   mpremote mount {{ facts.firmware.folder }}/{{ facts.firmware.lib_dir }} + run tests/test_timer_logic.py
   ```

   The badge borrows `timer_logic.py` from your laptop and runs the checks itself. If
   something passes on the laptop and fails here, you've found a difference between
   CPython and MicroPython before it found you.

   <!-- TODO(verify): that `mount` + `run` imports from the mounted folder, and that run's __name__ is "__main__" -->

7. **Make it a habit.** Before every copy to the badge, run the tests. Before every
   `git commit`, run the tests. Fix a bug? First write a test that fails because of it,
   then fix it, and watch it pass.

**✅ Done when** you have tests for your app's logic, they all pass on your laptop and on
the badge, and you've seen one fail when you broke the code.

## What just happened

A **unit test** is a small function that calls your code with inputs you chose and
checks the answer. One test proves little. A dozen, run after every change, means you
find out *at once* when an edit breaks something you'd stopped thinking about.

Testing pushed your app into a better shape: **decide in plain functions, act in the
app**. The functions are easy to test because they don't need a badge. The app gets
shorter, because all it does is read the hardware, call a function, and act on the
answer. That's the same split as `on_press()` in [[drive-app]], one step further.

The tests run in both Pythons because they only use plain Python: no `machine`, no
`lvgl`. Code that *does* need hardware is better tested by hand ([[drive-app]],
[[drive-badge]]) or in the [[simulator]].

On your laptop you can also run the same file with **pytest** (`pip install pytest`,
then `pytest tests/`), which finds every `test_` function by itself and explains each
failure in detail. The little `run` function is there so the badge, which doesn't have
pytest, can run them too.

## Stuck?

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: timer_logic` | `PYTHONPATH` must point at the folder that holds `timer_logic.py`. |
| `ImportError: no module named 'machine'` | Something your logic file imports needs the badge. Move it out of the logic file. |
| Nothing prints | The `if __name__ == "__main__":` block is missing, or you imported the file instead of running it. |
| A test fails only on the badge | Integer sizes, string methods and a few library functions differ in MicroPython. Read the failing test. |

## Have fun!

- Test the state machine from [[fsm]]: feed it a list of button presses and check the
  states it goes through.
- Test your conversion from [[real-units]] with the example numbers in the datasheet.
- Let an AI run your tests while it edits your code: [[ai-loop]].
