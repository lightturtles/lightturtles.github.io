---
id: web-data
title: Fetch data from the web (requests and JSON)
label: Fetch data from the web
topic: wifi
workshop: false
needs: [wifi-join]
time: 25 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Ask a website for some data, pull out the one number you want, and see why
the badge stutters while it waits.

## You need

- Your badge on WiFi (see [[wifi-join]])

## Steps

1. **Fetch some text.** At `>>>`, after joining WiFi:

   ```python
   import requests
   r = requests.get("{{ facts.wifi.test_url }}")
   r.status_code       # 200 means OK
   r.text
   r.close()
   ```

2. **Fetch JSON.** Most web APIs answer in **JSON**: text that looks like Python dicts
   and lists. This one is the current temperature in Pasadena:

   ```python
   r = requests.get("https://{{ facts.wifi.json_host }}{{ facts.wifi.json_path }}")
   data = r.json()
   r.close()
   data
   ```

3. **Dig out one value.** Read the printout, then follow the keys down to the number:

   ```python
   data["current"]["temperature_2m"]
   data["current_units"]["temperature_2m"]
   ```

4. **Time it.**

   ```python
   import time
   t0 = time.ticks_ms()
   r = requests.get("https://{{ facts.wifi.json_host }}{{ facts.wifi.json_path }}")
   temp = r.json()["current"]["temperature_2m"]
   r.close()
   time.ticks_diff(time.ticks_ms(), t0)
   ```

   Try it a few times. How long? How much does it vary?

5. **Feel the stutter.** Put the fetch in your app, on **{{ facts.buttons.app_1_label }}**:

   ```python
           if {{ facts.buttons.app_1 }}:
               r = requests.get("https://{{ facts.wifi.json_host }}{{ facts.wifi.json_path }}")
               try:
                   self.temp = r.json()["current"]["temperature_2m"]
               finally:
                   r.close()
               print(f"[{self.name}] {self.temp}")
   ```

   Open your app, press **{{ facts.buttons.app_1_label }}**, and immediately press other
   buttons. Nothing responds until the reply arrives. If you have an LED animation
   running (see [[animate-leds]]), watch it freeze.

**✅ Done when** you've pulled one number out of a JSON reply, and you know how long a
request takes on your network.

## What just happened

`requests.get()` does a lot: look up the name (DNS), connect, set up encryption for
`https`, send the request, wait for the server, and read the reply. Every one of those
steps waits on the network, and `requests` waits by *blocking*: nothing else on the
badge runs until it's done. That's the stutter. [[fetch-without-freezing]] fixes it.

**Habits that keep the badge happy:**

- **Always `close()`.** Each open response holds a socket and memory. The badge only
  has a few sockets; leak them and requests start failing. `try`/`finally` makes sure.
- **Ask for small replies.** Many APIs let you pick fields (like `current=temperature_2m`
  above). A big reply has to fit in RAM all at once (see [[out-of-memory]]).
- **Fetch rarely.** Weather changes every few minutes, not every second. Once every
  10 minutes is plenty, and kinder to free APIs.
- **Expect failure.** Conference WiFi drops. Wrap fetches in `try`/`except OSError`,
  and keep showing the last good value.

<!-- TODO(diagram): timeline of one request (DNS, connect, TLS, wait, read) with the badge's other tasks blocked underneath -->

## Stuck?

| Symptom | Fix |
|---|---|
| `ImportError: no module named 'requests'` | Older firmware calls it `urequests`. Or `mpremote mip install requests`. |
| `OSError: -202` or `-2` | DNS failed: not connected, or no internet. Check `wlan.isconnected()`. |
| `OSError: [Errno 12] ENOMEM` | Not enough RAM for `https`. Free some, or try the `http://` version of the URL. |
| `KeyError` | The reply isn't shaped how you expected. Print `data` and follow its keys. |
| `ValueError` from `.json()` | The reply isn't JSON (an error page?). Print `r.text`. |

## Have fun!

- Show tomorrow's forecast instead: add `&daily=temperature_2m_max` to the URL.
- Find another free JSON API (space station position, bus times, your GitHub stars)
  and show one number from it.
- Remember the last good value with a timestamp, and show how old it is.
- "They fight crime!" from the real website: fetch theyfightcrime.org (check that it's still up) and pull the sentence out of the HTML with `str.find()`. It's HTML, not JSON, so read the page source on your laptop first, and keep the response small (see [[out-of-memory]]).
