---
id: espnow-in-app
title: Receive ESP-NOW messages in the background, show them in your app
label: Messages in your app
topic: espnow
workshop: false
needs: [espnow-hello, pass-data]
time: 30 min
touches: [apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): aioespnow is in this firmware (help('modules')); the firmware's own ESP-NOW use (if any) doesn't clash with a second ESPNow() -->

**Goal:** An app that collects messages from other badges all the time, and shows them
when you open it.

## You need

- A partner badge, and [[espnow-hello]] done
- [[pass-data]] done (you'll use a queue)

## Steps

1. **Set up the radio once, in `__init__`.** In `{{ facts.firmware.user_app }}`:

   ```python
   import asyncio, network
   from collections import deque
   import aioespnow

   BROADCAST = b'\xff' * 6

   class App(BaseApp):
       def __init__(self, name, badge):
           super().__init__(name, badge)
           sta = network.WLAN(network.STA_IF)
           sta.active(True)
           sta.config(channel={{ facts.espnow.channel }})
           self.e = aioespnow.AIOESPNow()
           self.e.active(True)
           self.e.add_peer(BROADCAST)
           self.inbox = deque((), 10)       # the 10 newest messages
           self.unread = 0
           asyncio.create_task(self.listen())
   ```

2. **A task that listens, forever.** It sleeps until a message arrives, files it, and
   sleeps again:

   ```python
       async def listen(self):
           async for mac, msg in self.e:
               self.inbox.append((mac, msg))
               self.unread += 1
               print(f"[{self.name}] from {mac.hex()}: {msg}")
   ```

3. **Show them in the foreground,** and send one on a button:

   ```python
       def run_foreground(self):
           while self.inbox:
               mac, msg = self.inbox.popleft()
               print("SHOW:", msg)                # or a label (see lvgl-hello)
           self.unread = 0
           if {{ facts.buttons.app_1 }}:
               self.e.send(BROADCAST, b"ping from " + self.name.encode(), False)
           if {{ facts.buttons.home }}:
               self.switch_to_background()
   ```

4. **Tell the user from the background.** Light an LED while there's unread mail
   (make `self.np` in `__init__`, as in [[one-led]]):

   ```python
       def run_background(self):
           self.np[0] = (0, 0, 16) if self.unread else (0, 0, 0)
           self.np.write()
   ```

5. Save, **Ctrl+D**, and stay on the menu. Have your partner send a few. Watch the
   shell, and the LED. Then open your app: all the messages show up.

**✅ Done when** messages that arrive while your app is in the background are waiting
for you when you open it.

## What just happened

Three parts, each doing one job:

| Part | Runs | Job |
|---|---|---|
| `listen()` task | always, but only wakes when a message arrives | file messages in the inbox |
| `run_background()` | every `background_sleep_ms` | say "you've got mail" without the screen |
| `run_foreground()` | while the app is open | show and empty the inbox |

`aioespnow` is ESP-NOW with `await`able receives, so `listen()` takes no processor time
at all while it waits. The inbox is a queue (see [[pass-data]]): messages pile up while
nobody's looking, and nothing is lost unless more than 10 arrive.

Sending is quick, so it's safe to do straight from `run_foreground()`. The `False` at
the end means "don't wait for the radio to confirm." For broadcasts there's no
confirmation anyway.

## Stuck?

| Symptom | Fix |
|---|---|
| `ImportError: no module named 'aioespnow'` | Poll instead: drop `listen()`, and in `run_background()` do `while self.e.any(): self.inbox.append(self.e.recv(0))` with a plain `espnow.ESPNow()`. |
| Nothing arrives | Same channel as your partner? Is WiFi joined to a network on another channel? |
| Messages arrive twice | Two copies of the app (or the firmware) are listening. Check `help('modules')` and the firmware's own messaging. |
| `RuntimeError` in `create_task` | The firmware might create apps before the event loop runs. Start the task in `start()` instead. |

## Have fun!

- Show the 5 newest messages on screen, newest at the top.
- Reply automatically: when a "ping" arrives, send back "pong".
- Next: give your messages a proper shape with [[espnow-messages]].
