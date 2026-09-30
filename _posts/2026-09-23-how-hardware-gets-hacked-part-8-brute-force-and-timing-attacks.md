---
layout: post
title: "How Hardware Gets Hacked (Part 8): Brute Force and Timing Attacks"
date: 2026-09-23
type: article
subjects:
  - security
venue: DigiKey
excerpt: >
  Turning from the now-hardened unlock process to the eCTF key fob's pairing
  pin, which falls to a brute force attack in hours and to a timing attack in
  under a hundred guesses, then defending it with a per-attempt delay and a
  constant-time comparison.
documents:
  - title: "Brute Force and Timing Attacks (PDF)"
    url: /assets/hhghp8/hhghp8_brute_force_and_timing_attacks.pdf
    type: pdf
---

*Originally published on [Maker.io (DigiKey)](https://www.digikey.com/en/maker/blogs/2026/how-hardware-gets-hacked-part-8-brute-force-and-timing-attacks).*

![An attacker sends a pairing pin guess to a fob, which compares a MAC of the guess against a MAC of the real pin; the error comes back after 34 ns, and the attacker wonders what the timing says about their next guess]({{ '/assets/hhghp8/hhghp8_15_mac_pairing_pin_300.png' | relative_url }})

With challenge-response and a properly seeded PRNG in place, the unlock process from Part 7 would take something like breaking AES-CMAC to defeat. So Part 8 does what a real attacker would do: it goes looking for the weakest part of the system that gives the same payoff. That's the pairing process. A paired fob hands over the car ID, the unlock key, and the pairing pin to anyone who sends it `pair <pin>` with the right 6-hex-digit pin. There are only about 16.7 million possible pins, and at roughly 2.5 ms per guess a script can **brute force** its way through all of them in under 12 hours (about 6 on average). The payoff is the unlock key itself.

Brute force defenses come in three flavors: make each attempt harder (a fingerprint scan, or erasing the device after too many failures), make each attempt slower, or make any single guess less likely to succeed (a longer pin). The competition rules fix the pin format, and an attacker who can reset or re-flash the fob can wipe out any counter of failed attempts, so the defense here is a fixed delay added to every pairing attempt, no counter needed. A user never notices it, but it pushes the worst-case brute force time from 11.7 hours to 194 days.

That defense assumes a wrong guess tells the attacker nothing except that it's wrong. It doesn't. `memcmp` bails out at the first mismatched byte, so the error message comes back a few nanoseconds later for each leading digit the guess got right. Consistent differences that small are still measurable, and they turn the problem into a game of Wordle: guess all 16 values of the first digit, keep the slow one, repeat for the next digit. That's at most **96 guesses** instead of 16.7 million, or an hour and a half even at a full minute per guess. This is a **timing attack**, one kind of **side-channel attack**, in which a device leaks information through how long it takes, how much power it draws, or even what its error messages say.

The fix is a constant-time comparison that XORs every byte pair together and checks the accumulated result only at the end, so the run time no longer depends on where the pins differ. Because C has no way to express "constant-time," you have to check the generated assembly to make sure the compiler kept it that way. Comparing MACs of the pins would also work, since the avalanche effect makes a byte-by-byte timing leak useless to an attacker. The article also covers two tempting fixes that fall short. A random delay only adds noise, which averaging over many guesses (or watching the power trace) removes. Encrypting the pairing packet requires a key shared by every fob, and in this competition that key sits in a binary every attacker already has.

[Read the full article →](https://www.digikey.com/en/maker/blogs/2026/how-hardware-gets-hacked-part-8-brute-force-and-timing-attacks)
