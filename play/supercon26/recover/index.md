---
id: recover
title: Rescue a badge that crashes at boot
label: Boot rescue
tier: developmental
difficulty: 6
group: debugging
icon: life-ring
needs: [break-and-restore]
time: 15 min
touches: [main.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Get back to `>>>` on a badge whose program crashes or freezes as soon as it
starts, then stop it from happening again.

## You need

- Your badge, connected (see [[repl]])
- A [[backup]]

## Steps

1. **Make a badge that hangs at boot** (so you can practice the rescue). In
   `{{ facts.firmware.user_app }}`, add this as the very first line and save:

   ```python
   while True: pass
   ```

   Press **{{ facts.power.reset_button }}**. The badge never reaches its menu.

2. **Interrupt it.** Click in the shell and press **Ctrl+C**. You should get a traceback
   pointing at your line, then `>>>`. (In Thonny, the **Stop** button does the same.)

3. **Take `main.py` out of the way.** While the badge is stopped, rename it so it won't
   run at the next boot:

   ```python
   import os
   os.rename('main.py', 'main_off.py')
   ```

   Press **{{ facts.power.reset_button }}**. The badge boots straight to `>>>`, with no menu
   and no apps, and you have all the time you want.

4. **Fix the real problem.** Remove the line from step 1 (or restore the file, see
   [[break-and-restore]]).

5. **Put `main.py` back** and restart:

   ```python
   os.rename('main_off.py', 'main.py')
   ```

**✅ Done when** you've rescued the badge from a boot-time hang without help.

## What just happened

At power-up, MicroPython runs `boot.py`, then `main.py`, then (only if `main.py` ever
finishes) gives you `>>>`. The badge's `main.py` never finishes on purpose. That's
what keeps the menu and apps running. So if something it imports hangs or crashes in a
loop, you never get the prompt on your own.

**Ctrl+C** stops whatever's running, so it gets you in *if* the badge stays connected
long enough to hear it. Renaming `main.py` makes sure there's nothing to stop.
{% if facts.firmware.safe_mode %}
This badge also has a **safe mode**: {{ facts.firmware.safe_mode }}. It skips the apps
for you.
{% endif %}

<!-- TODO(diagram): power on → boot.py → main.py (loops forever) → >>> (never reached); Ctrl+C arrow jumping to >>> -->

## Stuck?

| Symptom | Fix |
|---|---|
| Ctrl+C does nothing | Click in the shell first. Press it several times, quickly, right after pressing **{{ facts.power.reset_button }}**. |
| The port keeps vanishing and coming back | The badge is hard-resetting over and over (a crash, or a `machine.reset()` in code). Spam **Ctrl+C** as the port reappears. `mpremote` reconnects quickest. |
| `>>>` appears but Thonny can't list files | Click **Stop** once more. |
| Nothing works, ever | Ask a helper. They can reflash MicroPython, and your [[backup]] gets your work back. |

## Prefer the command line?

```bash
mpremote exec "import os; os.rename('main.py', 'main_off.py')"
mpremote reset
```

## Have fun!

Add a guard to the top of `main.py`: if a button is held at startup (see
[[read-button]]), `raise SystemExit` before any app is imported. You've just invented
safe mode. (Back up `main.py` first, and test the guard *before* you need it.)
