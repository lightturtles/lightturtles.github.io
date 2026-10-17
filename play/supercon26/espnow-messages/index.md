---
id: espnow-messages
title: Design an ESP-NOW message (packing, pairing, acks and retries)
label: Design a message
topic: espnow
workshop: false
needs: [espnow-in-app]
time: 40 min
touches: [apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Turn "some bytes" into a message format two badges can agree on, then make
delivery reliable: pair two badges, confirm each message, and resend the lost ones.

## You need

- Your app from [[espnow-in-app]], and a partner running it too

## Steps

### Pack it

1. **Decide what a message holds.** Every message should say *what kind* it is, so the
   receiver knows how to read the rest. For a game:

   | Field | Type | Size |
   |---|---|---|
   | message type | 1 = HELLO, 2 = MOVE, 3 = ACK | 1 byte |
   | sequence number | counts up, wraps at 256 | 1 byte |
   | x, y | board position | 1 byte each |

2. **Pack it with `struct`.** It turns numbers into exact bytes and back:

   ```python
   import struct
   FMT = "BBBB"                     # four unsigned bytes
   msg = struct.pack(FMT, 2, 17, 3, 4)
   msg, len(msg)                    # 4 bytes
   kind, seq, x, y = struct.unpack(FMT, msg)
   ```

3. **Or with JSON.** Easier to read and extend, but bigger:

   ```python
   import json
   msg = json.dumps({"t": "move", "seq": 17, "x": 3, "y": 4}).encode()
   len(msg)                         # about 35 bytes
   json.loads(msg)
   ```

   Either way, keep it under **250 bytes**: that's ESP-NOW's limit.

### Pair up

4. **Find each other by broadcast, then switch to one-to-one.** In `__init__`, add
   `self.partner = None`, `self.seq = 0` and `self.waiting = None` (and `import time,
   struct` at the top). Broadcast a HELLO; when
   you hear one, add the sender as a peer:

   ```python
           # sending: in run_foreground, on a button
           self.e.send(BROADCAST, struct.pack("BB", 1, 0))
           # receiving: in run_foreground, for each (mac, msg) from the inbox
           if msg[0] == 1 and mac != self.partner:
               self.partner = mac
               try:
                   self.e.add_peer(mac)
               except OSError:
                   pass                     # already a peer
               print("paired with", mac.hex())
   ```

### Make it reliable

5. **Did it arrive?** Sending to one peer (not broadcast) tells you whether the other
   radio heard it:

   ```python
   ok = self.e.send(self.partner, msg, True)      # True = wait for the radio's answer
   ```

   `ok` is `False` if the partner's radio didn't confirm. Walk out of range and try.

6. **Did the *app* get it?** The radio's confirmation doesn't mean the other app saw
   the message (its inbox might be full, or its app crashed). For moves that must not
   be lost, have the receiver send back an **ACK** with the same sequence number, and
   resend until it comes:

   ```python
       def send_reliable(self, payload):
           self.seq = (self.seq + 1) % 256
           self.waiting = (self.seq, struct.pack("BB", 2, self.seq) + payload)
           self.tries, self.sent_at = 0, None

       def retry(self):                                # call every run_foreground
           if not self.waiting:
               return
           now = time.ticks_ms()
           if self.sent_at is None or time.ticks_diff(now, self.sent_at) > 300:
               if self.tries == 5:
                   print("gave up"); self.waiting = None; return
               self.e.send(self.partner, self.waiting[1], False)
               self.tries, self.sent_at = self.tries + 1, now
   ```

   When an ACK arrives with the sequence number you're waiting for, set
   `self.waiting = None`. The receiver ACKs every MOVE, and ignores a MOVE whose
   sequence number it has already seen (that's a resend whose ACK got lost).

7. Play it with your partner. Walk apart until messages start failing, and watch the
   retries.

**✅ Done when** you can pair two badges, send moves that each get an ACK, and see a
lost message get resent.

## What just happened

**A message format is a contract.** Both badges must agree on it exactly. A type byte
first means you can add new kinds of message later without breaking old ones.
`struct` is compact and exact; JSON is readable and flexible. Either works under 250 bytes.

**Broadcast vs. one-to-one:**

| | Broadcast | One peer |
|---|---|---|
| Reaches | every badge in range | one badge |
| Radio confirms delivery | no | yes (`send(..., True)`) |
| Good for | finding each other, "who's here?", announcements | games, chat, anything that matters |

**Acks and retries** are how every reliable network works, from TCP to your phone's
Bluetooth. The sequence number does two jobs: it matches ACKs to messages, and it lets
the receiver spot duplicates. Retrying with a timeout is a state machine (see [[fsm]]),
timed with `ticks_diff` (see [[on-time]]).

<!-- TODO(diagram): sequence diagram: A sends MOVE#17 → lost; timeout; A resends MOVE#17 → B; B sends ACK#17 → A -->

## Stuck?

| Symptom | Fix |
|---|---|
| `struct.error` unpacking | The message is a different length than the format. Check the type byte first, then unpack the right format. |
| `AttributeError: ... 'partner'` | Set `self.partner`, `self.seq` and `self.waiting` in `__init__` (step 4). |
| Moves happen twice | The receiver isn't ignoring duplicates. Remember the last sequence number per sender. |
| `ValueError: msg too long` | Over 250 bytes. Use `struct`, or shorter JSON keys. |

## Have fun!

- Tic-tac-toe or battleship over ESP-NOW: whose turn it is is part of the protocol.
- Add a checksum byte. Does anything ever arrive corrupted?
- Measure the round trip: time from sending a MOVE to getting its ACK.
- Rock-paper-scissors: choose → wait for your opponent → reveal. It's turn-based, so the slow screen doesn't matter.
- A shared canvas (Supercon's own r/place): move a cursor with the buttons, place a pixel, and broadcast it so every badge's canvas fills in together, in three colors (see [[draw-pixels]]).
