---
id: espnow-nearby
title: "Who's nearby? Count badges and estimate distance from signal strength"
label: Who's nearby?
topic: espnow
workshop: false
needs: [espnow-hello]
time: 25 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Count the badges around you, and guess how far away each one is from how
strong its signal is.

## You need

- The ESP-NOW setup from [[espnow-hello]]
- Other badges sending something. Ask your table to run step 1 too.

## Steps

1. **Everyone: send a beacon** every 2 seconds, for a couple of minutes:

   ```python
   import time
   for i in range(60):
       e.send(BROADCAST, b"here")
       time.sleep(2)
   ```

   (Run it on one badge per person. Use another badge, or step 2 afterwards, to listen.)

2. **Listen, and let ESP-NOW keep score:**

   ```python
   end = time.ticks_add(time.ticks_ms(), 10_000)
   while time.ticks_diff(end, time.ticks_ms()) > 0:
       e.recv(500)

   e.peers_table
   ```

   `peers_table` has one entry per badge heard: its MAC, then `[signal, time last heard]`.

3. **Count who's around right now** (heard in the last 10 seconds):

   ```python
   now = time.ticks_ms()
   near = {mac: rssi for mac, (rssi, t) in e.peers_table.items()
           if time.ticks_diff(now, t) < 10_000}
   len(near), near
   ```

4. **Read the signal.** The first number is the **RSSI**, in dBm: always negative, and
   closer to 0 means stronger. Put a partner's badge right next to yours, then 1 m away,
   then 3 m. Write down the RSSI at each. Does it change smoothly? Does it jump around?

5. **Turn signal into distance.** Use your 1 m reading as the reference:

   ```python
   RSSI_1M = -45        # yours, from step 4
   N = 2.5              # 2 in open air; 3 or more in a crowded room
   def meters(rssi):
       return 10 ** ((RSSI_1M - rssi) / (10 * N))

   {mac.hex(): round(meters(r), 1) for mac, r in near.items()}
   ```

   Test it: are the estimates for your partner right? How wrong are they?

**✅ Done when** you can count the badges in range, and you've seen how good (or bad)
a distance guess from RSSI is.

## What just happened

Every time ESP-NOW receives a message, it notes the sender, the signal strength, and
the time, in `peers_table`. You never have to answer anyone: listening is enough to
know who's around.

Radio signals get weaker with distance, roughly following a **path-loss** formula:
every time the distance multiplies by 10, the signal drops by `10 × N` dB. Measure the
strength at 1 m, pick `N`, and you can work backwards to a distance.

But it's a rough guess. Bodies absorb 2.4 GHz (it's the frequency microwave ovens use,
because water soaks it up), walls block it, and signals bounce off metal. Turning your
badge around can change the reading by 10 dB. Use RSSI for "near / medium / far," not
for meters. Averaging several readings helps.

<!-- TODO(diagram): RSSI vs. distance curve, with a scatter of real readings around it -->

## Stuck?

| Symptom | Fix |
|---|---|
| `peers_table` is empty | Nothing heard. Same channel as the senders? Are they actually sending? |
| `AttributeError: peers_table` | Older firmware. Count senders yourself: keep a dict of `mac: time.ticks_ms()` for each `e.recv()`, and skip the distance step. |
| RSSI jumps by 10+ between readings | Normal. Average the last 5. |

## Have fun!

- A "hot and cold" game: one badge hides; the seeker's LEDs glow brighter as RSSI rises.
- Light one LED per badge nearby (see [[all-leds]]).
- Run it in the background all weekend and count how many different badges you met
  (see [[firmware-diagram]] and [[save-settings]]).
- Hot potato: pass a "potato" to a nearby badge; your LEDs heat up the longer you hold it (see [[espnow-in-app]] and [[animate-leds]]).
- A scavenger hunt: a few badges run as hidden beacons. Hunters follow the signal strength and collect a token from each one, saved across reboots (see [[firmware-diagram]] and [[save-settings]]).
