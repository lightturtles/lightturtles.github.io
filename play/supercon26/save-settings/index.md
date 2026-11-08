---
id: save-settings
title: Save data across reboots with the config module
label: Save across reboots
topic: write-app
workshop: false
needs: [first-app]
time: 20 min
touches:
  - lib/json_configs.py   # load(), store(dict), append(entry, name); default file data/panel_config.json
  - main.py#main          # loads and re-stores the same file on every start-up (load_counter)
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Store a value on the badge that's still there after you pull the power.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- A recent backup (see [[backup]]); you're about to change a file on the badge

## Steps

1. Load the badge's settings module and see what it offers:

   ```python
   import {{ facts.config.module }} as config
   dir(config)
   ```

   Among the usual `__…__` names: `load`, `store` and `append`.

2. See what's already saved:

   ```python
   config.load()
   ```

   Something like `{'load_counter': 7}`: the badge counts its own start-ups here.

3. Save a value:

   ```python
   config.append((0, 32, 32), "favorite_color")
   ```

   `append` loads the file, adds (or replaces) one entry, and writes it all back.

4. Read it back:

   ```python
   config.load()["favorite_color"]
   ```

   You get `[0, 32, 32]`, a list. You saved a tuple, but the file is JSON, and JSON only
   has lists.

5. Power-cycle the badge (see [[resets]]), reconnect, press **Ctrl+C**, and read it again:

   ```python
   import {{ facts.config.module }} as config
   config.load()["favorite_color"]
   ```

6. Use it. Light the LEDs in your saved color (see [[one-led]]):

   ```python
   from lib.led_bar import leds
   leds.fill(config.load()["favorite_color"])
   ```

**✅ Done when** your value comes back after a power cycle.

## What just happened

Variables live in **RAM**, which forgets everything when the power goes (or even on a
soft reset). The filesystem lives in **flash**, which keeps its contents with no power.
`config.append()` and `config.store()` write a dictionary to a file,
`{{ facts.config.file }}`, as JSON, and `config.load()` reads it back.

Peek at it yourself:

```python
print(open("{{ facts.config.file }}").read())
```

You share this file with the badge. `main.py` loads it on every start-up, adds one to
`load_counter`, and stores it again (keeping your entries). So:

- **Use `append`, or `load` → change → `store`.** `config.store({"favorite_color": …})` on
  its own throws away everything else in the file, including the counter. (The badge
  then thinks it's brand new, and shows its first-boot splash screen.)
- **Pick names nobody else will.** Prefix them with your app's name: `"my_app_color"`.
- **Want a file of your own?** Every function takes a file name too:
  `config.store({...}, "/data/my_app.json")`, `config.load("/data/my_app.json")`.

Flash wears out after many thousands of writes to the same spot. Save when a setting
*changes*, not in a loop that runs every second.

<!-- TODO(diagram): RAM (variables, lost at reset) ↔ config.store()/load() ↔ flash file (kept) -->

## Stuck?

| Symptom | Fix |
|---|---|
| `ImportError` | It's `lib.json_configs`, with an underscore and an *s*. |
| `KeyError` | The key name must match exactly, including capitals. `config.load().get("name")` gives `None` instead of an error. |
| `OSError: [Errno 2] ENOENT` with your own file | It doesn't exist yet. `store()` to it once before you `load()` it. |
| The first-boot splash screen came back | Something stored the file without `load_counter`. Harmless. |
| Badge won't start after editing the file by hand | `main.py` can't read broken JSON. Fix the file from your [[backup]], or delete it (`import os; os.remove("{{ facts.config.file }}")`) and restart. |

## Prefer the command line?

```bash
mpremote fs cat :{{ facts.config.file }}
```

## Have fun!

- Count how many times *your app* has been opened: read a number, add 1, save it.
- Save your name from [[name-badge]] so you can change it without editing the app's code.
- An e-reader: page through a text file with the buttons, and save your page so the book opens where you left off. Read one page at a time, not the whole book (see [[out-of-memory]]).
