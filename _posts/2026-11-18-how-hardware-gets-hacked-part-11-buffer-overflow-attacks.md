---
layout: post
title: "How Hardware Gets Hacked (Part 11): Buffer Overflow Attacks"
date: 2026-11-18
type: article
subjects:
  - security
venue: DigiKey
excerpt: >
  Exploiting an unbounded write in the eCTF car's UART receive code to overwrite
  the car's computed MAC with an attacker-chosen value, then fixing it with
  length checking and reframing the bug as a broader lesson: every unenforced
  assumption in your code is a potential vulnerability.
documents:
  - title: "Buffer Overflow Attacks (PDF)"
    url: /assets/hhghp11/hhghp11_buffer_overflow.pdf
    type: pdf
---

*Originally published on [Maker.io (DigiKey)](https://www.digikey.com/en/maker/blogs/2026/how-hardware-gets-hacked-part-11-buffer-overflow-attacks).*

![An attacker sends the car an oversized response message whose payload fills received_mac, pads past the nonce, and overwrites the first 8 bytes of computed_mac with the same value, so the car's memcmp passes]({{ '/assets/hhghp11/hhghp11_11_buffer_oflow_on_computed_mac_2_300.png' | relative_url }})

Up to now, every attack in this series exploited an obvious gap in one of the five security principles: a fob that unlocks a car by sending "unlock" or a pairing pin with only 16.7 million possible values. With those gaps closed, Part 11 goes after a "known bug" that has been sitting in the code since the start. `receive_board_message()` reads a length byte off the UART and copies that many bytes into the receive buffer without checking how big the buffer is. Four of its six call sites pass buffers smaller than 255 bytes, so anyone who sends a message with an inflated length field can write past the end of the buffer. This is an **out-of-bounds write** ([CWE-787](https://cwe.mitre.org/data/definitions/787.html)).

An accidental overflow probably just crashes the device. An intentional one is another story. Using the competition's disassembled binary for the STM32 build, the article maps out `unlockCar()`'s stack frame byte by byte and shows what each receive buffer can reach. One of those targets is the link register, which would let an attacker redirect execution anywhere, including into shellcode sent inside the message itself. The easiest target is `computed_mac`, which sits just past `received_mac` and the nonce. **Attack #9** sends a response message that fills `received_mac` with an arbitrary value, pads over the nonce, and writes the same value into the first 8 bytes of `computed_mac`. The `memcmp` passes and the car unlocks.

**Defense #9** is the one you've probably been thinking of the whole time: pass the buffer size to `receive_board_message()` and never copy more than that. A stricter version stores the expected length for each message type and rejects any message that doesn't match. The article also walks through the pitfalls: checking the length only after copying the data, randomizing the stack layout, relying on a stack canary (which protects the return address but not neighboring local variables), and adding a checksum. It then covers alternatives and add-ons such as fixed-length messages, making `computed_mac` `static`, static analyzers, AddressSanitizer, and non-executable RAM.

The bigger lesson isn't "check your array bounds." It's that **any assumption your code makes but doesn't enforce is a vulnerability an attacker can try to exploit**. The rest of the article hunts for others in the same codebase. One assumption is enforced: feature numbers are bounds-checked, and without that check a car could be made to dump its memory 64 bytes at a time. Others are not: that car IDs are NUL-terminated, that expected messages eventually arrive, and that pairing packets have the right length. None of these are exploitable today. But they are vulnerabilities waiting for the day someone changes the code around them, so the question to keep asking is: "What is this code assuming, and is it actually enforced?"

[Read the full article →](https://www.digikey.com/en/maker/blogs/2026/how-hardware-gets-hacked-part-11-buffer-overflow-attacks)
