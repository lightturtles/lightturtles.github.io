---
id: i2c-scan
title: Scan the SAO I2C bus
label: Scan for I2C devices
tier: developmental
difficulty: 3
group: sao
icon: radar
needs: [sao-pinout]
time: 10 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Ask the SAO bus "who's there?" and get back the address of every I2C chip plugged in.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- Your pin table from [[sao-pinout]]
- An SAO or sensor breakout that uses I2C (helpful, but try it without one first)

## Steps

1. Set up the bus on the SAO pins:

   ```python
   from machine import I2C, Pin
   i2c = I2C({{ facts.sao.i2c_id }}, scl=Pin({{ facts.sao.scl }}), sda=Pin({{ facts.sao.sda }}))
   ```

2. Scan with nothing plugged in:

   ```python
   i2c.scan()
   ```

   An empty list `[]` means nobody answered. That's right, for now.

3. **Unplug the badge**, plug in your I2C add-on (mind the key!), reconnect, **Ctrl+C**,
   and redo steps 1–2.

4. Show the answers in hex. That's how datasheets write them:

   ```python
   [hex(a) for a in i2c.scan()]
   ```

5. Look the address up. Some common ones:

   | Address | Usually |
   |---|---|
   | `0x3c`, `0x3d` | Small OLED display |
   | `0x50`–`0x57` | EEPROM (many SAOs carry one that describes the add-on) |
   | `0x68` | Real-time clock, or a motion sensor |
   | `0x76`, `0x77` | Temperature/pressure sensor (BME280, BMP280) |

**✅ Done when** a scan finds your add-on and you know what kind of chip is at that address.

## What just happened

I2C lets many chips share two wires. Every chip has a 7-bit **address**, and the
badge (the **controller**) starts each conversation by calling one out. `scan()` just
calls every address from 8 to 119 and lists the ones that answer.

Knowing the address is step one. To *talk* to the chip, you need its datasheet, or a
library someone already wrote (see [[add-a-library]]).

<!-- TODO(diagram): SDA/SCL bus with badge as controller and two devices labeled with addresses -->

## Stuck?

| Symptom | Fix |
|---|---|
| Still `[]` with something plugged in | Reseat it, and check the key. Not every SAO has I2C; some only use GPIO. |
| `OSError: [Errno 116] ETIMEDOUT` | SDA and SCL may be swapped, or there's no pull-up resistor on the bus. Ask a helper. |
| Every address answers | SDA or SCL is shorted to ground. Unplug and check the wiring. |
| `ValueError` on `I2C(...)` | The firmware may already be using controller {{ facts.sao.i2c_id }}. Try `SoftI2C(scl=..., sda=...)` instead. |

<!-- TODO(verify): does the firmware expose its own SAO I2C object (last year: badge.sao_i2c)? If so, mention it. -->

## Have fun!

- Swap add-ons with a neighbor and scan theirs.
- Read the first bytes of an SAO's EEPROM: `i2c.readfrom_mem(0x50, 0, 32)`. Anything readable?
