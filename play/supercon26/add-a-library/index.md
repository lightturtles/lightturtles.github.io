---
id: add-a-library
title: Add a MicroPython library to the badge
label: Add a library
topic: i2c
workshop: true
needs: [i2c-scan]
time: 10 min
touches: []                     # nothing in the firmware; relies on /lib being on sys.path
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Put a driver for your sensor on the badge, and `import` it.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- Your sensor's address, from [[i2c-scan]]

## Steps

1. **Where does `import` look?**

   ```python
   import sys
   sys.path
   ```

   One of the entries is `'/{{ facts.firmware.lib_dir }}'`. That folder is for libraries.
   (The badge's own building blocks live there too, like `lib/sao.py`.)

2. **Pick your sensor's library.** The workshop wrote one small driver for each sensor:

   | Sensor | Library file |
   |---|---|
   {% for s in facts.sensors %}| {{ s[1].name }} ({{ s[1].what }}) | [`{{ s[1].driver }}.py`]({{ facts.drivers_url }}{{ s[1].driver }}.py) |
   {% endfor %}

3. **Copy it to the badge**, either way:

   **Thonny:** download the file to your laptop (right-click the link above → **Save
   link as…**). In Thonny's bottom (badge) pane, open `{{ facts.firmware.lib_dir }}/`. In
   the top pane, find the file, right-click → **Upload to /{{ facts.firmware.lib_dir }}**.

   **`mpremote`:** one line does both. It needs internet on the *laptop*, not on the badge
   (swap in your sensor's file name):

   ```bash
   mpremote mip install {{ facts.drivers_url }}aht20.py
   ```

   <!-- TODO(screenshot): Thonny, driver file in the top pane, "Upload to /lib" in the menu -->

4. **Import it.** Press **Ctrl+C** first if the badge's program is running, then use the
   file's name without `.py`:

   ```python
   import aht20         # your sensor's file name
   dir(aht20)
   ```

   Spot the class with your sensor's name in it, in capitals. That's what you'll use
   in [[use-a-library]].

**✅ Done when** `import` works with no error, and `dir()` shows your sensor's class.

## What just happened

`import x` searches each folder in `sys.path` for `x.py` (or a folder `x/`), in order.
`/{{ facts.firmware.lib_dir }}` is on that list, so anything you put there can be
imported from anywhere: the REPL, or any app.

The library is one of *your* files now (see [[backup]]): it's not in the official folder,
so back it up, and [[start-fresh]] will delete it.

Libraries written for regular Python usually *won't* work. MicroPython has fewer
modules and much less memory. Look for "MicroPython" in the README. Libraries
written for CircuitPython (Adafruit's version) need small changes too.

## Stuck?

| Symptom | Fix |
|---|---|
| `ImportError: no module named ...` | Check the name, then check the file is in `/{{ facts.firmware.lib_dir }}`, not `/`. |
| Thonny's upload says "busy" | Click **Stop** first. |
| `mpremote mip install` can't download | That's the laptop's internet. Use the Thonny way instead. |
| `SyntaxError` inside the library | It's not a MicroPython library (or the download is an HTML page, not the `.py` file). Download it again. |

## Prefer the command line?

Copy a file you've downloaded:

```bash
mpremote cp aht20.py :{{ facts.firmware.lib_dir }}/
```

`mip` can also install from GitHub or micropython-lib:

```bash
mpremote mip install github:someone/some-driver
mpremote mip install aioble
```

## Have fun!

- Open your library on your laptop and read it. It's short. Can you guess what each line does?
  [[read-register]] and [[real-units]] explain it.
- Put a file called `hello.py` in `/{{ facts.firmware.lib_dir }}` *and* in `/`, with
  different `print`s. Which one wins `import hello`? Why?
