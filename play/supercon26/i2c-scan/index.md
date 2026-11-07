---
id: i2c-scan
title: Scan the SAO I2C bus
label: Scan for I2C devices
topic: i2c
workshop: true
needs: [sao-pinout]
time: 10 min
touches:
  - lib/sao.py#i2c              # the firmware's SAO bus: I2C(0, scl=18, sda=17, freq=400_000)
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Ask the SAO bus "who's there?" and get back the address of every I2C chip plugged in.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- Your sensor, connected as in [[sao-pinout]]

## Steps

1. Press **Ctrl+C**, then grab the SAO bus the firmware sets up:

   ```python
   {{ facts.firmware.badge_import }}
   ```

   Using the firmware's bus (instead of making your own) means your code and the
   badge's agree on the pins and the speed.

2. Ask who's there:

   ```python
   i2c.scan()
   ```

   You get a list of numbers, one per chip that answered. An empty list `[]` means
   nobody did.

3. Show the answers in hex. That's how datasheets write them:

   ```python
   [hex(a) for a in i2c.scan()]
   ```

4. **Take it away.** Switch the badge off, unplug the sensor, switch it back on,
   **Ctrl+C**, and redo steps 1–3. Which number vanished? That one is your sensor.
   Put it back the same way.

5. Look the address up. The workshop's sensors:

   | Address | Sensor | Measures |
   |---|---|---|
   {% for s in facts.sensors %}| `{{ s[1].address }}` | {{ s[1].name }} | {{ s[1].what }} |
   {% endfor %}

   And some other common ones:

   | Address | Usually |
   |---|---|
   | `0x3c`, `0x3d` | Small OLED display |
   | `0x50`–`0x57` | EEPROM (many SAOs carry one that describes the add-on) |
   | `0x68` | Real-time clock, or a motion sensor |
   | `0x76`, `0x77` | Temperature/pressure sensor (BME280, BMP280) |

**✅ Done when** a scan finds your sensor, and you know its address.

## What just happened

I2C lets many chips share two wires. Every chip has a 7-bit **address**, and the
badge (the **controller**) starts each conversation by calling one out. `scan()` just
calls every address from 8 to 119 and lists the ones that answer.

Knowing the address is step one. To *talk* to the chip, you need its datasheet (see
[[read-register]]), or a library someone already wrote (see [[add-a-library]]).

<!-- TODO(diagram): SDA/SCL bus with badge as controller and two devices labeled with addresses -->

## Stuck?

| Symptom | Fix |
|---|---|
| Still `[]` with something plugged in | Reseat it, and check the key or the wires (see [[sao-pinout]]). Not every SAO has I2C; some only use GPIO. |
| `OSError: [Errno 116] ETIMEDOUT` | SDA and SCL may be swapped, or there's no pull-up resistor on the bus. Ask a helper. |
| Every address answers | SDA or SCL is shorted to ground. Unplug and check the wiring. |
| LIS3DH shows up at `0x18`, not `0x19` | Its address jumper is closed. That's fine; use `0x18` from now on. |
| `ImportError` on the first line | Make your own bus instead, below. |

**No firmware bus?** Make your own on the SAO pins:

```python
from machine import I2C, Pin
i2c = I2C({{ facts.sao.i2c_id }}, scl=Pin({{ facts.sao.scl }}), sda=Pin({{ facts.sao.sda }}), freq=400_000)
```

## Have fun!

- Borrow a neighbor's sensor and plug both in (chain them with a Qwiic cable). Does the scan find both?
- Read the first bytes of an SAO's EEPROM: `i2c.readfrom_mem(0x50, 0, 32)`. Anything readable?
