---
id: save-settings
title: Save data across reboots with the config module
label: Save across reboots
topic: write-app
workshop: false
needs: [first-app]
time: 20 min
touches: []                     # TODO: the config module's source file
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Store a value on the badge that's still there after you pull the power.

<!-- TODO(verify): every call to `config` below is a guess at the API. Check it against the firmware. -->

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- A recent backup (see [[backup]]); you're about to change a file on the badge

## Steps

1. Load the badge's settings module and see what it offers:

   ```python
   import {{ facts.config.module }} as config
   dir(config)
   ```

2. Save a value:

   ```python
   config.set("favorite_color", (0, 32, 32))
   config.save()
   ```

3. Read it back:

   ```python
   config.get("favorite_color")
   ```

4. Power-cycle the badge (see [[resets]]), reconnect, press **Ctrl+C**, and read it again:

   ```python
   import {{ facts.config.module }} as config
   config.get("favorite_color")
   ```

5. Use it. Light the LEDs in your saved color (setup from [[one-led]]):

   ```python
   np.fill(config.get("favorite_color"))
   np.write()
   ```

**✅ Done when** your value comes back after a power cycle.

## What just happened

Variables live in **RAM**, which forgets everything when the power goes (or even on a
soft reset). The filesystem lives in **flash**, which keeps its contents with no power.
`config.save()` writes your settings to a file, `{{ facts.config.file }}`, and the
module reads that file back the next time it's imported.

Peek at it yourself:

```python
print(open("{{ facts.config.file }}").read())
```

Flash wears out after many thousands of writes to the same spot. Save when a setting
*changes*, not in a loop that runs every second.

<!-- TODO(diagram): RAM (variables, lost at reset) ↔ config.save()/import ↔ flash file (kept) -->

## Stuck?

| Symptom | Fix |
|---|---|
| `ImportError` | Check the module name with `help('modules')`, or see [[explore-badge]]. |
| Value gone after reboot | Did you call `config.save()`? |
| `get` returns `None` | The key name must match exactly, including capitals. |
| Badge won't boot after editing the file by hand | Restore the file from your [[backup]], or delete it and reboot to get defaults. |

## Prefer the command line?

```bash
mpremote fs cat :{{ facts.config.file }}
```

## Have fun!

- Count how many times the badge has booted: read a number, add 1, save it.
- Save your name from [[name-badge]] so it survives a reflash of your app.
- An e-reader: page through a text file with the buttons, and save your page so the book opens where you left off. Read one page at a time, not the whole book (see [[out-of-memory]]).
