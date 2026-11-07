---
id: sao-pinout
title: Find the SAO pinout, and connect your sensor
label: SAO pinout, and connect your sensor
topic: i2c
workshop: true
needs: [map-firmware]
time: 15 min
touches:
  - lib/sao.py                  # SAO_I2C_SDA/SCL, SAOn_GPIOn, the shared i2c bus
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** For the badge's SAO connectors, know what each of the six pins does, which end
is pin 1, and which ESP32 GPIO it's wired to. You'll need this for anything you plug in.

## You need

- Your badge (no laptop needed for steps 1–2)
- The official folder (see [[map-firmware]])
- One of the workshop's sensors: {% for s in facts.sensors %}{{ s[1].name }} ({{ s[1].what }}){% unless forloop.last %}, {% endunless %}{% endfor %}
- {{ facts.sao.connector }}

## Steps

1. **Find the connectors.** An **SAO** ("Shitty Add-On") header is a 2×3 block of pins
   or a socket. The badge has {{ facts.sao.count }}. Many badges mark which way round an
   add-on goes with a notch or a key; this one doesn't, so you'll go by the top of the badge.

   <!-- TODO(photo): close-up of an SAO header with pin 1 marked -->

2. **Label the pins.** Every SAO follows the same standard. On this badge, with the
   badge the right way up:

   ```
              top of badge
       ┌───────┬───────┬───────┐
       │ 3V3   │ SDA   │ GPIO1 │   1  3  5
       │ GND   │ SCL   │ GPIO2 │   2  4  6
       └───────┴───────┴───────┘
   ```

3. **Find the GPIO numbers in the firmware.** Open `{{ facts.sao.pins_file }}` from the
   badge or the folder. Every SAO pin is named near the top. Check from the REPL:

   ```python
   import lib.sao as sao
   [n for n in dir(sao) if n.startswith('SAO')]
   sao.SAO_I2C_SDA, sao.SAO_I2C_SCL
   ```

4. **Confirm on the schematic** (if you like). The firmware says what the code *thinks*;
   the schematic says what's actually wired. It's in the repo under
   `hardware/billboard_pcb/` (`sao.kicad_sch`; open it in [KiCad](https://www.kicad.org)),
   and the repo's `README.md` lists the pins too.

5. **Fill in your table:**

   | SAO pin | Signal | SAO1 | SAO2 | SAO3 |
   |---|---|---|---|---|
   | 1 | 3V3 | (power) | (power) | (power) |
   | 2 | GND | (ground) | (ground) | (ground) |
   | 3 | SDA | {{ facts.sao.sda }} | {{ facts.sao.sda }} | {{ facts.sao.sda }} |
   | 4 | SCL | {{ facts.sao.scl }} | {{ facts.sao.scl }} | {{ facts.sao.scl }} |
   | 5 | GPIO1 | 2 | 4 | 7 |
   | 6 | GPIO2 | 42 | 5 | 6 |

   Cover the right-hand columns before you start. Did you get the same numbers?
   Notice that SDA and SCL are the same on all three: they're one shared bus.

6. **Connect your sensor.** Switch the badge off first.
   - **On an SAO board:** find its pin 1 (3V3), line it up with the badge's pin 1
     (top left in the diagram), and push it on. There's no key to stop it going on
     backwards, so check twice.
   - **A workshop sensor:** plug the cable's small white plug into either socket on the
     sensor board (it only fits one way). Then push the four sockets at the other end onto
     one SAO header's pins, matching the colors:

     | SAO pin | Signal | Cable wire | Sensor pin (on other boards, often labeled) |
     |---|---|---|---|
     | 1 | 3V3 | red | VCC, VIN or 3V3 |
     | 2 | GND | black | GND |
     | 3 | SDA | blue | SDA or SDI |
     | 4 | SCL | yellow | SCL or SCK |

     Pins 5 and 6 stay empty.

   Any of the three SAO headers works for I2C.

   <!-- TODO(photo): the cable's four sockets on an SAO header, colors visible -->

   <!-- TODO(photo): a workshop sensor connected to an SAO header -->

   Switch the badge back on. Nothing will look different yet. [[i2c-scan]] checks the
   badge can see it.

**✅ Done when** you can point to SAO pin 1 on the badge, name the GPIO behind
SDA, SCL, and one SAO's GPIO1 and GPIO2, and your sensor is connected the right way round.

## What just happened

An SAO header gives an add-on four things: power (3.3 V and ground), an **I2C bus** (SDA
is data, SCL is clock) for talking to smart chips, and two plain **GPIO** pins you can
switch on and off or read. Because every badge uses the same layout, add-ons work on
any badge, if you know which of *this* chip's pins are behind them.

This badge has three headers on one I2C bus, so up to three add-ons (or more, chained
with Qwiic cables) can share it, as long as each chip has a different address. The
workshop's four sensors all do.

## Stuck?

| Symptom | Fix |
|---|---|
| Can't find the SAO names | They're in `{{ facts.sao.pins_file }}`, not `lib/board.py`. Search for `SAO`. |
| Firmware and schematic disagree | Believe the schematic, and tell the badge team! |
| An add-on gets hot when plugged in | **Switch off and unplug it now.** It's in backwards (3V3 and GND swapped). |
| The sensor's pins don't say SDA/SCL | SPI-only boards say MOSI/MISO/CS; those won't work on I2C. Some boards do both; check its docs. |

**Careful:** never connect pin 1 (3V3) straight to pin 2 (GND). That's a short circuit.

## Have fun!

- Which GPIOs are completely free? (Hint: `lib/board.py` names two test points.)
- Try [[i2c-scan]] (I2C) next, or [[sao-blink]] (GPIO).
- Find your sensor's chip on its board. Can you read the part number? Search for its datasheet.
