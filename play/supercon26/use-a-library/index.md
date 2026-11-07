---
id: use-a-library
title: Talk to your sensor with a library
label: Use a library
topic: i2c
workshop: true
needs: [add-a-library]
time: 10 min
touches:
  - lib/sao.py#i2c              # the bus every driver is handed
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Get a reading in real units from your sensor, in three lines of Python.

## You need

- Your sensor's library on the badge (see [[add-a-library]])

## Steps

1. Press **Ctrl+C**, then get the badge's SAO bus. Every library needs to be told which
   bus its sensor is on:

   ```python
   {{ facts.firmware.badge_import }}
   ```

2. **Open the section for your sensor** and follow it. They all work the same way:
   make the sensor object, then ask it for `reading()`.

<details markdown="1">
<summary><strong>{{ facts.sensors.aht20.name }}</strong>: temperature and humidity</summary>

```python
import aht20
s = aht20.AHT20(i2c)
s.reading()           # (temperature in °C, humidity in %)
s.text()              # the same, as text
```

**Make it change.** Breathe on it while this runs. Both numbers should go up (breath is
warm *and* wet):

```python
import time
for i in range(20):
    print(s.text())
    time.sleep(1)
```

Each `reading()` takes about 80 ms: the sensor needs that long to measure.

Curious about other libraries? [This one]({{ facts.sensors.aht20.other_driver }}) does the
same job. {{ facts.sensors.aht20.other_note }}

</details>

<details markdown="1">
<summary><strong>{{ facts.sensors.bh1750.name }}</strong>: light</summary>

```python
import bh1750
s = bh1750.BH1750(i2c)
s.reading()           # light, in lux
s.text()
```

**Make it change.** Cover it with your hand, then shine a phone light on it:

```python
import time
for i in range(20):
    print(s.text())
    time.sleep(0.5)
```

An office is a few hundred lux; a phone light up close is thousands.

Curious about other libraries? [This one]({{ facts.sensors.bh1750.other_driver }}) does the
same job. {{ facts.sensors.bh1750.other_note }}

</details>

<details markdown="1">
<summary><strong>{{ facts.sensors.lis3dh.name }}</strong>: motion</summary>

```python
import lis3dh
s = lis3dh.LIS3DH(i2c)
s.reading()           # (x, y, z), in g
s.text()
```

**Make it change.** Lay the badge flat: one axis reads about 1 g (that's gravity) and the
others about 0. Then tilt it slowly while this runs:

```python
import time
for i in range(40):
    print(s.text())
    time.sleep(0.25)
```

If your board's address jumper is closed (it showed up at `0x18` in [[i2c-scan]]),
use `lis3dh.LIS3DH(i2c, address=0x18)`.

Curious about other libraries? [This one]({{ facts.sensors.lis3dh.other_driver }}) does the
same job. {{ facts.sensors.lis3dh.other_note }}

</details>

<details markdown="1">
<summary><strong>{{ facts.sensors.cap1203.name }}</strong>: touch slider</summary>

```python
import cap1203
s = cap1203.CAP1203(i2c)
s.reading()           # where your finger is: 0 (left) to 100 (right), or None
s.text()
s.touched()           # which pads were touched: (left, middle, right)
```

**Make it change.** Slide your finger along it while this runs:

```python
import time
for i in range(40):
    print(s.text())
    time.sleep(0.25)
```

Does it react when nobody's touching it, or miss light touches? Change how sensitive it
is: `cap1203.CAP1203(i2c, threshold=30)` (higher = needs a firmer touch).

Curious about other libraries? [This one]({{ facts.sensors.cap1203.other_driver }}) is
SparkFun's. {{ facts.sensors.cap1203.other_note }}

</details>

**✅ Done when** your sensor's `text()` shows a sensible value, and it changes when you
change what the sensor senses.

## What just happened

A **driver** is a library that knows one chip. You hand it the bus, and it hides the
chip's details: which bytes to send, how long to wait, and how to turn what comes back
into real units. You get a method that answers in those units.

Every workshop driver has the same shape: `Sensor(i2c)`, then `reading()`, `text()`, and
`units`. That's deliberate. Code that uses a sensor (like the screen in
[[name-badge]]) can work with any of them by changing one line. Drivers out in the wild
are less tidy, so check each one's README or example for its names.

Want to know what the driver does inside? [[read-register]] and [[real-units]] do the same
thing by hand, one step at a time.

## Stuck?

| Symptom | Fix |
|---|---|
| `ImportError` | The library isn't on the badge, or isn't in `/{{ facts.firmware.lib_dir }}`. Redo [[add-a-library]]. |
| `NameError: name 'i2c' is not defined` | You skipped step 1, or reset since. Run it again. |
| `OSError: [Errno 19] ENODEV` | Nothing answered at the driver's address. Run `[hex(a) for a in i2c.scan()]` (see [[i2c-scan]]). |
| `RuntimeError: not a ...` | Something answered, but it's a different chip. Check you imported the library for *your* sensor. |
| `AttributeError: 'module' object has no attribute ...` | Check the capitals: the module is lower-case (`aht20`), the class upper-case (`AHT20`). |

## Have fun!

- Show the reading on the LEDs: more LEDs for more light, or blue-to-red for temperature (see [[all-leds]]).
- Borrow a second sensor and plug both in. Can you read both at once?
- Put your sensor on the badge's screen: that's the sensor variant of [[name-badge]].
