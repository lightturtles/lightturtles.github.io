---
id: add-a-library
title: Add a MicroPython library to the badge
label: Add a library
topic: i2c
workshop: false
needs: [i2c-scan]
time: 15 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Skip the datasheet: install a driver for your sensor, `import` it, and get
readings in real units.

## You need

- Your sensor, found with [[i2c-scan]]
- A library: a `.py` file written for **MicroPython**, e.g. a sensor driver from the
  sensor's maker, [micropython-lib](https://github.com/micropython/micropython-lib), or
  a helper at the workshop

<!-- TODO: pick one example driver to match the workshop's I2C sensor, and link it here -->

## Steps

1. **Where does `import` look?**

   ```python
   import sys
   sys.path
   ```

   One of the entries is `'/{{ facts.firmware.lib_dir }}'`. That folder is for libraries.

2. Download the library's `.py` file to your laptop. Open it and skim the top: is there
   a short example of how to use it?

3. In Thonny's bottom (badge) pane, open `{{ facts.firmware.lib_dir }}/`. (No such folder?
   Right-click → **New directory…**.) In the top pane, right-click the `.py` file →
   **Upload to /{{ facts.firmware.lib_dir }}**.

4. Import it and look around:

   ```python
   import sensor_name      # the file's name, without .py
   dir(sensor_name)
   ```

5. **Use it.** Most drivers take an I2C bus (and sometimes an address) when you
   make the object. Hand it the firmware's bus:

   ```python
   {{ facts.firmware.badge_import }}
   s = sensor_name.SENSOR(badge_obj.{{ facts.sao.i2c_attr }})   # the class name is in the library's example
   dir(s)                 # look for something like temperature, or read()
   ```

   <!-- TODO: fill in with the real driver's names once the workshop sensor is picked -->

6. Back it up. It's one of *your* files now (see [[backup]]).

**✅ Done when** `import` works, and the library gives you a reading in real units.

## What just happened

`import x` searches each folder in `sys.path` for `x.py` (or a folder `x/`), in order.
Putting libraries in `/{{ facts.firmware.lib_dir }}` keeps them apart from the badge's
own code. This matters when you update or [[start-fresh]]: anything not in the
official folder gets treated as yours, and a start-fresh deletes it.

A driver does the work of [[read-register]] and [[real-units]] for you: it knows
which registers to read and how to turn the bytes into units. Reading its source is
a good way to learn how, once you're curious.

Libraries written for regular Python usually *won't* work. MicroPython has fewer
modules and much less memory. Look for "MicroPython" in the README.

## Stuck?

| Symptom | Fix |
|---|---|
| `ImportError: no module named ...` | Check the name, then check it's in `/{{ facts.firmware.lib_dir }}`, not `/`. |
| `ImportError` for a *different* module | The library needs another library. Install that one too. |
| `MemoryError` on import | The file is too big to compile on the badge. Ask a helper about `.mpy` files. |
| `SyntaxError` inside the library | It's written for regular Python (or a newer MicroPython). Find another. |

## Prefer the command line?

Copy a file you've downloaded:

```bash
mpremote mkdir :{{ facts.firmware.lib_dir }}
mpremote cp sensor_name.py :{{ facts.firmware.lib_dir }}/
```

Or install straight from micropython-lib or GitHub. This needs internet on the
*laptop*, not on the badge:

```bash
mpremote mip install aioble
mpremote mip install github:someone/some-driver
```

## Have fun!

Put a file called `hello.py` in `/{{ facts.firmware.lib_dir }}` *and* in `/`, with
different `print`s. Which one wins `import hello`? Why?
