---
id: wifi-join
title: Join WiFi from the REPL
label: Join WiFi
tier: developmental
difficulty: 3
group: connectivity
icon: wifi
needs: [repl]
time: 10 min
touches: []
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Get the badge onto a WiFi network and find its IP address.

## You need

- Your badge, connected and showing `>>>` (see [[repl]])
- A **2.4 GHz** WiFi network and its password. The conference network is
  **{{ facts.wifi.ssid }}**; a phone hotspot works too.

## Steps

1. Turn on the WiFi radio in "station" mode (it joins a network rather than creating one):

   ```python
   import network
   wlan = network.WLAN(network.STA_IF)
   wlan.active(True)
   ```

2. Look around:

   ```python
   for net in wlan.scan():
       print(net[0], net[3])     # name, signal strength (closer to 0 = stronger)
   ```

3. Join:

   ```python
   wlan.connect("{{ facts.wifi.ssid }}", "{{ facts.wifi.password }}")
   ```

4. Joining takes a few seconds. Check:

   ```python
   wlan.isconnected()
   wlan.ifconfig()      # (IP address, netmask, gateway, DNS)
   ```

**✅ Done when** `isconnected()` says `True` and you've written down the badge's IP address.

## What just happened

The ESP32 has a WiFi radio built in; `network.WLAN` is MicroPython's handle on it. The
first number in `ifconfig()` is the address the router handed out to your badge. Any
other device on the same network can now reach it.

The badge only speaks **2.4 GHz** WiFi. A network that's 5 GHz-only won't show up in the
scan at all.

Conference WiFi, with thousands of devices in one room, is the least reliable network
you'll ever use. If it doesn't work, it's probably not you. Try a phone hotspot.

## Stuck?

| Symptom | Fix |
|---|---|
| Your network isn't in the scan | It's 5 GHz-only, or too far away. Use a 2.4 GHz network or hotspot. |
| `isconnected()` stays `False` | Check the password (it's case-sensitive). Wait 10 seconds and check again. |
| `OSError: Wifi Internal Error` | Run `wlan.active(False)`, then `wlan.active(True)`, and connect again. |
| Badge's own radio features stop working | The firmware may use the radio too. **Ctrl+D** to give it back. |

<!-- TODO(verify): does this year's firmware use the ESP32's radio (ESP-NOW, etc.)? Note any conflicts. -->

## Have fun!

- Set the clock: `import ntptime, time; ntptime.settime(); time.localtime()` (the time is UTC).
- Fetch a web page: `import requests; requests.get("http://example.com").text[:200]`
- Make the badge join WiFi on its own at startup with a setting saved in [[save-settings]].
