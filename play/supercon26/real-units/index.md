---
id: real-units
title: Turn raw bytes into real units with the datasheet
label: Raw bytes to real units
topic: i2c
workshop: false
needs: [read-register]
time: 20 min
touches:
  - lib/sao.py#i2c
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Turn your sensor's raw bytes into a number in real units, using only the
datasheet, and wrap it in a function you can use anywhere.

## You need

- The raw reading from [[read-register]], and the same `i2c`, `ADDR` and `time` at the REPL
- Your sensor's datasheet

## Steps

1. **Find the format.** In the datasheet, find the description of the bytes you read.
   You're looking for four answers:

   | Question | Look for |
   |---|---|
   | Which byte comes first? | "MSB first", "big-endian", "little-endian", or a bit diagram |
   | How many bits are the reading? | "10-bit", "16-bit", "20-bit", or the bit diagram |
   | Can it be negative? | "two's complement", "signed" |
   | What's one step worth? | "resolution", "sensitivity", "LSB =", or a formula |

   Answer them yourself first, then check against your sensor's section below.

2. **Open your sensor's section**, put the bytes together, and scale them.

3. **Wrap it in a function** called `reading()`, like the one at the end of your section.
   You'll use it to show your sensor on the badge's screen in [[name-badge]].

<details markdown="1">
<summary><strong>{{ facts.sensors.lis3dh.name }}</strong>: motion, in g</summary>

| Question | Answer |
|---|---|
| Which byte comes first? | **Low** byte first (little-endian): `0x28` is X's low byte, `0x29` its high byte |
| How many bits? | 10, in "normal mode", sitting at the **top** of the 16 (left-justified) |
| Negative? | Yes, two's complement |
| One step? | 4 mg (0.004 g) in normal mode at ±2 g |

`struct` puts the bytes together and handles the sign. `<` means low byte first, and
each `h` is one signed 16-bit number:

```python
import struct
raw = i2c.readfrom_mem(ADDR, 0x28 | 0x80, 6)
x, y, z = struct.unpack("<hhh", raw)
x, y, z
```

Shift off the 6 spare bits at the bottom, then scale:

```python
[(n >> 6) * 0.004 for n in (x, y, z)]
```

