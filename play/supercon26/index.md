---
layout: metro-map
title: "Supercon Ten Badge Skill Map"
type: skill-tree
event: Supercon 2026
subjects:
  - micropython
  - badges
date: 2026-10-14
excerpt: >
  A metro map of skills for hacking the Supercon Ten badge. Start at the top
  left, ride any line you like, and transfer wherever lines meet.

# Details likely to change before/during Supercon. Skill pages that start with
# {% include facts.html %} can use these as {{ facts.<path> }}.
facts:
  badge:
    name: Supercon Ten Badge
    mcu: ESP32-S3              # TODO: confirm
    devices: display, buttons, LEDs, SAO I2C bus, radio   # TODO: hardware the Badge object holds

  display:
    type: e-ink
    width: TBD                 # TODO: pixels
    height: TBD
    colors: black, white and red   # TODO: confirm
    third_color: red               # TODO: confirm
    refresh_s: TBD             # TODO: seconds for a full refresh
    lvgl_period_ms: 33         # how often LVGL's task redraws (2025 value; hardware/lvgl_setup.py)
    datasheet: TBD             # TODO: URL of the e-ink panel's datasheet
    sample_image: images/wrencher.png   # TODO: an image that ships on the badge (2025 value)

  usb:
    bridge: native             # TODO: confirm. "native" (chip's own USB), or CH340 / CP210x

  power:
    reset_button: RESET        # TODO: label printed next to the reset button
    power_off: slide the power switch to OFF   # TODO: confirm there's a switch (else: unplug the battery)

  thonny:
    interpreter: MicroPython (ESP32)   # entry name in Thonny's interpreter list

  leds:
    type: WS2812               # addressable RGB ("NeoPixel")
    pin: 21                    # TODO: GPIO number of the LED data line
    count: 8                   # TODO: number of LEDs in the chain

  buttons:
    example_label: A           # TODO: label printed next to the button used in the button skill
    example_pin: 0             # TODO: its GPIO number (and confirm it's a direct GPIO, not via an expander)
    # Checking buttons from inside an app (2025 values: the F1–F5 keys)
    app_1_label: F1            # TODO: label printed next to it
    app_1: self.badge.keyboard.f1()   # TODO: "was it pressed?" (True once per press)
    app_2_label: F2
    app_2: self.badge.keyboard.f2()
    home_label: F5             # the button that leaves an app
    home: self.badge.keyboard.f5()

  battery:
    adc_pin: TBD               # TODO: GPIO of the battery-sense divider
    divider: 2                 # TODO: battery volts / pin volts

  config:
    module: badge.config       # TODO: confirm import path (badge.config? board.config?)
    file: /config.json         # TODO: where the settings are stored on the filesystem

  # The "official" firmware: a folder in the badge's repo that mirrors the
  # badge's filesystem exactly. Values below are from the 2025 badge.
  firmware:
    repo: https://github.com/Hack-a-Day/2026-Supercon-Badge   # TODO: real repo URL
    folder: badge              # TODO: folder in the repo that gets copied to the badge
    zip_folder: 2026-Supercon-Badge-main   # TODO: top folder name inside GitHub's "Download ZIP"
    version_check: os.listdir('/')         # TODO: how to tell which release is on a badge (VERSION file?)
    badge_import: from hardware.badge import badge_obj   # TODO: how to reach the firmware's Badge object at >>>
    app_list: main.py          # TODO: the file that creates the apps and builds the menu
    user_apps: apps/userA.py … apps/userD.py   # TODO: confirm the "yours to edit" app files
    user_app: apps/userA.py
    user_app_name: User A      # TODO: the name main.py gives it (shows in prints)
    user_app_menu: User → User A   # TODO: how to open it from the menu
    user_app_2: apps/userB.py  # a second "yours to edit" slot
    template_app: apps/template_app.py   # TODO: confirm
    state_dir: data            # TODO: folder the badge writes its own data to (keys, settings)
    lib_dir: lib               # where add-on libraries go (on sys.path)
    pins_file: hardware/board.py   # TODO: file that names the GPIO pins
    usb_drive: false           # TODO: true if the badge shows up as a USB drive (CircuitPython-style)
    safe_mode: null            # TODO: e.g. "hold the A button while pressing RESET"; null if none

  name_badge:
    app: Nametag               # TODO: menu name of the name-tag app
    file: apps/nametag.py      # TODO: its source file
    find: font_montserrat_42   # TODO: a value that's safe for beginners to change
    replace: font_montserrat_28
    what: the font size of your name
    text: "Hello, my name is"   # TODO: a fixed string the app shows, safe to change
    image: images/wrencher.png     # TODO: the image file it shows (if any)

  sao:
    count: 1                   # TODO: number of SAO headers
    sda: 4                     # TODO: GPIO numbers (2025 values)
    scl: 5
    gpio1: 7
    gpio2: 6
    i2c_id: 0                  # TODO: I2C controller the firmware uses for the SAO bus
    i2c_attr: sao_i2c          # TODO: the firmware's SAO I2C bus, as badge_obj.<this>

  sensor:                      # the I2C sensor handed out at the workshop
    name: TBD                  # TODO
    address: TBD               # TODO: e.g. 0x44
    register: TBD              # TODO: register holding the reading
    bytes: 2                   # TODO
    id_register: TBD           # TODO: a "who am I" / ID register, if it has one
    id_value: TBD              # TODO: what that register should read
    datasheet: TBD             # TODO: URL
    units: °C

  wifi:
    ssid: Supercon             # TODO: conference network name
    password: ""               # TODO
    test_url: http://wttr.in/Pasadena?format=3   # TODO: plain-text URL that works on the conference network
    json_host: api.open-meteo.com
    json_path: /v1/forecast?latitude=34.15&longitude=-118.14&current=temperature_2m   # Pasadena's temperature, as small JSON

  espnow:
    channel: 1                 # TODO: WiFi channel badges use for ESP-NOW (the conference AP's, if badges join it)
    firmware_uses: TBD         # TODO: does the stock firmware use ESP-NOW itself? (then Ctrl+C before trying it)

  clock:
    utc_offset_h: -7           # Pasadena: PDT (UTC−7) until 2 a.m. Sunday Nov 1, 2026, then PST (UTC−8)
    ntp_host: pool.ntp.org

  sleep:
    wake_label: TBD            # TODO: button that wakes the badge (must be on an RTC-capable GPIO, 0–21 on the S3)
    wake_pin: TBD              # TODO: its GPIO number

