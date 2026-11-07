---
layout: post
title: "Badge Hacking for Beginners (Hackaday Supercon 2026)"
date: 2026-11-07
type: tutorial
subjects:
  - firmware
  - hardware
  - teaching
venue: Hackaday Supercon
excerpt: >
  Workshop materials from Hackaday Supercon 2026: a two-hour, hands-on
  introduction to hacking the Supercon Ten badge, built around 14 skills
  from the badge skill map and ending with a live I2C sensor reading on
  your name badge.
documents:
  - title: "Slides (PDF)"
    url: /assets/badge_hacking_for_beginners_26/badge_hacking_for_beginners.pdf
    type: pdf
  - title: "Slides (HTML)"
    url: /assets/badge_hacking_for_beginners_26/badge_hacking_for_beginners.html
    type: html
---

*Workshop given at [Hackaday Supercon 2026](https://hackaday.io/superconference/), November 2026.*

![The Supercon Ten badge skill map, drawn as a metro map: colored lines for setup and recovery, modifying an app, writing your own app, GPIO, I2C, the display, WiFi, ESP-NOW, and debugging, with workshop skills marked by rings]({{ '/play/supercon26/metro-map.png' | relative_url }})

Every Supercon, a few hundred people get handed a brand-new badge and a weekend to do something with it. Plenty of them have never written a line of MicroPython or plugged anything into an SAO header, and the gap between "it turned on" and "I made it do something" can feel pretty wide. This workshop was for closing that gap.

The goal was concrete: by the end of two hours, every participant should have a real I2C sensor plugged into their badge, with its reading showing up live on their own name badge app. Getting there meant learning to connect to the badge, find your way around its files, keep a backup so you can't break anything permanently, talk to hardware from the REPL, and edit an app that was already running.

**The plan**

The two hours broke down into a 20-minute intro, 90 minutes of hands-on work, and a 10-minute wrap-up where everyone planned the hack they wanted to build next and gave some feedback on the workshop. The hands-on part was built entirely on the [Supercon Ten badge skill map]({{ '/play/supercon26/' | relative_url }}), a "metro map" of short, self-contained lessons. Fourteen of those skills were marked as workshop skills, and those were the ones we worked through together.

Before we started, I asked everyone to follow three rules:

1. **No troll left behind.** Share what you discover ("Check out what I just found!") and ask about what your neighbors are doing ("Wait, what are you doing there?").
2. **Be curious, creative, and subversive.** "I wonder what would happen if..." is the whole point of badge hacking.
3. **Periodically stop and summarize.** "So doing X makes Y happen." Draw a picture of how it works. That's how a pile of steps turns into something you actually understand.

**What you needed**

- A way to talk to the badge: [Thonny](https://thonny.org/), the browser-based [Viper IDE](https://viper-ide.org/) (in a Chrome-based browser like Chrome, Edge, Brave, or Opera), or [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) if you prefer the command line.
- A clone of the [official badge repo](https://github.com/Hack-a-Day/2026-Billboard_Badge), which has the stock firmware files.
- An I2C sensor and a [Qwiic / STEMMA QT cable with female sockets](http://adafrui.it/4209), graciously donated by [DigiKey](https://www.digikey.com/). There were four kinds to choose from, all with different I2C addresses so they could share the bus:
  - [Adafruit AHT20](https://www.adafruit.com/product/4566) (temperature and humidity)
  - [Adafruit BH1750](https://www.adafruit.com/product/4681) (light)
  - [SparkFun LIS3DH, SEN-29528](https://www.sparkfun.com/sparkfun-triple-axis-accelerometer-breakout-lis3dh-qwiic.html) (motion)
  - [SparkFun Capacitive Touch Slider, SEN-15344](https://www.sparkfun.com/products/15344) (touch)

**The 14 workshop skills**

The skills ran along four lines of the map. Each one is a short lesson with its own page, so you can work through them on your own if you weren't there.

*Setup and recovery.* First, get comfortable with the badge as it shipped, and make sure nothing you do later is permanent.

- [Use your badge]({{ '/play/supercon26/use-badge/' | relative_url }}): the buttons, the menu, and the apps that came on it.
- [Connect to the REPL]({{ '/play/supercon26/repl/' | relative_url }}): connect over USB-C and run your first line of code.
- [Find the files]({{ '/play/supercon26/map-firmware/' | relative_url }}): what's on the badge, and which files are yours to change.
- [Back up your badge]({{ '/play/supercon26/backup/' | relative_url }}): copy your files to your laptop.
- [Update the firmware]({{ '/play/supercon26/update-firmware/' | relative_url }}): get the latest firmware without losing your files.

*GPIO.* Next, control some hardware directly from the REPL.

- [Light one LED]({{ '/play/supercon26/one-led/' | relative_url }})
- [Read a button]({{ '/play/supercon26/read-button/' | relative_url }})

*I2C.* Then, get a sensor talking to the badge.

- [SAO pinout, and connect your sensor]({{ '/play/supercon26/sao-pinout/' | relative_url }}): figure out which SAO pin is which and wire up the sensor.
- [Scan for I2C devices]({{ '/play/supercon26/i2c-scan/' | relative_url }}): confirm the badge can see it.
- [Add a library]({{ '/play/supercon26/add-a-library/' | relative_url }}): copy a MicroPython driver onto the badge.
- [Use a library]({{ '/play/supercon26/use-a-library/' | relative_url }}): get a real reading from your sensor.

*Modify an app.* Finally, put it all together.

- [Edit the base app]({{ '/play/supercon26/name-badge/' | relative_url }}): put your name on the name badge app by changing one line of code.
- [Your sensor on your badge]({{ '/play/supercon26/sensor-badge/' | relative_url }}): show your sensor's live reading on your name badge.
- [Share and install apps]({{ '/play/supercon26/share-apps/' | relative_url }}): install someone else's app, and share yours.

**Going further**

The fourteen workshop skills are only a small part of the map. The [full skill map]({{ '/play/supercon26/' | relative_url }}) has dozens more: writing your own app from scratch with asyncio, drawing on the three-color e-ink display with LVGL, fetching data over WiFi, sending messages badge-to-badge with ESP-NOW, and a whole set of debugging lessons for when things go wrong. Start wherever you left off, ride any line you like, and transfer wherever the lines meet.
