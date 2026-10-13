---
id: demo
title: Demo your hack on Sunday night
label: Demo your hack!
tier: core
difficulty: 9
group: apps
icon: trophy
needs: [app-screen]
time: 60 s on stage
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Show the room what you made.

## You need

- Your badge, charged
- Your app from [[app-screen]], or anything else you're proud of
- A [[backup]] of your app, made today

## Steps

1. **Sign up.** <!-- TODO: where and when sign-ups happen, and when demos start -->

2. **Make sure it runs without a laptop.** Unplug USB, press
   **{{ facts.power.reset_button }}**, and open your app from the menu. Your demo
   won't have a serial cable. Anything that only worked while plugged in will show up now.

3. **Back it up.** Copy your app to your laptop again (see [[backup]]). If something
   breaks five minutes before your demo, you can restore it in one step.

4. **Plan 60 seconds.** Three sentences is plenty:
   - What does it do? (Show it, don't describe it.)
   - What surprised you, or what was hardest?
   - What would you add next?

5. **Rehearse once** to a neighbor, with the badge in your hand. Hold it so the screen
   faces the audience (or the camera), and give the e-ink time to refresh.

**✅ Done when** you've demoed it!

## What just happened

You built something on hardware you'd never seen a few days ago, and explained it to
a room full of people who build things. That second part is a skill too, and it gets
easier every time.

## Stuck?

| Symptom | Fix |
|---|---|
| It worked an hour ago | Press **{{ facts.power.reset_button }}** and try again. Then restore from your backup (see [[break-and-restore]]). |
| Works plugged in, not on battery | Is the battery charged? Is your app waiting on the laptop (USB serial, `input()`)? |
| Screen shows nothing new in front of the crowd | Give it a few seconds; e-ink is slow. Talk while it refreshes. |
| Nerves | Everyone in the room has had a demo fail. They'll cheer anyway. |

## Have fun!

Skills that look good on stage: [[all-leds]] (rainbow!), [[share-hardware]], or anything
with an SAO plugged in ([[sao-blink]]). Want others to use your app after Supercon?
<!-- TODO: link the "write a README / open a PR" skill when it exists -->
