---
id: read-register
title: Read raw data from your I2C sensor
label: Read a register
topic: i2c
workshop: false
needs: [use-a-library]
time: 15 min
touches:
  - lib/sao.py#i2c
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Ask your sensor for a reading and get raw bytes back, at the REPL.

This is what the driver from [[use-a-library]] does inside, one step at a time. Open
your sensor's driver file next to this page and you'll recognize every line.

## You need

- Your sensor, found with [[i2c-scan]] (you know its address)
- Its datasheet (linked in your sensor's section below)

## Steps

1. Press **Ctrl+C** and get the bus again:

   ```python
   {{ facts.firmware.badge_import }}
   import time
   ```

2. **Find out what kind of chip you have.** Open the datasheet and look for one of these:
   - a **register map** ("register summary", "register description"): a table of
     numbered registers, each holding one setting or reading. You read and write them
     by number.
   - a **command table**: a list of bytes you send to tell the chip what to do
     ("power on", "measure now"). You then read back whatever it measured.

   Two of the workshop's sensors work each way.

3. **Open the section for your sensor** and follow it.

<details markdown="1">
<summary><strong>{{ facts.sensors.lis3dh.name }}</strong>: {{ facts.sensors.lis3dh.what }}, registers</summary>

Datasheet: from [its product page]({{ facts.sensors.lis3dh.page }}). Look for
"Register mapping".

```python
ADDR = {{ facts.sensors.lis3dh.address }}
```

**Say hello.** Read the WHO_AM_I register. It should hold `{{ facts.sensors.lis3dh.id_value }}`:

```python
i2c.readfrom_mem(ADDR, {{ facts.sensors.lis3dh.id_register }}, 1)
```

You get back a `bytes` object: `b'3'`. That's one byte. MicroPython shows it as a
character when it can, and `0x33` happens to be the code for `3`. Use `hex(...[0])`
to see it as a number.

**Wake it up.** The LIS3DH starts asleep. Register `0x20` (CTRL_REG1) sets how often
it measures and which axes are on. `0x57` means "100 times a second, X, Y and Z":

```python
i2c.writeto_mem(ADDR, 0x20, bytes([0x57]))
```

**Read X, Y and Z.** They're in six registers starting at `0x28`. To read several in
a row you add `0x80` to the first one. That's this chip's way of saying "keep going":

```python
raw = i2c.readfrom_mem(ADDR, 0x28 | 0x80, 6)
list(raw)
```

**Make it change.** Tilt the badge slowly while this runs:

```python
for i in range(20):
    print(list(i2c.readfrom_mem(ADDR, 0x28 | 0x80, 6)))
    time.sleep(0.5)
```

Which bytes change most? (Hint: count from 0, and look at bytes 1, 3 and 5.)

</details>

<details markdown="1">
<summary><strong>{{ facts.sensors.cap1203.name }}</strong>: {{ facts.sensors.cap1203.what }}, registers</summary>

Datasheet: from [its product page]({{ facts.sensors.cap1203.page }}). Look for
"Register Description".

```python
ADDR = {{ facts.sensors.cap1203.address }}
```

**Say hello.** Read the Product ID register. It should hold `{{ facts.sensors.cap1203.id_value }}`:

```python
i2c.readfrom_mem(ADDR, {{ facts.sensors.cap1203.id_register }}, 1)
```

You get back a `bytes` object like `b'm'`. That's one byte. MicroPython shows it as a
character when it can (`0x6D` is the code for `m`). `hex(...[0])` shows it as a number.

**Read which pads are touched.** Register `0x03` (Sensor Input Status) has one bit per
pad: bit 0 is the left pad, bit 1 the middle, bit 2 the right. The chip remembers a
touch until you clear it, by writing `0` to register `0x00` (Main Control):

```python
def touched():
    status = i2c.readfrom_mem(ADDR, 0x03, 1)[0]
    i2c.writeto_mem(ADDR, 0x00, bytes([0]))     # clear it for next time
    return status
```

**Make it change.** Touch the pads while this runs:

```python
for i in range(40):
    print(bin(touched()))
    time.sleep(0.25)
```

**How hard?** Registers `0x10`, `0x11` and `0x12` say how much each pad's reading has
moved from normal (its "delta count"). Watch them as you hover, then touch:

```python
list(i2c.readfrom_mem(ADDR, 0x10, 3))
```

<!-- TODO(verify) on a real board: register numbers, and that writing 0 to 0x00 clears the status -->

</details>

<details markdown="1">
<summary><strong>{{ facts.sensors.aht20.name }}</strong>: {{ facts.sensors.aht20.what }}, commands</summary>

Datasheet: from [its product page]({{ facts.sensors.aht20.page }}). Look for the
section on reading the sensor ("Sensor reading process").

```python
ADDR = {{ facts.sensors.aht20.address }}
```

**Say hello.** The AHT20 has no ID, but reading one byte gives its **status**. Bit 3
(`0x08`) says it's calibrated and ready:

```python
status = i2c.readfrom(ADDR, 1)[0]
bin(status), bool(status & 0x08)
```

If that's `False`, send the "initialize" command and try again:
`i2c.writeto(ADDR, bytes([0xBE, 0x08, 0x00]))`.

**Ask for a measurement, wait, read it.** The command is `0xAC 0x33 0x00`, and a
measurement takes about 80 ms:

```python
i2c.writeto(ADDR, bytes([0xAC, 0x33, 0x00]))
time.sleep_ms(80)
raw = i2c.readfrom(ADDR, 6)
list(raw)
```

The first byte is the status again (bit 7 set means "still busy, wait longer"). The other
five hold humidity and temperature, packed together.

**Make it change.** Breathe on the sensor while this runs:

```python
for i in range(20):
    i2c.writeto(ADDR, bytes([0xAC, 0x33, 0x00]))
    time.sleep_ms(80)
    print(list(i2c.readfrom(ADDR, 6)))
    time.sleep(0.5)
```

Which bytes jump when you breathe? (Breath is warm *and* wet.)

<!-- TODO(verify) on a real board: commands and timing (sources: community drivers, not the official datasheet) -->

</details>

<details markdown="1">
<summary><strong>{{ facts.sensors.bh1750.name }}</strong>: {{ facts.sensors.bh1750.what }}, commands</summary>

Datasheet: from [its product page]({{ facts.sensors.bh1750.page }}). Look for the
"Instruction Set Architecture" table.

```python
ADDR = {{ facts.sensors.bh1750.address }}
```

**Say hello.** The BH1750 has no ID and no registers at all, just commands. Turn it on,
then tell it to measure continuously at high resolution:

```python
i2c.writeto(ADDR, bytes([0x01]))    # power on
i2c.writeto(ADDR, bytes([0x10]))    # measure continuously, 1 lx steps
time.sleep_ms(180)                  # the first measurement takes up to 180 ms
```

No error means it heard you.

**Read the reading.** Just read two bytes, no register number needed:

```python
raw = i2c.readfrom(ADDR, 2)
list(raw)
```

**Make it change.** Cover the sensor with your hand, then shine a phone light on it:

```python
for i in range(20):
    print(list(i2c.readfrom(ADDR, 2)))
    time.sleep(0.5)
```

Which byte changes a little, and which changes a lot?

</details>

**✅ Done when** your sensor says hello (the right ID, or a sensible status), and you
can make its bytes change.

## What just happened

To read a **register**, the badge sends the sensor's address, then the register number,
then reads back as many bytes as you asked for. `readfrom_mem(address, register, count)`
does all three. Its partner, `writeto_mem()`, changes a register: that's how you woke
the {{ facts.sensors.lis3dh.name }} up.

**Command** chips skip the register number. `writeto(address, bytes)` sends a command,
and `readfrom(address, count)` reads back whatever the chip has ready.

Either way, the bytes are the sensor's **raw** numbers, in its own format. Often a
reading is split across two or more bytes: a "high" byte that changes slowly and a
"low" byte that changes fast. The datasheet says how to put them together and turn
them into real units. That's [[real-units]].

Saying hello is worth doing every time you meet a new chip: if it answers correctly, the
wiring, the address, and the bus are all working.

<!-- TODO(diagram): two I2C transactions side by side: register read (START, addr+W, register, repeated START, addr+R, bytes, STOP) and command chip (START, addr+W, command, STOP … START, addr+R, bytes, STOP) -->

## Stuck?

| Symptom | Fix |
|---|---|
| `OSError: [Errno 19] ENODEV` | Nothing answered at that address. Re-run [[i2c-scan]]. |
| `OSError: [Errno 116] ETIMEDOUT` | Bus trouble: check the wiring (see [[sao-pinout]]). |
| The ID is wrong | Different chip, or a different version. Check the part number printed on it. |
| The bytes never change | It may still be asleep. Check you did the "wake it up" or "power on" step in your sensor's section. |
| {{ facts.sensors.aht20.name }}: first byte has bit 7 set (`>= 128`) | It's still measuring. Wait longer before you read. |

## Have fun!

- Got a register chip? Read *every* register:
  `for r in range(0x40): print(hex(r), i2c.readfrom_mem(ADDR, r, 1))`.
  Can you match some to the register map?
- {{ facts.sensors.lis3dh.name }}: write `0x27` to `0x20` instead of `0x57`. What changed?
  (Look up "ODR" in the datasheet.)
- {{ facts.sensors.bh1750.name }}: try command `0x13` instead of `0x10`. What's different about the numbers?
