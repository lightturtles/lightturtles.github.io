---
id: post-mortem
title: Post-mortem (after Ctrl+C, inspect an app's state in the REPL)
label: Post-mortem
tier: developmental
difficulty: 6
group: debugging
icon: magnifier
needs: [break-and-restore]
time: 20 min
touches: [apps/nametag.py]     # TODO: facts.name_badge.file
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Stop the badge mid-run and look inside a running app: what's in its
variables *right now*?

## You need

- The app file from [[name-badge]], open in Thonny from the badge
- A [[backup]]

## Steps

1. **Leave yourself a handle.** Apps are objects that `main.py` creates and keeps to
   itself, so you can't reach them from `>>>` yet. Find the app's `__init__` method in
   `{{ facts.name_badge.file }}`, and add these two lines at the end of it (indented
   to match):

   ```python
   global me
   me = self
   ```

   <!-- TODO(verify): if this year's firmware keeps its apps somewhere reachable
        (e.g. a module-level list), use that instead and skip this step -->

2. Save, press **Ctrl+D**, and open **{{ facts.name_badge.app }}** on the badge. Use it for a
   moment.

3. **Stop the world.** Click in the shell and press **Ctrl+C**. Everything freezes
   exactly as it was.

4. **Look inside.** The app's module is already loaded; importing it again just hands it
   to you:

   ```python
   import {{ facts.name_badge.file | remove: ".py" | replace: "/", "." }} as m
   m.me                # the app object
   m.me.__dict__       # every variable it holds, and its value
   ```

5. Pick one value from that list and explain it. Is it what you expected? Change
   something on the badge, run `m.me.__dict__` again, and spot the difference.
   (You'll need **Ctrl+D**, then the app, then **Ctrl+C** again.)

6. **More places to look:**

   ```python
   import sys
   sys.modules.keys()   # every module that's loaded
   import micropython
   micropython.mem_info()   # how much RAM is in use
   ```

7. Take the two lines out again when you're done, or keep them; they're harmless.

**✅ Done when** you can read one of the app's variables after Ctrl+C and explain its value.

## What just happened

**Ctrl+C** raises a `KeyboardInterrupt` wherever the program happens to be. The badge's
main loop dies, but *nothing is cleaned up*: every object stays in RAM until the next
reset. That's what makes a post-mortem possible.

`global me` stores the app in a module-level variable, so it outlives the function that
made it. And because Python loads each module only once, `import` gives you the very
same module the badge is using.

You can't resume after Ctrl+C. The loop that ran the apps is gone. Look all you like,
then **Ctrl+D** to start over.

<!-- TODO(diagram): main.py's main() holding app objects; `me` as a second arrow from the module to the same object; REPL reaching in through the module -->

## Stuck?

| Symptom | Fix |
|---|---|
| `AttributeError: ... has no attribute 'me'` | The app's `__init__` hasn't run. Did you **Ctrl+D** and open the app first? |
| `SyntaxError` at boot | Check the indentation of the two new lines. See [[break-and-restore]]. |
| `__dict__` is huge | Look at one value at a time: `m.me.some_name`. |

## Have fun!

- Catch a bug in the act: after the badge prints a traceback, it's sitting at `>>>`
  with everything still in RAM. What were the variables when it crashed?
- Use `dir(m.me)` to find its *methods* too. Can you call one from `>>>`?
