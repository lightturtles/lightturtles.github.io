---
id: sao-blink
title: Blink an LED on an SAO GPIO pin
label: Blink on the SAO
tier: developmental
difficulty: 3
group: sao
icon: lightbulb
needs: [sao-pinout, one-led]
time: 15 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Wire an LED to the SAO connector and switch it on and off from the REPL.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- Your pin table from [[sao-pinout]]
- An LED, a resistor (anything from 220 Ω to 1 kΩ), and two female-to-female jumper
  wires. Or any SAO with an LED on GPIO1.

## Steps

1. **Wire it, with the badge unplugged:**
   - SAO **GPIO1** → resistor → LED's **long** leg
   - LED's **short** leg → SAO **GND**

   <!-- TODO(photo): breadboard-free wiring: jumper, resistor, LED, jumper -->

2. Plug the badge back in, then press **Ctrl+C** to get `>>>`.

3. Make the pin an output, and turn it on:

   ```python
   from machine import Pin
   led = Pin({{ facts.sao.gpio1 }}, Pin.OUT)
   led.value(1)
   ```

4. Off again:

   ```python
   led.value(0)
   ```

5. Blink it ten times:

   ```python
   import time
   for i in range(10):
       led.toggle()
       time.sleep(0.25)
   ```

**✅ Done when** your LED blinks on command.

## What just happened

`Pin.OUT` turns the GPIO into a switch the chip controls. `value(1)` connects it to 3.3 V,
`value(0)` to ground. Current flows from the pin, through the resistor and the LED, back
to GND, and the LED lights.

The resistor limits that current. Without it, the LED would try to pull more than the pin
can safely supply. One pin can only handle a few milliamps, plenty for an LED but
nowhere near enough for a motor.

Unlike the badge's own LEDs from [[one-led]], this one is "dumb": one wire, on or off. The
badge's LEDs have a chip inside that listens for color data.

<!-- TODO(diagram): GPIO → resistor → LED → GND, with current arrow -->

## Stuck?

| Symptom | Fix |
|---|---|
| LED never lights | Flip the LED around (it only works one way). Check you're on GPIO1, not GPIO2. |
| Lights, but very dim | Try a smaller resistor (but not below 100 Ω). |
| Blinks on its own | The badge's program uses that pin. **Ctrl+C** first, or try GPIO2. |
| Need a multimeter check | Measure between GPIO1 and GND: ~3.3 V after `value(1)`, ~0 V after `value(0)`. |

## Have fun!

- Fade it with PWM: `from machine import PWM; p = PWM(Pin({{ facts.sao.gpio1 }})); p.duty_u16(2000)`
- Make it blink whenever you press a button (see [[read-button]]).
- Blink your name in Morse code.
