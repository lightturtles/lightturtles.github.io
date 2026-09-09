---
layout: post
title: "Breadboarding an STM32 (Another Teaching Moment)"
date: 2026-09-08
type: video
subjects:
  - hardware
venue: DigiKey
excerpt: >
  How to build the minimal breadboard circuit for an STM32C0 microcontroller for only a few dollars in parts. Discusses the five key design considerations for any microcontroller circuit (power, reset, clocking, programming, and specialty pins) and how to account for them in your design.
documents:
  - title: "Bill of Materials (CSV)"
    url: /assets/minimal_stm32_circuit/minimal-stm32-circuit-bom.csv
    type: csv
    description: "Manufacturer part numbers and DigiKey links for the parts used in the video."
---

{% include youtube.html id="M9FHGF2F6tE" %}

This one covers the same territory as my [Make Your Own MCU Boards]({% post_url 2023-06-25-teardown23-make-your-own-mcu-boards %}) talk, but live and on camera: how little you actually need to bring up a microcontroller. The chip in question is an STM32C071KBT3 — a 32-pin QFP part — paired with a breakout board from Adafruit. Solder the chip down, add header pins, and you're most of the way to a working circuit.

What's left is the same list of five things every MCU needs, no matter the vendor:

1. **Power** — digital supply pins tied to the rails, with decoupling capacitors as a nice-to-have rather than a requirement. Separate analog power pins can share the digital rail too, at the cost of a noisier ADC.
2. **Reset** — the STM32C0 has an internal pull-up on NRST, so the pin needs nothing extra. A two-pin breadboard-mount button gives you a manual reset if you want one.
3. **Clocking** — the internal RC oscillator is enough for most projects. An external clock only earns its keep when you need precision timing, like USB or a real-time clock, and a packaged oscillator (rather than a hand-tuned crystal circuit) is the more reliable way to add one.
4. **Programming** — an ST-Link V2 debug adapter supplies SWDIO, SWCLK, and reset directly; no extra circuitry needed.
5. **Specialty pins** — BOOT0 controls where the STM32C0 starts executing after reset, and it's disabled by default, so it's another pin you can leave alone.

Add power, wire up SWD, and drop in a quick CubeMX Blinky project, and that's a working STM32 for only a few dollars in new parts — cheaper if you use a less expensive STM32C0 variant and make your own breakout boards.

**Related**

- [Getting started with STM32C0 MCU hardware development (AN5673)](https://www.st.com/resource/en/application_note/an5673-getting-started-with-stm32c0-mcu-hardware-development-stmicroelectronics.pdf) — ST application note describing the minimal circuit for an STM32C0 in great detail.
- [Make Your Own MCU Boards (Teardown 2023)]({% post_url 2023-06-25-teardown23-make-your-own-mcu-boards %}) — the talk this video's premise is drawn from, with more on sourcing, layout, and assembly
- [STM32F103C8T6 breakout board (GitHub)](https://github.com/nathancharlesjones/STM32F103C8T6-breakout-board) — my own minimal MCU board design, as a reference
