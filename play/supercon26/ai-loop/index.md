---
id: ai-loop
title: "Let an AI run the tests: an AI coding agent that checks its own work"
label: Let an AI run the tests
topic: advanced
workshop: false
needs: [unit-tests, simulator]
time: 30 min
touches: [tests/]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Give an AI coding agent what it needs to check its own changes to your app
(your tests, the simulator, and the badge's rules), so it hands you code that already
passes, not code that only looks right.

## You need

- Your project folder in git (see [[mount-and-run]]), with tests from [[unit-tests]]
- The [[simulator]]
- An AI coding agent that can run commands in a terminal (Claude Code, or similar)

## Steps

1. **Commit first.** The agent is about to edit your files. Make sure you can get back:

   ```bash
   git status          # nothing uncommitted
   ```

2. **Write it a briefing.** Agents read a file of instructions at the top of the project
   (Claude Code reads `CLAUDE.md`; many others read `AGENTS.md`). Make one:

   ```markdown
   # Badge app

   MicroPython app for the Supercon badge. My code: {{ facts.firmware.folder }}/{{ facts.firmware.user_app }}
   and {{ facts.firmware.folder }}/{{ facts.firmware.lib_dir }}/timer_logic.py. Don't edit any other file in {{ facts.firmware.folder }}/.

   ## Check every change
   - Tests: PYTHONPATH={{ facts.firmware.folder }}/{{ facts.firmware.lib_dir }} python tests/test_timer_logic.py
     All must pass. Add a test for any logic you add or fix.
   - Simulator: python sim.py {{ facts.firmware.user_app }}     (TODO: real command)

   ## Rules for app code (it runs on a microcontroller, cooperatively scheduled)
   - run_foreground()/run_background() must return quickly: no time.sleep, no waiting loops.
   - Keep state in self, not in locals.
   - Decisions go in plain functions in timer_logic.py (no hardware imports), so they can be tested.
   - MicroPython, not CPython: no typing, dataclasses or f-string = specifiers.
   ```

   <!-- TODO(simulator): real command, and whether it can run headless for an agent -->

   The rules are the ones from [[firmware-diagram]]. An agent that knows desktop Python
   but not the badge will happily write `time.sleep(1)`. This is how it knows not to.

3. **Ask for a change, and say how to check it.**

   > Add a long break: after every 4 work periods, the break is 15 minutes instead of 5.
   > Write the tests first, then change timer_logic.py until they pass.

   Watch what it does. A good run looks like: writes new tests, runs them (they fail),
   changes the code, runs them again (they pass), tells you what it did.

4. **Read the diff yourself.**

   ```bash
   git diff
   ```

   Do the new tests check what you asked for? Did it touch files it shouldn't? Did it
   make a test pass by changing the *test*? If you don't understand a line, ask it.

5. **Try it on the badge.** The tests and the simulator are a laptop's view. Copy it
   over (see [[mount-and-run]]) and use it for real. Timing and hardware bugs only show
   up here (see [[simulator]] for what the laptop can't tell you).

6. **Commit, or throw it away.**

   ```bash
   git commit -am "Long break after every 4 work periods"
   # or, if it went wrong:
   git checkout .
   ```

**✅ Done when** an agent has made a change to your app, run the tests to prove it, and
you've read the diff, tried it on the badge, and committed it.

## What just happened

An AI writing code without running it is guessing, and its guesses look exactly as
confident whether they're right or wrong. Tests turn the guess into a loop: change,
run, read the failure, change again. The agent does the tedious part of that loop; you
decide what "right" means (by writing or approving the tests) and whether the result is
good (by reading the diff and trying it).

Everything that made your app easy for *you* to test made it easy for the agent:
logic in plain functions ([[unit-tests]]), a way to run the app without the badge
([[simulator]]), and output it can read (the `log` lines from [[better-prints]]).

**Keep the badge in your hands.** An agent *can* run `mpremote` too, and copy files to
the badge or run tests on it. Let it only if you'd let a stranger do the same, and keep
your agent asking before it runs commands. Everything it changes on your laptop is
undone by `git checkout`; changes on the badge aren't (see [[backup]]).

## Stuck?

| Symptom | Fix |
|---|---|
| It ignores your rules | Is the briefing named what your agent reads? Ask it: "what does CLAUDE.md say?" |
| It edits firmware files | Say so in the briefing, and `git checkout` those files. |
| The tests pass, but the feature is wrong | The tests check the wrong thing. Fix the tests yourself, then ask again. |
| It changed a test to make it pass | Tell it the tests are the spec, and not to change them without asking. |
| Works in tests, fails on the badge | Timing, memory, or a MicroPython difference. Add what you learned to the briefing. |

## Have fun!

- Ask the agent to find a bug from a traceback: paste it (see [[break-and-restore]]) and
  let it reproduce the crash in a test before fixing it.
- Ask it to add tests for code you already wrote. Do they find anything?
- Keep a "lessons learned" list in the briefing: every time the agent trips on the badge,
  add one line.
