---
layout: post
title: "You're Underutilizing Your Serial Port (Part 1): Logging and Telemetry"
date: 2026-10-27
type: article
subjects:
  - firmware
  - debugging
  - tooling
venue: Embedded Edit
excerpt: >
  A serial port is more than a place to print "Here". Part 1 covers richer log
  messages, how much data a UART (or RTT, or USB) can realistically move,
  turning the stream into a graphical MCU dashboard, and reaching that
  dashboard from the other side of the world.
documents:
  - title: "You're Underutilizing Your Serial Port, Part 1 (PDF)"
    url: /assets/youre-underutilizing-your-serial-port-p1/youre_underutilizing_your_serial_port_p1.pdf
    type: pdf
---

*Originally published on [The Embedded Edit](https://www.embeddededit.com/article/uart-logging-telemetry-debugging).*

![A PyQt dashboard on a laptop in Prague parses a log message ("[I] foo.c[53] doStuff() ADC, Ch1: 718") and a data message ("adc_ch2 0.18234") into a text field and a live graph; the messages arrive over Tailscale from a single-board computer in Santiago that's connected to an MCU by UART]({{ '/assets/youre-underutilizing-your-serial-port-p1/serial_port_p1_00_remote.png' | relative_url }})

For most of us, a UART gets used for `printf("Hello World!\n")` to prove it works, maybe `printf("Here\n")` to check if some code ever ran, and not much else. This new series argues that's a waste: a serial port is "a tiny portal into the heart of your microcontroller," useful for logging and telemetry, control and configuration, and testing and debugging. Part 1 starts with logging and telemetry.

The first step is a better `printf`. Adding a severity level, a timestamp, and the file, line, and function to each message makes them useful enough to keep in the code for good, with a global flag to filter them by build or severity (see [In Defense of `printf` Debugging]({% post_url 2025-06-02-in-defense-of-printf-debugging %}) and [Improved `printf` Debugging]({% post_url 2025-09-29-improved-printf-debugging %}) for more). The obvious objection is throughput. At 115200 baud, a UART moves 11,520 bytes/sec, or only about **209 messages/sec** at 55 bytes each. Many STM32s will run their UARTs at 3 Mbaud, though, which gets you about **5,454 messages/sec**, 26 times faster. Beyond that, the article compares SEGGER RTT, USB-FS, and USB-HS (up to about 15 MB/sec) and points out the easiest option of all: [simulating the system on your host computer](https://lightturtles.github.io/works/2024/10/02/simulating-your-embedded-project-part-1/), where the "virtual baud rate" is as fast as your computer can copy memory.

Logs don't have to stay in a terminal, either. A GUI built with PyQt, or with Web Serial in Chrome, Edge, or Opera (which means no software to install), can parse data values out of the message stream and route them to graphs and other widgets. Those messages can be full log lines, simple `<name> <value>` pairs, or compact binary frames: a COBS-framed binary message carries the same reading as a 12-byte ASCII message in just 5 bytes. The open-source [Scrutiny Debugger](https://scrutinydebugger.com/) takes this a step further, reading and writing MCU memory over a custom serial protocol and showing it as live graphs, gauges, and indicators without any dedicated log messages at all.

Finally, the dashboard doesn't need to be in the same room (or on the same continent) as the device. Connect the MCU to a small internet-connected SBC like a Raspberry Pi Zero 2 W, join both to a VPN like Tailscale, and `usbip` (or `usbip-win2` on Windows) will attach the MCU's USB serial port to your laptop as if it were plugged in locally. None of this is much more complicated than `printf(something)`. You just have to get creative about what `something` is, how you display it, and how you connect to the port it's printed on.

This is not your grandma's `printf`, friends!

[Read the full article →](https://www.embeddededit.com/article/uart-logging-telemetry-debugging)
