---
layout: post
title: "You're Underutilizing Your Serial Port (Part 2): Controlling Your MCU"
date: 2026-11-04
type: article
subjects:
  - firmware
  - debugging
  - tooling
venue: Embedded Edit
excerpt: >
  Part 1 only sent data out of the MCU. Part 2 starts sending commands in:
  building a simple CLI parser, using it to control peripherals, tasks,
  configuration, and memory, and thinking through the tiny protocol of
  notifications, commands, and replies that results.
documents:
  - title: "You're Underutilizing Your Serial Port, Part 2 (PDF)"
    url: /assets/youre-underutilizing-your-serial-port-p2/youre_underutilizing_your_serial_port_p2.pdf
    type: pdf
---

*Originally published on [The Embedded Edit](https://www.embeddededit.com/article/uart-cli-mcu-control-configuration).*

![A Python dashboard with a toggle switch set to "Yes" sends the command "led on" to the MCU, which replies with the notification "led_status on" to fill in an LED indicator on the dashboard]({{ '/assets/youre-underutilizing-your-serial-port-p2/serial_port_p2_00_led_dashboard.png' | relative_url }})

In [Part 1]({% post_url 2026-10-27-youre-underutilizing-your-serial-port-part-1-logging-and-telemetry %}), data only flowed one direction: out of the MCU. Part 2 turns things around and starts *sending* data to the MCU to control and modify its behavior at runtime. In fact, the rest of the series may just be "fancy things you can do after sending a command to the MCU".

The core piece is a simple, line-based command parser (a CLI): collect UART characters until you have a complete line, split it into words, and call the function associated with the first word. Libraries like the Memfault firmware shell will do most of that for you, but it's not hard to write yourself, and the article points to libraries for nice-to-haves like line editing, history, tab completion, and argument parsing.

![CLI flowchart]({{ '/assets/youre-underutilizing-your-serial-port-p2/serial_port_p2_01_cli.png' | relative_url }})

Once that's in place, you can run just about any function on your MCU by typing its name. The article walks through a whole list of uses: turning LEDs and motors on and off (or letting a dashboard do it with the click of a button); changing the log level or which data values get streamed; running calibrations and setting configuration values; getting system stats like uptime and error logs; saving persistent settings; reading and writing arbitrary memory with `rd` and `wr` (or, with a little help from the DWARF debug info, reading and writing variables *by name*); implementing a reduced HAL over the command line; and enabling, disabling, re-timing, or even swapping the filter function used by a running task. Add a `pause_all_tasks` command to that last one and your humble UART starts to feel almost like a debugger!

Last, the article takes a step back to look at the protocol we've accidentally built: asynchronous, self-describing **notifications** from the MCU, self-contained **commands** from the host, and **replies** that don't need an identifier as long as only one command is ever in flight.

![Protocol sequence diagram]({{ '/assets/youre-underutilizing-your-serial-port-p2/serial_port_p2_06_notifications_mixed.png' | relative_url }})
{: style="text-align:center;"}

That's essentially a tiny RPC system. It's not a sophisticated one, but understanding its assumptions (one command source, one command at a time, simple ASCII messages) tells us what it can do and what it can't.

[Read the full article →](https://www.embeddededit.com/article/uart-cli-mcu-control-configuration)