# The map is generated from skills.yml; to change it, edit that file and run
#   python3 _scripts/metro_layout.py play/supercon26

# ── Metro layout (generated by _scripts/metro_layout.py from skills.yml) ──
# Don't edit: change skills.yml and rerun the script.
metro:
  width: 1780
  height: 875
  lines:
    - {"topic": "setup", "title": "Setup & Recovery", "color": "#4a4a48", "d": "M130,70 H780"}
    - {"topic": "modify-app", "title": "Software: Modify an app", "color": "#5aa89a", "d": "M278,70 V110 L323,155 H910"}
    - {"topic": "write-app", "title": "Software: Write your own app", "color": "#2f7f73", "d": "M390,155 V280 L435,325 H1690"}
    - {"topic": "gpio", "title": "Hardware: GPIO", "color": "#c4622d", "d": "M139,70 V620 L184,665 H910"}
    - {"topic": "i2c", "title": "Hardware: I2C", "color": "#8f4a1f", "d": "M269,70 V450 L314,495 H910"}
    - {"topic": "display", "title": "Hardware: Display (e-ink + LVGL)", "color": "#c9902f", "d": "M520,325 V365 L565,410 H1690"}
    - {"topic": "wifi", "title": "Hardware: WiFi", "color": "#3b5b92", "d": "M130,70 V705 L175,750 H650"}
    - {"topic": "espnow", "title": "Hardware: ESP-NOW", "color": "#7a5ea8", "d": "M260,750 V790 L305,835 H780"}
    - {"topic": "workflow", "title": "Build & debug: Workflow", "color": "#5e9b45", "d": "M260,70 V535 L305,580 H650"}
    - {"topic": "debugging", "title": "Build & debug: Debugging", "color": "#046307", "d": "M520,155 V195 L565,240 H1300"}
  stations:
    - {"id": "repl", "topic": "setup", "x": 130, "y": 70, "label": ["Connect to the", "REPL"], "workshop": true, "start": true}
    - {"id": "map-firmware", "topic": "setup", "x": 260, "y": 70, "label": ["Find the files"], "workshop": true}
    - {"id": "explore-badge", "topic": "setup", "x": 390, "y": 70, "label": ["Explore the", "badge object"]}
    - {"id": "backup", "topic": "setup", "x": 520, "y": 70, "label": ["Back up your", "badge"], "workshop": true}
    - {"id": "update-firmware", "topic": "setup", "x": 650, "y": 70, "label": ["Update the", "firmware"], "workshop": true}
    - {"id": "start-fresh", "topic": "setup", "x": 780, "y": 70, "label": ["Start fresh"]}
    - {"id": "firmware-diagram", "topic": "modify-app", "x": 390, "y": 155, "label": ["Diagram the", "firmware"]}
    - {"id": "name-badge", "topic": "modify-app", "x": 520, "y": 155, "label": ["Edit the base", "app"], "also": ["update-firmware"], "workshop": true}
    - {"id": "resets", "topic": "modify-app", "x": 650, "y": 155, "label": ["Three kinds of", "reset"]}
    - {"id": "badge-diff", "topic": "modify-app", "x": 780, "y": 155, "label": ["What did I", "change?"], "also": ["backup"]}
    - {"id": "share-apps", "topic": "modify-app", "x": 910, "y": 155, "label": ["Share and", "install apps"], "also": ["update-firmware"], "workshop": true}
    - {"id": "first-app", "topic": "write-app", "x": 520, "y": 325, "label": ["Your first app"]}
    - {"id": "asyncio-basics", "topic": "write-app", "x": 650, "y": 325, "label": ["Take turns with", "asyncio"]}
    - {"id": "hog-the-cpu", "topic": "write-app", "x": 780, "y": 325, "label": ["Preventing", "freezes"], "also": ["break-and-restore"]}
    - {"id": "fsm", "topic": "write-app", "x": 910, "y": 325, "label": ["Break work into", "states"]}
    - {"id": "on-time", "topic": "write-app", "x": 1040, "y": 325, "label": ["Doing things on", "time"]}
    - {"id": "pass-data", "topic": "write-app", "x": 1170, "y": 325, "label": ["Passing data", "between tasks"]}
    - {"id": "share-hardware", "topic": "write-app", "x": 1300, "y": 325, "label": ["Share the LEDs"], "also": ["all-leds"]}
    - {"id": "background-app", "topic": "write-app", "x": 1430, "y": 325, "label": ["A", "background-only", "app"]}
    - {"id": "save-settings", "topic": "write-app", "x": 1560, "y": 325, "label": ["Save across", "reboots"]}
    - {"id": "out-of-memory", "topic": "write-app", "x": 1690, "y": 325, "label": ["Running out of", "memory"]}
    - {"id": "one-led", "topic": "gpio", "x": 260, "y": 665, "label": ["Light one LED"], "workshop": true}
    - {"id": "read-button", "topic": "gpio", "x": 390, "y": 665, "label": ["Read a button"], "workshop": true}
    - {"id": "all-leds", "topic": "gpio", "x": 520, "y": 665, "label": ["Light all the", "LEDs"]}
    - {"id": "animate-leds", "topic": "gpio", "x": 650, "y": 665, "label": ["Animate without", "blocking"], "also": ["on-time"]}
    - {"id": "interrupts", "topic": "gpio", "x": 780, "y": 665, "label": ["Polling vs.", "interrupts"], "also": ["asyncio-basics"]}
    - {"id": "sao-blink", "topic": "gpio", "x": 910, "y": 665, "label": ["Blink on the SAO"], "also": ["sao-pinout"]}
    - {"id": "sao-pinout", "topic": "i2c", "x": 390, "y": 495, "label": ["SAO pinout, and", "connect your", "sensor"], "workshop": true}
    - {"id": "i2c-scan", "topic": "i2c", "x": 520, "y": 495, "label": ["Scan for I2C", "devices"], "workshop": true}
    - {"id": "read-register", "topic": "i2c", "x": 650, "y": 495, "label": ["Read a register"], "workshop": true}
    - {"id": "real-units", "topic": "i2c", "x": 780, "y": 495, "label": ["Raw bytes to", "real units"], "workshop": true}
    - {"id": "add-a-library", "topic": "i2c", "x": 910, "y": 495, "label": ["Add a library"]}
    - {"id": "lvgl-hello", "topic": "display", "x": 650, "y": 410, "label": ["Hello, LVGL"]}
    - {"id": "app-screen", "topic": "display", "x": 780, "y": 410, "label": ["Layout and fonts"]}
    - {"id": "draw-pixels", "topic": "display", "x": 910, "y": 410, "label": ["Draw pixels,", "shapes and", "charts"]}
    - {"id": "eink-images", "topic": "display", "x": 1040, "y": 410, "label": ["Images on a", "3-color panel"]}
    - {"id": "use-red", "topic": "display", "x": 1170, "y": 410, "label": ["Use red on", "purpose"]}
    - {"id": "eink-refresh", "topic": "display", "x": 1300, "y": 410, "label": ["Why e-ink is", "slow"]}
    - {"id": "eink-updates", "topic": "display", "x": 1430, "y": 410, "label": ["Update the", "screen well"], "also": ["on-time"]}
    - {"id": "qr-code", "topic": "display", "x": 1560, "y": 410, "label": ["Show a QR code"]}
    - {"id": "sleep-with-image", "topic": "display", "x": 1690, "y": 410, "label": ["Sleep with your", "image showing"]}
    - {"id": "wifi-join", "topic": "wifi", "x": 260, "y": 750, "label": ["Join WiFi"]}
    - {"id": "web-data", "topic": "wifi", "x": 390, "y": 750, "label": ["Fetch data from", "the web"]}
    - {"id": "fetch-without-freezing", "topic": "wifi", "x": 520, "y": 750, "label": ["Fetch without", "freezing"], "also": ["asyncio-basics"]}
    - {"id": "ntp-time", "topic": "wifi", "x": 650, "y": 750, "label": ["Set the clock"]}
    - {"id": "espnow-hello", "topic": "espnow", "x": 390, "y": 835, "label": ["Badge-to-badge", "hello"]}
    - {"id": "espnow-in-app", "topic": "espnow", "x": 520, "y": 835, "label": ["Messages in your", "app"], "also": ["pass-data"]}
    - {"id": "espnow-messages", "topic": "espnow", "x": 650, "y": 835, "label": ["Design a message"]}
    - {"id": "espnow-nearby", "topic": "espnow", "x": 780, "y": 835, "label": ["Who's nearby?"]}
    - {"id": "repl-setup", "topic": "workflow", "x": 390, "y": 580, "label": ["A faster REPL"]}
    - {"id": "drive-app", "topic": "workflow", "x": 520, "y": 580, "label": ["Drive your app", "by hand"], "also": ["first-app"]}
    - {"id": "mount-and-run", "topic": "workflow", "x": 650, "y": 580, "label": ["Work from your", "laptop"], "also": ["backup"]}
    - {"id": "break-and-restore", "topic": "debugging", "x": 650, "y": 240, "label": ["Read a traceback"]}
    - {"id": "post-mortem", "topic": "debugging", "x": 780, "y": 240, "label": ["Post-mortem"]}
    - {"id": "bp", "topic": "debugging", "x": 910, "y": 240, "label": ["Pause and poke"]}
    - {"id": "better-prints", "topic": "debugging", "x": 1040, "y": 240, "label": ["Better print", "debugging"], "also": ["first-app"]}
    - {"id": "log-and-plot", "topic": "debugging", "x": 1170, "y": 240, "label": ["Log and plot"]}
    - {"id": "recover", "topic": "debugging", "x": 1300, "y": 240, "label": ["Boot rescue"]}
# ── end of metro layout ──
---
Made for the *Badge Hacking for Beginners* workshop at Hackaday Supercon 2026, but
open to everyone. Each line is a topic; ride it in order, or hop off wherever you
like. Tick off a station with its circle (saved in this browser only). Stations
with a red ring are the ones the workshop covers.
