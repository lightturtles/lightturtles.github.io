---
id: read-register
title: Read a register from your I2C sensor
label: Read a register
topic: i2c
workshop: true
needs: [i2c-scan]
time: 15 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Ask your sensor for its reading and get raw bytes back, at the REPL.

## You need

- Your sensor, found with [[i2c-scan]] (you know its address)
- Its datasheet: <{{ facts.sensor.datasheet }}>

## Steps

1. Press **Ctrl+C** and get the bus again:

   ```python
   {{ facts.firmware.badge_import }}
   i2c = badge_obj.{{ facts.sao.i2c_attr }}
   ADDR = {{ facts.sensor.address }}
   ```

2. **Find the register map** in the datasheet. Search for "register map" or "register
   summary": a table of numbered registers, each holding one setting or reading.
   Find two:
   - an **ID** register ("WHO_AM_I", "chip ID", "device ID"), if there is one, and
   - the register holding the **reading** you want.

   For the workshop's {{ facts.sensor.name }}: ID at `{{ facts.sensor.id_register }}`,
   reading at `{{ facts.sensor.register }}`, {{ facts.sensor.bytes }} bytes long.

3. **Say hello.** Read the ID register. It should hold the number the datasheet says
   (`{{ facts.sensor.id_value }}`):

   ```python
   i2c.readfrom_mem(ADDR, {{ facts.sensor.id_register }}, 1)
   ```

   You get back a `bytes` object like `b'\x75'`. That's one byte, written in hex.

4. **Read the reading:**

   ```python
   raw = i2c.readfrom_mem(ADDR, {{ facts.sensor.register }}, {{ facts.sensor.bytes }})
   raw
   list(raw)              # the same bytes, as numbers 0–255
   ```

5. **Make it change.** Read it in a loop and hold the sensor between your fingers:

   ```python
   import time
   for i in range(20):
       print(list(i2c.readfrom_mem(ADDR, {{ facts.sensor.register }}, {{ facts.sensor.bytes }})))
       time.sleep(0.5)
   ```

   Which byte changes fastest? Which barely moves?

**✅ Done when** you get the right ID back, and you can make the reading's bytes change.

## What just happened

Most I2C sensors look like a small set of numbered **registers**. To read one, the
badge sends the sensor's address, then the register number, then reads back as many
bytes as you asked for. `readfrom_mem(address, register, count)` does all three.

The bytes are the sensor's **raw** numbers, in its own format. Often a reading is
split across two bytes: a "high" byte that changes slowly and a "low" byte that
changes fast. The datasheet says how to put them together and turn them into real
units. That's [[real-units]].

The ID check is worth doing every time you meet a new chip: if it's right, the wiring,
the address, and the bus are all working.

<!-- TODO(sensor): some sensors (e.g. SHT4x) have no registers: you send a command with
     i2c.writeto(), wait, then i2c.readfrom(). Add a box here if the workshop sensor is one. -->

<!-- TODO(diagram): one I2C transaction: START, address+W, register, repeated START, address+R, byte, byte, STOP -->

## Stuck?

| Symptom | Fix |
|---|---|
| `OSError: [Errno 19] ENODEV` | Nothing answered at that address. Re-run [[i2c-scan]]. |
| `OSError: [Errno 116] ETIMEDOUT` | Bus trouble: check the wiring (see [[sao-pinout]]). |
| The ID is wrong | Different chip, or a different version. Check the part number printed on it. |
| The bytes never change | Some sensors must be woken up first (a "power" or "mode" register). Check the datasheet's start-up steps. |

## Have fun!

- Read *every* register: `for r in range(0x40): print(hex(r), i2c.readfrom_mem(ADDR, r, 1))`.
  Can you match some to the register map?
- Change a setting: `i2c.writeto_mem(ADDR, register, bytes([value]))`, then read it back.
