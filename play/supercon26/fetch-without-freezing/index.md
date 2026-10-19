---
id: fetch-without-freezing
title: Fetch from the web without freezing the badge (asyncio streams)
label: Fetch without freezing
topic: wifi
workshop: false
needs: [web-data, asyncio-basics]
time: 30 min
touches: [apps/userA.py]
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): is aiohttp in the firmware, or mip-installable? Does asyncio.open_connection(ssl=True) work on this build? -->

**Goal:** Fetch web data in an asyncio task, so the buttons, screen and LEDs keep working
while you wait for the reply.

## You need

- The fetch from [[web-data]] working
- [[asyncio-basics]] done

## Steps

1. **A fetch that `await`s.** At `>>>`, on WiFi, paste this. It speaks plain HTTP
   itself, over an asyncio connection:

   ```python
   import asyncio, json

   HOST = "{{ facts.wifi.json_host }}"
   PATH = "{{ facts.wifi.json_path }}"

   async def fetch_json(host, path):
       reader, writer = await asyncio.open_connection(host, 80)
       writer.write(f"GET {path} HTTP/1.0\r\nHost: {host}\r\n\r\n".encode())
       await writer.drain()
       reply = await reader.read(-1)          # everything, until the server hangs up
       writer.close()
       await writer.wait_closed()
       headers, body = reply.split(b"\r\n\r\n", 1)
       return json.loads(body)
   ```

2. **Prove it doesn't block.** Run it next to a ticker:

   ```python
   async def ticker():
       for i in range(30):
           print("tick", i)
           await asyncio.sleep_ms(100)

   async def main():
       t = asyncio.create_task(ticker())
       data = await fetch_json(HOST, PATH)
       print("got", data["current"]["temperature_2m"])
       await t

   asyncio.new_event_loop()
   asyncio.run(main())
   ```

   The ticks keep coming while the request is out. Compare with `requests` in
   [[web-data]], where everything stopped.

3. **Put it in your app.** Your app's methods aren't `async`, so they *start* a task and
   check on it later. In `{{ facts.firmware.user_app }}` (paste `fetch_json` above the class):

   ```python
       def start_fetch(self):
           if getattr(self, "fetching", False):
               return                                  # one at a time
           self.fetching = True
           asyncio.create_task(self.fetch())

       async def fetch(self):
           try:
               data = await fetch_json(HOST, PATH)
               self.temp = data["current"]["temperature_2m"]
           except Exception as e:
               print(f"[{self.name}] fetch failed: {e!r}")
           finally:
               self.fetching = False
   ```

4. **Start it on a button, show it when it lands:**

   ```python
       def run_foreground(self):
           if {{ facts.buttons.app_1 }}:
               self.start_fetch()
           temp = getattr(self, "temp", None)
           if temp is not None and temp != getattr(self, "shown", None):
               self.shown = temp
               print(f"[{self.name}] {temp}")          # or set a label (see lvgl-hello)
   ```

5. Save, **Ctrl+D**, open your app, press **{{ facts.buttons.app_1_label }}**, and try the other
   buttons straight away. They answer while the fetch runs.

**✅ Done when** your app fetches web data, and the badge stays responsive the whole time.

## What just happened

`requests` *blocks*: it sits in a loop waiting for bytes. `asyncio.open_connection`
gives you a **stream** whose reads and writes are `await`able. When there's nothing to
read yet, your task steps aside and everyone else gets a turn (see [[asyncio-basics]]).

The shape in step 3 is the one to remember: **a sync app starts an async task, the task
writes its result into `self`, and the app checks `self` each call.** It's the same idea
as [[pass-data]]: a shared variable for "the latest value," plus a flag so you never
start two fetches at once.

The task you started isn't the app's own task (that one belongs to `BaseApp`), so
nothing stops it for you. A fetch ends on its own, which makes that fine here. A task
that loops forever is different: keep a reference (`self.poller = asyncio.create_task(...)`)
and call `self.poller.cancel()` when your app stops needing it. Inside the task, a
`try`/`finally` around the loop runs your clean-up when the cancel arrives.

Two catches:

- **DNS still blocks.** Looking up the host's name happens before the connection, and
  doesn't `await`. It's usually quick, but on bad WiFi it can stall for a moment.
- **This is plain HTTP.** For `https`, pass `ssl=True` and port 443 to
  `open_connection`, if your build supports it. Or install the `aiohttp` library
  (`mpremote mip install aiohttp`), which does both for you.

## Stuck?

| Symptom | Fix |
|---|---|
| `ValueError` splitting the reply | The server sent no body, or redirected you to `https`. Print `reply[:200]`. |
| `OSError: -202` | DNS failed. Is the badge still on WiFi? |
| A second press does nothing | That's the `fetching` flag. If it sticks at `True`, the task died before `finally`; look for a traceback. |
| `AttributeError: ... 'create_task'` | The firmware imports asyncio under another name (2025: `aio`). Use that, or `import asyncio`. |

## Have fun!

- Fetch every 10 minutes from `run_background()`, so the value is always fresh when
  you open the app.
- Show a spinner on the LEDs while `self.fetching` is `True` (see [[animate-leds]]).
- Fetch two different APIs at once with `asyncio.gather`.
- A weather badge: a forecast refreshed every 15 minutes, with a three-color icon for each day (see [[eink-images]]).
