---
layout: skill-tree
title: "Supercon Ten Badge Skill Tree"
type: skill-tree
event: Supercon 2026
subjects:
  - micropython
  - badges
date: 2026-10-12
excerpt: >
  A hex "skill tree" for hacking the Supercon Ten badge. Start at the top,
  follow the red tiles, and branch out wherever you like. Each tile links to
  step-by-step instructions.

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

  wifi:
    ssid: Supercon             # TODO: conference network name
    password: ""               # TODO
    test_url: http://wttr.in/Pasadena?format=3   # TODO: plain-text URL that works on the conference network

# ── Skill tree layout (rewritten by _scripts/skilltree_layout.py) ─────────
# Hand-edit freely: change a tile's number in `tiles:` to move it, or swap two
# numbers to swap tiles. Re-running keeps your edits and only slots in new skills.
palette:
  core: "#046307"
  developmental: "#c4622d"
  stretch: "#6b4f3f"

# Slots, top row first. Indented rows sit half a hex to the right.
grid: |
  1   2   3   4   5   6   7   8
    9   10  11  12  13  14  15  16
  17  18  19  20  21  22  23  24
    25  26  27  28  29  30  31  32
  33  34  35  36  37  38  39  40
    41  42  43  44  45  46  47  48
  49  50  51  52  53  54  55  56
    57  58  59  60  61  62  63  64
  65  66  67  68  69  70  71  72
    73  74  75  76  77  78  79  80
  81  82  83  84  85  86  87  88

tiles:
  5: repl
  11: wifi-join
  12: map-firmware
  13: one-led
  14: asyncio-basics
  19: sao-pinout
  20: backup
  21: read-button
  22: inspect-firmware
  23: firmware-diagram
  26: i2c-scan
  27: update-firmware
  28: name-badge
  29: resets
  30: all-leds
  35: sao-blink
  36: add-a-library
  37: break-and-restore
  38: save-settings
  39: mount-and-run
  42: first-app
  43: badge-diff
  44: start-fresh
  45: post-mortem
  46: recover
  50: live-data
  51: hog-the-cpu
  53: lvgl-hello
  54: app-crash
  58: share-hardware
  60: app-screen
  61: eink-refresh
  69: demo
# ── end of layout ─────────────────────────────────────────────────────────
---
Made for the *Badge Hacking for Beginners* workshop at Hackaday Supercon 2026, but
open to everyone. Tick off a skill with the circle on its hex, or on its page
(saved in this browser only).
