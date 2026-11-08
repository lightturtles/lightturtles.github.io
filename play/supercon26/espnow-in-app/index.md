---
id: espnow-in-app
title: Receive ESP-NOW messages in the background, show them in your app
label: Messages in your app
topic: espnow
workshop: false
needs: [espnow-hello, pass-data]
time: 30 min
touches:
  - lib/app_switcher.py#AppSwitcher.arun   # only the open app's run() is called
  - lib/led_bar.py#LedBar.menu_display     # the menu repaints every LED while it shows
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** An app that collects messages from other badges all the time, even while
you're using another app, and shows them when you open it.

## You need

- A partner badge, and [[espnow-hello]] done
- [[pass-data]] done (you'll use a queue), and the "work that keeps going after you
  leave" pattern from [[firmware-diagram]]

## Steps

1. **The app, and its inbox.** Replace `{{ facts.firmware.user_app }}` with:

   ```python
   """Collects ESP-NOW messages all the time; shows them when you open the app."""

   import asyncio, network
   from collections import deque
   import aioespnow

   from apps.base_app import BaseApp
   from lib.button import UserA
   from lib.led_bar import leds

   BROADCAST = b'\xff' * 6


   class MyApp(BaseApp):
       def __init__(self):
           super().__init__("{{ facts.firmware.user_app_name }}")
           self.e = None                     # the radio, once it's started
           self.inbox = deque((), 10)        # the 10 newest messages
           self.unread = 0
   ```

2. **Start the radio the first time the app opens.** The switcher makes every app at
   start-up, so `__init__` is the wrong place for slow set-up nobody may need. Add:

   ```python
       def start_radio(self):
           sta = network.WLAN(network.STA_IF)
           sta.active(True)
           sta.config(channel={{ facts.espnow.channel }})
           self.e = aioespnow.AIOESPNow()
           self.e.active(True)
           self.e.add_peer(BROADCAST)
           asyncio.create_task(self.listen())
   ```

3. **A task that listens, forever.** It sleeps until a message arrives, files it, and
   sleeps again. It also lights the last LED: "you've got mail."

   ```python
       async def listen(self):
           async for mac, msg in self.e:
               self.inbox.append((mac, msg))
               self.unread += 1
               leds[{{ facts.leds.count }} - 1] = (0, 0, 16)
               leds.write()
               print(f"[{self.name}] from {mac.hex()}: {msg}")
   ```

4. **Show them when the app is open,** and send one on a button:

   ```python
       def run(self):
           if self.launched:
               if self.e is None:
                   self.start_radio()
               self.unread = 0               # opening the app turned the LEDs off
           while self.inbox:
               mac, msg = self.inbox.popleft()
               print("SHOW:", mac.hex(), msg)    # or a label (see lvgl-hello)
           if {{ facts.buttons.app_1 }}:
               self.e.send(BROADCAST, b"ping from " + self.name.encode(), False)
   ```

5. Save, **Ctrl+D**, and open your app once: that starts the radio. Then open another
   app, like Gallery. Have your partner send a few (from their REPL, as in
   [[espnow-hello]], or from this app with **{{ facts.buttons.app_1_label }}**). Watch the shell, and the last
   LED. Then open your app again: all the messages show up.

**✅ Done when** messages that arrive while another app is open are waiting for you
when you open yours.

## What just happened

Three parts, each doing one job:

| Part | Runs | Job |
|---|---|---|
| `listen()` task | always, once started, but only wakes when a message arrives | file messages in the inbox; light the LED |
| `run()`, first call after opening | once per open | start the radio (the first time); clear "unread" |
| `run()`, every call | while the app is open | show and empty the inbox |

`aioespnow` is ESP-NOW with `await`able receives, so `listen()` takes no processor time
at all while it waits. The inbox is a queue (see [[pass-data]]): messages pile up while
nobody's looking, and nothing is lost unless more than 10 arrive.

`listen()` is a task of your own. The switcher only ever calls the open app's `run()`,
so this task is what keeps your app listening while another one is open. It never
ends, which is what you want here. If you ever want it to stop, keep a reference
(`self.listener = asyncio.create_task(self.listen())`) and call
`self.listener.cancel()`.

The LED has one catch: while the **menu** is showing, it repaints every LED every
10 ms, so your "you've got mail" light only shows while some app is open (see
[[share-hardware]]).

Sending is quick, so it's safe to do straight from `run()`. The `False` at the end means
"don't wait for the radio to confirm." For broadcasts there's no confirmation anyway.

## Stuck?

| Symptom | Fix |
|---|---|
| `ImportError: no module named 'aioespnow'` | Poll instead: use a plain `espnow.ESPNow()`, and make `listen()` a loop that does `while self.e.any(): self.inbox.append(self.e.recv(0))`, then `await asyncio.sleep_ms(100)`. |
| `AttributeError: 'NoneType' object has no attribute 'send'` | You pressed **{{ facts.buttons.app_1_label }}** before the radio started. `start_radio()` must run in the `if self.launched:` part. |
| Nothing arrives | Same channel as your partner? Is WiFi joined to a network on another channel? |
| Messages arrive twice | Two listeners: did `start_radio()` run twice? Check `if self.e is None:`. |
| The LED never lights | The menu was showing when the message came. Open an app first. |

## Have fun!

- Show the 5 newest messages on screen, newest at the top.
- Reply automatically: when a "ping" arrives, send back "pong".
- Next: give your messages a proper shape with [[espnow-messages]].
