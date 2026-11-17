---
layout: post
title: "What's Really Inside a 555 Timer? (Another Teaching Moment)"
date: 2026-11-10
type: talk
subjects:
  - hardware
  - analog
venue: DigiKey
excerpt: >
  The 555 "timer" has no timing circuitry at all. A look at the SR latch,
  two comparators, three 5k resistors, and discharge transistor inside,
  and how they work together with an external RC network to make a square wave.
---

{% include youtube.html id="fs0LgSkrrLc" %}

The 555 timer is everywhere, but did you know it doesn't have any internal timing circuitry? Circuits that use it as a timer are really just using its flexible internal components, and those same components can be wired up to do everything from amplifying audio to detecting rain. So what's actually inside?

![Block diagram of an NE555]({{ '/assets/inside_a_555/555_block_diagram.png' | relative_url }})

- **An SR latch.** This is the heart of the chip. Once it's set, the output stays HIGH, even after Set goes LOW again. Once it's reset (or the RESET pin is pulled LOW), the output stays LOW.
- **Two comparators.** One resets the latch when THRESHOLD rises above the CONTROL voltage (nominally 2/3 V<sub>CC</sub>). The other sets it when TRIGGER drops below 1/3 V<sub>CC</sub>.
- **Three 5k resistors.** They set those 1/3 and 2/3 V<sub>CC</sub> reference voltages, and they're where the 555 gets its name.
- **A discharge transistor.** It's driven by the inverse of the output. If you know microcontroller GPIO, think of OUTPUT as push-pull and DISCHARGE as open-drain.

With those pieces in mind, the classic astable circuit makes sense.

![Astable NE555]({{ '/assets/inside_a_555/astable-555-circuit.png' | relative_url }})\\
*Figure from [All About Circuits](https://www.allaboutcircuits.com/uploads/thumbnails/astable-555-circuit.png)*
{: style="text-align:center;"}

At power-up, the capacitor is empty, so TRIGGER (pin 2) is below 1/3 V<sub>CC</sub>. That sets the latch, which drives the output HIGH and turns the internal transistor (on pin 7) off, and the capacitor starts charging through R<sub>1</sub> and R<sub>2</sub>. When it passes 2/3 V<sub>CC</sub>, the latch resets, the output goes LOW, and the transistor discharges the capacitor through R<sub>2</sub>. When it falls back to 1/3 V<sub>CC</sub>, the cycle starts over. The frequency is set entirely by the external parts: how long the capacitor takes to charge through R<sub>1</sub> + R<sub>2</sub> and discharge through R<sub>2</sub>.

That mix of analog and digital parts makes the 555 a Swiss Army knife of mixed-signal design. Once you've seen a few more 555 circuits, you might start to agree with the Grey Beards who say most simple microcontroller projects "could have been done with a 555."

**Related**

- [555 internals (Falstad)](https://www.falstad.com/s.py?s=lNX4Yh): an interactive simulation of the 555's internal circuitry
- [NE555/SA555/NA555 datasheet (Diodes Incorporated)](https://www.diodes.com/assets/Datasheets/NE555_SA555_NA555.pdf): the datasheet whose block diagram the video uses
