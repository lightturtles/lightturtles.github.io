---
id: repl-setup
title: "A faster REPL: what's left after Ctrl+C, and reloading without a reboot"
label: A faster REPL
topic: workflow
workshop: false
needs: [map-firmware]
time: 20 min
touches: [main.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(dev.py): a dev.py helper for this badge (setup shortcuts, reload, etc.) is still
     being designed. Add a step for it here once it exists. -->

**Goal:** Spend less time rebooting and retyping: reuse what the badge already set up,
paste big blocks cleanly, and reload a file you've changed without restarting.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- [[map-firmware]] done, so you know `main.py`

## Steps

1. **What's left after Ctrl+C?** Let the badge start normally, then press **Ctrl+C**
   and look around:

   ```python
   dir()
   ```

   Those are `main.py`'s leftovers: `main.py` and the REPL share one set of global
   names. Anything `main.py` made at the top level of the file is still there, ready
   to use. Things it made *inside a function* (like `async def main()`) are gone,
   unless something else kept hold of them.

   <!-- TODO(verify): which useful objects this year's main.py leaves at the top level -->

2. **Reach the rest through modules.** A module is only loaded once, so importing it
   again hands you the very same one, with everything the badge put in it:

   ```python
   {{ facts.firmware.badge_import }}
   import sys
   sorted(sys.modules)             # every module the badge has loaded
   ```

3. **Paste big blocks cleanly.** Press **Ctrl+E** (paste mode), paste, then **Ctrl+D**.
   The REPL takes it all as one block: no auto-indent mangling it.

4. **Run a file without importing it.** Useful for a scratch script:

   ```python
   exec(open("test.py").read())
   ```

   Or from your laptop, without copying the file to the badge at all:

   ```bash
   mpremote run test.py
   ```

5. **Reload a module you changed.** Edit and save a file (say, a helper in
   `{{ facts.firmware.lib_dir }}/`), then, without rebooting:

   ```python
   import sys
   sys.modules.pop("myhelper", None)   # forget the old version
   import myhelper                      # load the new one
   ```

   For a module in a folder, use the full name: `sys.modules.pop("apps.userA", None)`,
   then `import apps.userA`.

6. **Know the catch.** Objects made *before* the reload still run the old code. Make
   new ones after reloading (see [[drive-app]]).

**✅ Done when** you've used something `main.py` left behind, and reloaded a changed
file without a reset.

## What just happened

A soft reset (see [[resets]]) throws away everything in RAM and runs `main.py` again.
That's safe but slow, and it loses whatever you'd set up at the REPL. The tricks here
keep the session alive instead.

`sys.modules` is the list of loaded modules. `import` checks it first, and only reads
the file if the name isn't there. Removing a name forces a fresh read. Python's
`importlib.reload()` does the same on a desktop; MicroPython doesn't have it, so you do
it by hand.

## Stuck?

| Symptom | Fix |
|---|---|
| `dir()` shows almost nothing | `main.py` keeps everything inside functions. Use step 2 instead. |
| Reloaded, but nothing changed | You're using an object made before the reload. Make a new one. Or the file wasn't saved to the badge. |
| Paste mode shows `===` lines | That's paste mode. Finish with **Ctrl+D**, or **Ctrl+C** to cancel. |

## Have fun!

- Write a one-line `reload(name)` helper in `{{ facts.firmware.lib_dir }}/`. (Watch out:
  `__import__("apps.userA")` returns the `apps` package, not `userA`.)
- What's in `dir()` right after a reset with `main.py` renamed (see [[recover]])?
  Compare it with step 1.
