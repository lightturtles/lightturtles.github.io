---
id: espnow-hello
title: Say hello badge-to-badge with ESP-NOW
label: Badge-to-badge hello
topic: espnow
workshop: false
needs: [wifi-join]
time: 20 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): does the stock firmware use ESP-NOW itself ({{ facts.espnow.firmware_uses }})? If so, which channel, and does Ctrl+C free it? -->

**Goal:** Send a message straight from your badge to a neighbor's, no router or
internet involved.

## You need

- Two badges (find a partner), each connected and showing `>>>` (see [[repl]])
- [[wifi-join]] done, so you've met `network.WLAN`

## Steps

1. **Both of you:** press **Ctrl+C**, then switch on the radio and ESP-NOW:

   ```python
   import network, espnow
   sta = network.WLAN(network.STA_IF)
   sta.active(True)
   sta.config(channel={{ facts.espnow.channel }})    # both badges on the same channel
   e = espnow.ESPNow()
   e.active(True)
   ```

2. **Find your badge's address.** Every radio has a 6-byte **MAC address**:

   ```python
   mac = sta.config('mac')
   mac
   mac.hex(':')
   ```

   Write it down, or read it out to your partner. (`machine.unique_id()` is another
   ID for the chip; on the ESP32 it's usually the same 6 bytes.)

3. **Shout to everyone.** The address of all `ff` bytes means "every badge in range":

   ```python
   BROADCAST = b'\xff' * 6
   e.add_peer(BROADCAST)
   ```

4. **One of you listens:**

   ```python
   host, msg = e.recv(10_000)       # wait up to 10 s
   host, msg
   ```

5. **The other sends**, within those 10 seconds:

   ```python
   e.send(BROADCAST, b"hello from Ana")
   ```

   The listener gets the sender's MAC and the message, as bytes. Swap roles.

6. **Just to one badge.** Add your partner by their MAC (type it in as bytes) and send
   only to them:

   ```python
   PARTNER = bytes.fromhex("aabbccddeeff")    # their mac.hex(), without the colons
   e.add_peer(PARTNER)
   e.send(PARTNER, b"just for you")
   ```

7. **Break it on purpose.** One of you changes channel (`sta.config(channel=6)`) and
   sends again. Nothing arrives. Change back.

8. Press **Ctrl+D** to get the badges back.

**✅ Done when** you've sent a message to a partner's badge and received one back, and
you can say why both badges must be on the same channel.

## What just happened

**ESP-NOW** is Espressif's own radio protocol, built on WiFi hardware but without a
network: no router, no passwords, no IP addresses. Badges talk directly, addressed by
MAC. Messages are small (up to 250 bytes) and fast to send, which makes it ideal for
games, chat, and "who's nearby?" (see [[espnow-nearby]]).

**The same-channel rule.** WiFi is split into channels, and a radio listens on one at a
time. Two badges on different channels can't hear each other. If a badge joins a WiFi
network, its channel follows the router's, so badges that want to use both WiFi and
ESP-NOW must all be on the same network (or none).

**Broadcast vs. one badge.** Broadcast reaches everyone in range, but nobody confirms
they got it. Sending to one MAC (a **peer**) gets a quick confirmation from the radio
(see [[espnow-messages]]).

<!-- TODO(diagram): two badges with MAC labels; broadcast arrow to many badges vs. unicast arrow to one; both on "channel 1" -->

## Stuck?

| Symptom | Fix |
|---|---|
| `recv` returns `(None, None)` | Nothing arrived in time. Same channel? Did the sender `add_peer` first? |
| `OSError: ESP_ERR_ESPNOW_NOT_FOUND` | You sent to a MAC you haven't added with `add_peer`. |
| `OSError: ESP_ERR_ESPNOW_EXIST` | That peer is already added. Fine; carry on. |
| `ValueError` on `bytes.fromhex` | Exactly 12 hex digits, no colons or spaces. |
| Works at the table, not across the room | Walls, bodies and other radios. Range in a crowded hall can be a few meters. |

## Have fun!

- Send a color and light your partner's LED with it (see [[one-led]]).
- Make a group: three badges, all listening, one sending to broadcast.
- Put messages in your app, so they arrive while you're using the badge: [[espnow-in-app]].
- Wave: a button sends "hi from <your name>", and the screen shows the last name that waved at you (see [[lvgl-hello]]).
