---
layout: post
title: "You're Underutilizing Your Serial Port (Part 3): Remote Control, Firmware Updates, and Running Python/Lua on an MCU"
date: 2026-11-10
type: article
subjects:
  - firmware
  - tooling
  - security
venue: Embedded Edit
excerpt: >
  Part 3 puts the command parser from Part 2 to work: controlling an MCU
  from across the world, updating its firmware over UART, running
  manufacturing tests, and even "programming" it in Python or Lua.
documents:
  - title: "You're Underutilizing Your Serial Port, Part 3 (PDF)"
    url: /assets/youre-underutilizing-your-serial-port-p3/youre_underutilizing_your_serial_port_p3.pdf
    type: pdf
---

*Originally published on [The Embedded Edit](https://www.embeddededit.com/article/uart-remote-control-firmware-updates-python-lua).*

In [Part 2]({% post_url 2026-11-04-youre-underutilizing-your-serial-port-part-2-controlling-your-mcu %}), we built a simple command parser so that sending `<command>` over UART runs the matching function on the MCU. Part 3 finishes the "control and configuration" theme by looking at what that one little mapping makes possible.

The first one is **remote control**. In [Part 1]({% post_url 2026-10-27-youre-underutilizing-your-serial-port-part-1-logging-and-telemetry %}), I used a small SBC and a VPN like Tailscale to read an MCU's `printf` output from anywhere. The same link works in the other direction: your dashboard in Prague can turn on an LED in Santiago.

![A dashboard in Prague sends "led on" through Tailscale, over WiFi, to an SBC in Santiago, which forwards it over UART to the MCU; the MCU's "adc_ch2" notifications flow back to the dashboard's graph]({{ '/assets/youre-underutilizing-your-serial-port-p3/serial_port_p3_01_remote_control.png' | relative_url }})

Next is **firmware updates**. A UART bootloader just has to trigger an update, collect the new image, verify it, and write it to flash.

A checksum catches bit errors, not forged firmware, and a bootloader also has to survive power loss, failed writes, and timeouts without bricking the device. The same caution applies to the next use, **manufacturing fixtures**. Commands like `selftest`, `calibrate adc`, and `config set key_material` are a convenient way to finish a board on the factory line. Leave them (or `rd`/`wr`, or an unauthenticated updater) in production firmware, though, and you've handed an attacker the keys. The article's advice: compile out what you don't need, expose as few commands as possible, authenticate clients, default to the lowest privilege, and fuzz your parser.

Last, the fun part: **"programming" an MCU in Python**. Wrap commands like `config`, `dw`, and `dr` in a small pyserial library with a MicroPython-style API, and you can write `led.high()` on your PC and watch the LED on your MCU turn on.

![A Python REPL on a PC imports a "machine" module and blinks an LED; each line of Python becomes a serial command, like "config A 5 OUT" or "dw A 5 1", sent over UART to the MCU]({{ '/assets/youre-underutilizing-your-serial-port-p3/serial_port_p3_00_python.png' | relative_url }})

Once a driver works in Python, porting it to C is pretty straightforward. Or skip the PC entirely and run **Lua** on the MCU: it's small, fast, portable, and a basic REPL is just a few lines of C (see my [comparison of MicroPython, Zephyr, Lua, and Forth]({% post_url 2026-07-13-comparing-micropython-zephyr-lua-and-forth %}) for more).

![A PC sends "x = 5" and "print(x + 6)" over UART to an MCU running a Lua REPL (luaL_newstate, then luaL_dostring on each line), which replies "11"]({{ '/assets/youre-underutilizing-your-serial-port-p3/serial_port_p3_04_lua.png' | relative_url }})

All of this by just coming up with creative ways to map a serial `<command>` to a function.

| Feature          | `<command>`                        | `function`                                              |
| ---------------- | ---------------------------------- | ------------------------------------------------------- |
| Firmware updates | Ex: `update {firmware blob} {CRC}` | Reprogram flash                                         |
| Python           | Ex: `dw A 5 1`                     | R/W MCU peripherals<br />Ex: `digitalWrite(A, 5, HIGH)` |
| Lua              | Ex: `print(x+5)`                   | Evaluate the text as Lua code                           |

[Read the full article →](https://www.embeddededit.com/article/uart-remote-control-firmware-updates-python-lua)
