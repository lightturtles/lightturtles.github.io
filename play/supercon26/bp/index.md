---
id: bp
title: "Pause and poke: a bp() breakpoint for the badge"
label: Pause and poke
topic: crashes
workshop: false
needs: [post-mortem]
time: 20 min
touches: [apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Stop your app at a line you choose, type Python to look around, then let it
carry on as if nothing happened.

## You need

- Your app from [[first-app]]
- [[post-mortem]] done

## Steps

1. **Install the helper.** Make a file `{{ facts.firmware.lib_dir }}/bp.py` on the badge:

   ```python
   def bp(g):
       while (s := input("dbg> ")):
           try: exec(s, g)
           except Exception as e: print(repr(e))
   ```

   That's the whole debugger: read a line, run it, repeat, until you enter an empty line.

2. **Set a breakpoint.** In your app, import it and call it where you want to stop.
   Pass it the names you want to see:

   ```python
   from bp import bp        # at the top of the file

       def run_background(self):
           self.ticks += 1
           if self.ticks == 3:
               g = globals().copy()
               g["self"] = self
               bp(g)
   ```

3. Save, **Ctrl+D**, and wait for tick 3. The shell shows `dbg>`. Look around:

   ```
   dbg> print(self.ticks)
   dbg> print(self.__dict__)
   dbg> print([n for n in dir(self) if not n.startswith("_")])
   ```

   `exec` runs statements, so wrap anything you want to see in `print()`.

4. **Notice what stopped.** While `dbg>` is waiting, press the badge's buttons, watch
   the LEDs and the screen. *Everything* is paused, not just your app.

5. **Change something, then carry on.** Set a value and press **Enter** on an empty
   line:

   ```
   dbg> self.ticks = 100
   dbg>
   ```

   Your app continues from the line after `bp(g)`, and the next tick prints 101.

6. **Locals need passing in.** Inside a function, try `bp(locals())`. In MicroPython,
   `locals()` returns the module's globals, not the function's variables. That's why
   step 2 builds `g` by hand: add every local you want to see (`g["n"] = n`).

7. **Take it out** before you unplug: `bp()` waits for a keyboard that isn't there,
   forever.

**✅ Done when** you've paused your app, read and changed a variable at `dbg>`, and
carried on.

## What just happened

`input()` waits for a line from the USB serial port, and it waits by **blocking**: no
`await`, so no other task gets a turn (see [[asyncio-basics]]). The whole badge freezes
mid-call with every variable intact. That's exactly what a breakpoint should do.

`exec(s, g)` runs your line using `g` as its global names. Two things follow:

- **Changing an object sticks.** `self.ticks = 100` changes the real app, because
  `g["self"]` *is* your app.
- **Rebinding a name doesn't.** `n = 5` only changes `g`, your copy of the names. The
  function's own `n` is untouched.

Compared with the alternatives:

| | `print` | [[post-mortem]] | `bp()` |
|---|---|---|---|
| When you look | where you planned | after it's stopped | where you planned |
| Can carry on | yes | no | yes |
| Can change things | no | only to look | yes |

Thonny's step-by-step debugger only works with Python on your laptop, not on the
badge. `bp()` is the closest thing, in four lines.

## Stuck?

| Symptom | Fix |
|---|---|
| `dbg>` never appears | That line isn't reached. Add a `print` just before `bp(g)` to check. |
| Typing a name shows nothing | `exec` doesn't echo. Use `print(name)`. |
| `NameError` at `dbg>` | It's a local that wasn't put in `g`. Add it before calling `bp(g)`. |
| Badge seems dead unplugged | A `bp()` is waiting for input. Remove it, or guard it: `if DEBUG: bp(g)`. |
| `SyntaxError` on `:=` | Very old MicroPython. Use `while True: s = input("dbg> ")` and `if not s: break`. |

## Have fun!

- Make it echo values: `try: print(eval(s, g))` first, and fall back to `exec` on
  `SyntaxError`.
- A conditional breakpoint: `if self.value > 30: bp(g)` stops only when something's odd.
- Break on an error: call `bp(g)` inside the `except` from [[post-mortem]], so you can
  look around at the moment it went wrong.
