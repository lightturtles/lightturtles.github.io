---
id: real-units
title: Turn raw bytes into real units with the datasheet
label: Raw bytes to real units
topic: i2c
workshop: true
needs: [read-register]
time: 20 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Turn your sensor's raw bytes into a number in real units ({{ facts.sensor.units }}),
using only the datasheet.

## You need

- The raw reading from [[read-register]]
- The sensor's datasheet: <{{ facts.sensor.datasheet }}>

## Steps

1. **Find the format.** In the datasheet, find the description of the register you read.
   You're looking for four answers:

   | Question | Look for | Example (a TMP102 temperature sensor) |
   |---|---|---|
   | Which byte comes first? | "MSB first", "big-endian", or a bit diagram | high byte first |
   | How many bits are the reading? | "12-bit", "16-bit", or the bit diagram | 12 bits, left-aligned in 16 |
   | Can it be negative? | "two's complement", "signed" | yes (below 0 °C) |
   | What's one step worth? | "resolution", "LSB =", "sensitivity" | 0.0625 °C per step |

   <!-- TODO(sensor): fill in the right-hand column for the workshop sensor too, once it's chosen -->

2. **Put the bytes together.** Two bytes, high byte first, make one 16-bit number:

   ```python
   raw = i2c.readfrom_mem(ADDR, {{ facts.sensor.register }}, 2)
   n = (raw[0] << 8) | raw[1]
   n
   ```

   `<< 8` moves the high byte up 8 places; `|` drops the low byte in underneath.

3. **Signed or not?** If the datasheet says two's complement, numbers 32768 and up are
   really negative. `struct` handles that for you:

   ```python
   import struct
   n = struct.unpack(">h", raw)[0]     # > = high byte first, h = signed 16-bit
   ```

   (`">H"` is the unsigned version.)

4. **Line it up.** If the reading uses fewer bits than it's given, shift off the spare
   ones. The TMP102's 12 bits sit at the top of its 16, so:

   ```python
   n = n >> 4
   ```

5. **Scale it.** Multiply by what one step is worth (and add an offset, if the
   datasheet has one):

   ```python
   n * 0.0625
   ```

   Now you have a temperature. Does it look like the room's?

6. **Wrap it in a function** so you can use it anywhere (like [[name-badge]], change C):

   ```python
   def to_units(raw):
       n = struct.unpack(">h", raw)[0]
       return (n >> 4) * 0.0625          # TODO: the workshop sensor's own formula
   ```

   Test it: `to_units(i2c.readfrom_mem(ADDR, {{ facts.sensor.register }}, 2))`.

**✅ Done when** your function prints a value in {{ facts.sensor.units }} that makes sense,
and it changes the right way when you warm the sensor with your fingers.

## What just happened

A sensor measures something (a voltage, a resistance) and turns it into a whole
number, because that's all it can send. The datasheet tells you the recipe back:

**real value = (raw number, put together and aligned) × step size + offset**

Each step in that recipe has a name you'll see again: **byte order** (endianness),
**sign** (two's complement), **resolution** (bits), and **scale and offset**. Every
digital sensor uses some mix of them, whether it's measuring temperature, light,
pressure or motion.

A library (see [[add-a-library]]) does exactly this for you. Now you can read one and
know what it's doing.

<!-- TODO(diagram): two bytes → joined 16-bit number → shifted → × 0.0625 → °C, with each arrow labeled -->

## Stuck?

| Symptom | Fix |
|---|---|
| The value is about 16× or 256× too big | You missed a shift, or the bytes are the other way round (try `"<h"`). |
| It's huge when it should be cold | It's signed and you treated it as unsigned. Use `"h"`, not `"H"`. |
| It's a few degrees above the room | The sensor sits near warm parts of the badge, and you're touching it. Normal. |
| `struct.error` | You read the wrong number of bytes. `"h"` needs exactly 2. |

## Have fun!

- Show it in °F too: `c * 9 / 5 + 32`.
- Average 10 readings to smooth out the noise. Does the last digit settle?
- Find a second reading in the datasheet (humidity? a different resolution setting?)
  and convert that too.
- Show the temperature on the LEDs: blue when it's cold, red when it's warm (see [[all-leds]]).