Lay the badge flat. One axis should read about 1 g (that's gravity) and the other two
about 0. Stand it up and watch the 1 g move to another axis.

```python
def reading():
    """(x, y, z) in g."""
    x, y, z = struct.unpack("<hhh", i2c.readfrom_mem(ADDR, 0x28 | 0x80, 6))
    return tuple((n >> 6) * 0.004 for n in (x, y, z))
```

</details>

<details markdown="1">
<summary><strong>{{ facts.sensors.cap1203.name }}</strong>: touch, as a position along the slider</summary>

| Question | Answer |
|---|---|
| Which byte comes first? | One byte per pad: `0x10` left, `0x11` middle, `0x12` right |
| How many bits? | 8 |
| Negative? | Yes, two's complement (−128 to 127) |
| One step? | No unit: a "delta count" just says how far the pad has moved from normal |

The datasheet doesn't give a real unit here, so you make one up. Here's the recipe: a
finger between two pads moves *both* of their counts. Weight each pad by where it sits
(left 0 %, middle 50 %, right 100 %) and average:

```python
import struct
left, mid, right = struct.unpack("bbb", i2c.readfrom_mem(ADDR, 0x10, 3))   # b = signed byte
left, mid, right
```

```python
def reading():
    """Finger position along the slider, 0 (left) to 100 (right), or None if no touch."""
    left, mid, right = (max(n, 0) for n in struct.unpack("bbb", i2c.readfrom_mem(ADDR, 0x10, 3)))
    total = left + mid + right
    if total < 20:          # just noise: nobody's touching it
        return None
    return (mid * 50 + right * 100) / total
```

Slide your finger along it while you call `reading()` a few times. Does it go from about
0 to about 100? Change the `20` if it reacts to nothing, or misses light touches.

<!-- TODO(verify) on a real board: delta registers, and a good noise threshold -->

</details>

<details markdown="1">
<summary><strong>{{ facts.sensors.aht20.name }}</strong>: temperature in °C, humidity in %RH</summary>

| Question | Answer |
|---|---|
| Which byte comes first? | High first. Byte 0 is status; humidity is bytes 1, 2 and the top half of 3; temperature is the bottom half of 3, then 4 and 5 |
| How many bits? | 20 each |
| Negative? | No (the formula handles below zero) |
| One step? | Humidity: 100 % ÷ 2²⁰. Temperature: 200 °C ÷ 2²⁰, then subtract 50 |

Twenty bits don't fit `struct`, so put them together by hand. `<<` moves bits up,
`|` drops the next ones in underneath, and `>> 4` / `& 0x0F` split byte 3 in half:

```python
i2c.writeto(ADDR, bytes([0xAC, 0x33, 0x00]))
time.sleep_ms(80)
raw = i2c.readfrom(ADDR, 6)
hum  = (raw[1] << 12) | (raw[2] << 4) | (raw[3] >> 4)
temp = ((raw[3] & 0x0F) << 16) | (raw[4] << 8) | raw[5]
hum * 100 / 2**20, temp * 200 / 2**20 - 50
```

Does the temperature look like the room's? Breathe on it: both should go up.

```python
def reading():
    """(°C, %RH)."""
    i2c.writeto(ADDR, bytes([0xAC, 0x33, 0x00]))
    time.sleep_ms(80)
    raw = i2c.readfrom(ADDR, 6)
    hum  = (raw[1] << 12) | (raw[2] << 4) | (raw[3] >> 4)
    temp = ((raw[3] & 0x0F) << 16) | (raw[4] << 8) | raw[5]
    return temp * 200 / 2**20 - 50, hum * 100 / 2**20
```

<!-- TODO(verify) on a real board: bit layout and formulas (sources: community drivers) -->

</details>

<details markdown="1">
<summary><strong>{{ facts.sensors.bh1750.name }}</strong>: light, in lux</summary>

| Question | Answer |
|---|---|
| Which byte comes first? | High byte first (big-endian) |
| How many bits? | 16 |
| Negative? | No (there's no such thing as negative light) |
| One step? | 1 ÷ 1.2 lux in the `0x10` mode |

```python
import struct
raw = i2c.readfrom(ADDR, 2)
n = struct.unpack(">H", raw)[0]     # > = high byte first, H = unsigned 16-bit
n / 1.2
```

An office is a few hundred lux; a phone light up close is thousands.

```python
def reading():
    """Light in lux. Needs the power-on and 0x10 commands from read-register first."""
    return struct.unpack(">H", i2c.readfrom(ADDR, 2))[0] / 1.2
```

</details>

**✅ Done when** your `reading()` returns a value in real units that makes sense, and it
changes the right way when you change what the sensor senses.

## What just happened

A sensor measures something (a voltage, a capacitance) and turns it into a whole
number, because that's all it can send. The datasheet tells you the recipe back:

**real value = (raw number, put together and aligned) × step size + offset**

Each part of that recipe has a name you'll see again: **byte order** (endianness),
**sign** (two's complement), **resolution** (bits), and **scale and offset**. Every
digital sensor uses some mix of them. Compare your sensor's section with a neighbor's:
the four use almost every combination.

A library (see [[add-a-library]]) does exactly this for you. Now you can read one and
know what it's doing.

<!-- TODO(diagram): bytes → joined number → shifted → × step + offset → real units, with each arrow labeled -->

## Stuck?

| Symptom | Fix |
|---|---|
| The value is about 16×, 64× or 256× too big | You missed a shift, or the bytes are the other way round (`<` vs. `>`). |
| It's huge when it should be small or negative | It's signed and you treated it as unsigned. Use lower-case `h` or `b`, not `H` or `B`. |
| It's a few degrees above the room | The sensor sits near warm parts of the badge, and you're touching it. Normal. |
| `struct.error` | You read the wrong number of bytes for the format. `"<hhh"` needs exactly 6. |
| `NameError: name 'i2c' is not defined` | You've reset since [[read-register]]. Redo its step 1 and your sensor's setup. |

## Have fun!

- Show it in other units: °F (`c * 9 / 5 + 32`), or m/s² (`g * 9.81`).
- Average 10 readings to smooth out the noise. Does the last digit settle?
- {{ facts.sensors.lis3dh.name }}: work out the badge's tilt angle with `math.atan2`.
- Show the reading on the LEDs: more LEDs for more light, or blue-to-red for temperature (see [[all-leds]]).
