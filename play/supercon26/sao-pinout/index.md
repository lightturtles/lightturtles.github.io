---
id: sao-pinout
title: Find the SAO pinout, and which GPIO each pin goes to
label: SAO pinout
tier: developmental
difficulty: 2
group: sao
icon: plug
needs: [map-firmware]
time: 15 min
touches: [hardware/board.py]   # TODO: facts.firmware.pins_file
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** For the badge's SAO connector, know what each of the six pins does, which end
is pin 1, and which ESP32 GPIO it's wired to. You'll need this for anything you plug in.

## You need

- Your badge (no laptop needed for steps 1–2)
- The official folder (see [[map-firmware]])

## Steps

1. **Find the connector(s).** An **SAO** ("Shitty Add-On") header is a 2×3 block of pins
   or a socket. The badge has {{ facts.sao.count }}. Look for a notch or a mark on the
   board's silkscreen: that's the key, so add-ons only fit one way.

   <!-- TODO(photo): close-up of the SAO header with pin 1 and the key marked -->

2. **Label the pins.** Every SAO follows the same standard:

   ```
          key / notch
       ┌───────┬───────┐
       │ 3V3   │ GND   │   1  2
       │ SDA   │ SCL   │   3  4
       │ GPIO1 │ GPIO2 │   5  6
       └───────┴───────┘
   ```

   <!-- TODO(verify): orientation vs. the real silkscreen; redraw as an SVG over a photo -->

3. **Find the GPIO numbers in the firmware.** Open `{{ facts.firmware.pins_file }}` from
   the badge or the folder, and search for `SAO`. You should find four pins with names.
   Check from the REPL:

   ```python
   import {{ facts.firmware.pins_file | remove: ".py" | replace: "/", "." }} as pins
   [n for n in dir(pins) if 'SAO' in n]
   ```

4. **Confirm on the schematic** (if you like). The firmware says what the code *thinks*;
   the schematic says what's actually wired.

   <!-- TODO: link to the schematic PDF -->

5. **Fill in your table:**

   | SAO pin | Signal | ESP32 GPIO |
   |---|---|---|
   | 1 | 3V3 | (power) |
   | 2 | GND | (ground) |
   | 3 | SDA | {{ facts.sao.sda }} |
   | 4 | SCL | {{ facts.sao.scl }} |
   | 5 | GPIO1 | {{ facts.sao.gpio1 }} |
   | 6 | GPIO2 | {{ facts.sao.gpio2 }} |

   Cover the right column before you start. Did you get the same numbers?

**✅ Done when** you can point to SAO pin 1 on the badge and name the GPIO behind
GPIO1, GPIO2, SDA, and SCL.

## What just happened

An SAO header gives an add-on four things: power (3.3 V and ground), an **I2C bus** (SDA
is data, SCL is clock) for talking to smart chips, and two plain **GPIO** pins you can
switch on and off or read. Because every badge uses the same layout, add-ons work on
any badge, if you know which of *this* chip's pins are behind them.

The firmware names its pins in one place so nobody has to remember numbers. That file is
the fastest way to find any pin on the badge, not just these.

## Stuck?

| Symptom | Fix |
|---|---|
| Can't find `SAO` in the pins file | Try searching for `I2C` or the numbers in the table. Names change between years. |
| Firmware and schematic disagree | Believe the schematic, and tell the badge team! |
| An add-on gets hot when plugged in | **Unplug it now.** It's in backwards (3V3 and GND swapped). |

**Careful:** never connect pin 1 (3V3) straight to pin 2 (GND). That's a short circuit.

## Have fun!

- Which other GPIOs does `{{ facts.firmware.pins_file }}` name? Which are free?
- Try [[sao-blink]] (GPIO) or [[i2c-scan]] (I2C) next.
