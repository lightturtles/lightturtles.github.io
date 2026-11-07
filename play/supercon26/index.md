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
#
# Values marked "fw:" were read from the stock firmware copied off a badge on
# 2026-11-06 (file:line). "REPL:" = still needs a check on a real badge.
# "DECISION:" = depends on how a lesson gets rewritten (step 1 of the plan).
facts:
  badge:
    name: Supercon Ten Badge   # fw: lib/*.py docstrings call it the "Billboard Badge"
    mcu: ESP32-S3              # REPL: os.uname() "ESP32S3 module with Octal-SPIRAM" (~5.9 MB free)
    devices: display, buttons, LEDs, SAO I2C bus, radio   # fw: no single Badge object; each is its own lib/ module. REPL: network, espnow, bluetooth all in the build

  display:
    type: e-ink
    width: 960                 # fw: lib/epd.py display_width
    height: 672                # fw: lib/epd.py display_height
    colors: black, white and red   # fw: lib/epd.py has a black and a red framebuffer
    third_color: red
    refresh_s: TBD             # REPL: global_update() prints its own ms timings during a refresh
    lvgl_period_ms: null       # fw: no LVGL timer task. Apps call lvgl.refr_now() and then display.update() themselves
    datasheet: TBD             # TODO: 9.69" Pervasive Displays panel (fw: lib/epd.py pdi_size 0x96); driver from github.com/PervasiveDisplays/EPD_Driver_GU_large
    sample_image: /data/graphics/supercon-x-splash.png   # fw: main.py first-boot splash

  usb:
    bridge: native             # confirmed: shows up as /dev/ttyACM0 (no USB-serial chip)

  power:
    reset_button: RESET        # TODO: label printed next to the reset button
    power_off: slide the power switch to OFF   # BOM: SW3 is a slide switch (MST22D18G2); battery pads TP1/TP2. TODO: confirm label
    battery: TBD               # TODO: what powers it without USB (the PCB mentions 18650)

  thonny:
    interpreter: MicroPython (ESP32)   # entry name in Thonny's interpreter list

  leds:
    type: WS2812               # fw: lib/led_bar.py uses neopixel
    pin: 38                    # fw: lib/led_bar.py WS2812_PIN
    count: 8                   # fw: lib/led_bar.py NUM_LEDS

  buttons:
    # fw: lib/button.py. Five buttons, all direct GPIOs with pull-ups (active low).
    # Note in the source: Menu +/- are swapped on the silkscreen.
    example_label: User A      # TODO: confirm the printed label
    example_pin: 39            # fw: lib/button.py USER_A_PIN
    # Checking buttons from inside an app: from lib.button import UserA, UserB
    app_1_label: User A        # TODO: confirm the printed label
    app_1: UserA.pressed()     # fw: True once per press
    app_2_label: User B
    app_2: UserB.pressed()
    home_label: Menu + or Menu −   # fw: lib/app_switcher.py; the switcher leaves the app itself
    home: null                 # DECISION: apps no longer check a "home" button (lessons using this need a rewrite)

  battery:
    adc_pin: 14                # fw: lib/board.py BATT_V_SNS_PIN (reg_in_v_sns); reads USB *or* battery, whichever powers the regulator
    divider: 2                 # fw: lib/board.py "1/2 voltage divider"

  config:
    module: lib.json_configs   # fw: load() / store() / append(entry, name)
    file: /data/panel_config.json   # fw: main.py keeps load_counter here (relative path "data/panel_config.json" in code)

  # The "official" firmware: a folder in the badge's repo that mirrors the
  # badge's filesystem exactly.
  firmware:
    micropython: 1.24.1        # REPL: os.uname() release; build "v1.20.0-2527.g44aa2b153.dirty on 2026-11-04" (LVGL fork). Decides which modules exist (no machine.I2CTarget)
    snapshot: 6ba6dd8          # upstream commit the lessons are checked against ("Add firmware", 2026-11-06); matches the files copied off a badge
    repo: https://github.com/Hack-a-Day/2026-Billboard_Badge
    folder: firmware/badge     # folder in the repo that mirrors the badge
    zip_folder: 2026-Billboard_Badge-main   # top folder inside GitHub's "Download ZIP"
    update_script: firmware/scripts/update.py   # the repo's own tool: ls (compare), pull (copy everything off), push (make the badge match firmware/badge, deleting extras outside /data)
    version_check: os.listdir('/')         # fw: no VERSION file. TODO: decide how to tell releases apart
    badge_import: from lib.sao import i2c  # fw: no Badge object; DECISION: lessons that use this import the module they need
    app_list: lib/app_switcher.py   # fw: finds every /apps/*.py at boot (skips _*.py, base_app, template) and writes /data/user_apps.py
    user_apps: any new .py file in apps/   # fw: no userA…userD slots. DECISION: confirm wording
    user_app: apps/my_app.py   # DECISION: proposed name for the attendee's own app file
    user_app_name: My App      # DECISION: the self.name it sets (shows in prints)
    user_app_menu: Menu +/− until its LED is lit, then User A   # fw: lib/app_switcher.py + led_bar.menu_display
    user_app_2: apps/my_app_2.py   # DECISION
    template_app: apps/template.py   # fw: on the deny list, so it never appears in the menu until copied/renamed
    state_dir: data            # fw: mixes shipped files (graphics/, gallery/, schedule.csv, rendered_luts.py) with badge-written ones (panel_config.json, app_list, user_apps.py, hwconf)
    lib_dir: lib               # fw: the firmware's own modules also live here
    pins_file: lib/board.py    # fw: also lib/button.py, lib/led_bar.py, lib/sao.py, lib/epd.py each name their own pins
    usb_drive: false           # MicroPython, not CircuitPython
    safe_mode: null            # fw: boot.py is empty; no safe-mode check in main.py

  name_badge:
    app: Nametag               # fw: apps/nametag.py self.name
    file: apps/nametag.py
    find: hello.set_text("")   # fw: apps/nametag.py:52; the stock app draws two *empty* labels on the PNG
    replace: hello.set_text("Ada")
    what: the name on your badge
    image: /data/graphics/hello_i_am_blank.png   # fw: apps/nametag.py:30

  sao:
    count: 3                   # fw: lib/sao.py SAO1–SAO3, all on one I2C bus
    sda: 17                    # fw: lib/sao.py SAO_I2C_SDA
    scl: 18                    # fw: lib/sao.py SAO_I2C_SCL (400 kHz)
    gpio1: 2                   # fw: SAO1_GPIO1 (SAO2: 4/5, SAO3: 7/6)
    gpio2: 42                  # fw: SAO1_GPIO2
    i2c_id: 0                  # fw: lib/sao.py SAO_I2C_BUS
    i2c_attr: i2c              # fw: from lib.sao import i2c
    pins_file: lib/sao.py      # fw: names the SAO pins and makes the bus (400 kHz). Not imported by main.py
    connector: "A [Qwiic / STEMMA QT cable with female sockets](http://adafrui.it/4209) (comes with the sensor)"   # Adafruit 4209: JST SH to 4 female sockets

  # The four sensors handed out at the workshop (10 of each). The I2C lessons have
  # one collapsible section per sensor. All four addresses differ, so they can
  # share the bus. All are Qwiic / STEMMA QT boards.
  # Checked against product pages, the Linux cap11xx driver, and AHT20/BH1750
  # drivers on 2026-11-06; the register/command code was confirmed on real sensors
  # the same day.
  # driver/class: the workshop's own drivers, in play/supercon26/drivers/ (same
  # shape for all four: Class(i2c), .reading(), .text(), .units).
  # other_driver: an off-the-shelf MicroPython driver, for the curious (with its catch).
  drivers_url: https://lightturtles.github.io/play/supercon26/drivers/
  sensors:
    aht20:
      name: AHT20
      what: temperature and humidity
      board: Adafruit AHT20 (STEMMA QT)
      address: "0x38"
      units: °C and %RH
      page: https://www.adafruit.com/product/4566     # datasheet linked from here
      driver: aht20
      class: AHT20
      other_driver: https://github.com/targetblank/micropython_ahtx0
      other_note: "MIT-licensed and fairly complete. Check its README for which class fits an AHT20."
    bh1750:
      name: BH1750
      what: light
      board: Adafruit BH1750 (STEMMA QT)
      address: "0x23"          # 0x5C if its ADDR pin is pulled high
      units: lux
      page: https://www.adafruit.com/product/4681
      driver: bh1750
      class: BH1750
      other_driver: https://github.com/octaprog7/BH1750
      other_note: "One of several small ones; this one is spread over four files."
    lis3dh:
      name: LIS3DH
      what: motion
      board: SparkFun LIS3DH (Qwiic), SEN-29528
      address: "0x19"          # SparkFun default; 0x18 with the address jumper closed
      id_register: "0x0F"      # WHO_AM_I
      id_value: "0x33"
      units: g
      page: https://www.sparkfun.com/sparkfun-triple-axis-accelerometer-breakout-lis3dh-qwiic.html   # SparkFun's LIS3DH (Qwiic) page; the chip datasheet (ST's) is the same for every LIS3DH board
      driver: lis3dh
      class: LIS3DH
      other_driver: https://github.com/jposada202020/MicroPython_LIS3DH
      other_note: "Installs with mip, but the project is archived. It defaults to address 0x18, so pass address=0x19."
    cap1203:
      name: CAP1203
      what: touch
      board: SparkFun Capacitive Touch Slider (Qwiic), SEN-15344
      address: "0x28"          # fixed in the chip
      id_register: "0xFD"      # product ID
      id_value: "0x6D"
      units: position along the slider (%)
      page: https://www.sparkfun.com/products/15344
      driver: cap1203
      class: CAP1203
      other_driver: https://github.com/sparkfun/qwiic_cap1203_py
      other_note: "SparkFun's Python driver. Not checked on MicroPython, or with the badge's own I2C bus. A good challenge."

  wifi:
    ssid: Supercon             # TODO: conference network name
    password: ""               # TODO
    test_url: http://wttr.in/Pasadena?format=3   # TODO: plain-text URL that works on the conference network
    json_host: api.open-meteo.com
    json_path: /v1/forecast?latitude=34.15&longitude=-118.14&current=temperature_2m   # Pasadena's temperature, as small JSON

  espnow:
    channel: 1                 # TODO: WiFi channel badges use for ESP-NOW (the conference AP's, if badges join it)
    firmware_uses: false       # fw: no espnow/network code in the stock files. REPL: espnow and aioespnow are in the build

  clock:
    utc_offset_h: -7           # Pasadena: PDT (UTC−7) until 2 a.m. Sunday Nov 1, 2026, then PST (UTC−8)
    ntp_host: pool.ntp.org

  sleep:
    wake_label: TBD            # fw: RTC-capable buttons are Boot (0), Menu + (15), User B (16). DECISION: pick one
    wake_pin: TBD

# The map is generated from skills.yml; to change it, edit that file and run
#   python3 _scripts/metro_layout.py play/supercon26

# ── Metro layout (generated by _scripts/metro_layout.py from skills.yml) ──
# Don't edit: change skills.yml and rerun the script.
metro:
  width: 1910
  height: 960
  lines:
    - {"topic": "setup", "title": "Setup & Recovery", "color": "#4a4a48", "d": "M130,70 H1170"}
    - {"topic": "modify-app", "title": "Software: Modify an app", "color": "#5aa89a", "d": "M650,70 V110 L695,155 H1170"}
    - {"topic": "write-app", "title": "Software: Write your own app", "color": "#2f7f73", "d": "M399,70 V280 L444,325 H1690"}
    - {"topic": "gpio", "title": "Hardware: GPIO", "color": "#c4622d", "d": "M269,70 V705 L314,750 H1040"}
    - {"topic": "i2c", "title": "Hardware: I2C", "color": "#8f4a1f", "d": "M390,70 V620 L435,665 H1170"}
    - {"topic": "display", "title": "Hardware: Display (e-ink + LVGL)", "color": "#c9902f", "d": "M668,325 V365 L713,410 H1820"}
    - {"topic": "wifi", "title": "Hardware: WiFi", "color": "#3b5b92", "d": "M260,70 V790 L305,835 H780"}
    - {"topic": "espnow", "title": "Hardware: ESP-NOW", "color": "#7a5ea8", "d": "M390,835 V875 L435,920 H910"}
    - {"topic": "crashes", "title": "Debugging: When it crashes", "color": "#046307", "d": "M780,155 V195 L825,240 H1040"}
    - {"topic": "watch", "title": "Debugging: Watch it run", "color": "#5e9b45", "d": "M659,325 V450 L704,495 H1040"}
    - {"topic": "advanced", "title": "Debugging: Advanced tactics", "color": "#a8326e", "d": "M650,325 V535 L695,580 H1430"}
  stations:
    - {"id": "use-badge", "topic": "setup", "x": 130, "y": 70, "label": ["Use your badge"], "workshop": true, "start": true}
    - {"id": "repl", "topic": "setup", "x": 260, "y": 70, "label": ["Connect to the", "REPL"], "workshop": true}
    - {"id": "map-firmware", "topic": "setup", "x": 390, "y": 70, "label": ["Find the files"], "workshop": true}
    - {"id": "explore-badge", "topic": "setup", "x": 520, "y": 70, "label": ["Explore the", "badge object"]}
    - {"id": "backup", "topic": "setup", "x": 650, "y": 70, "label": ["Back up your", "badge"], "workshop": true}
    - {"id": "update-firmware", "topic": "setup", "x": 780, "y": 70, "label": ["Update the", "firmware"], "workshop": true}
    - {"id": "mount-and-run", "topic": "setup", "x": 910, "y": 70, "label": ["Work from your", "laptop"]}
    - {"id": "start-fresh", "topic": "setup", "x": 1040, "y": 70, "label": ["Start fresh"]}
    - {"id": "recover", "topic": "setup", "x": 1170, "y": 70, "label": ["Boot rescue"], "also": ["resets"]}
    - {"id": "name-badge", "topic": "modify-app", "x": 780, "y": 155, "label": ["Edit the base", "app"], "workshop": true}
    - {"id": "badge-diff", "topic": "modify-app", "x": 910, "y": 155, "label": ["What did I", "change?"]}
    - {"id": "sensor-badge", "topic": "modify-app", "x": 1040, "y": 155, "label": ["Your sensor on", "your badge"], "also": ["use-a-library"], "workshop": true}
    - {"id": "share-apps", "topic": "modify-app", "x": 1170, "y": 155, "label": ["Share and", "install apps"], "also": ["update-firmware"], "workshop": true}
    - {"id": "firmware-diagram", "topic": "write-app", "x": 520, "y": 325, "label": ["How apps run"]}
    - {"id": "first-app", "topic": "write-app", "x": 650, "y": 325, "label": ["Your first app"]}
    - {"id": "asyncio-basics", "topic": "write-app", "x": 780, "y": 325, "label": ["Take turns with", "asyncio"]}
    - {"id": "hog-the-cpu", "topic": "write-app", "x": 910, "y": 325, "label": ["Preventing", "freezes"], "also": ["break-and-restore"]}
    - {"id": "fsm", "topic": "write-app", "x": 1040, "y": 325, "label": ["Break work into", "states"]}
    - {"id": "on-time", "topic": "write-app", "x": 1170, "y": 325, "label": ["Doing things on", "time"]}
    - {"id": "pass-data", "topic": "write-app", "x": 1300, "y": 325, "label": ["Passing data", "between tasks"]}
    - {"id": "share-hardware", "topic": "write-app", "x": 1430, "y": 325, "label": ["Share the LEDs"], "also": ["all-leds"]}
    - {"id": "save-settings", "topic": "write-app", "x": 1560, "y": 325, "label": ["Save across", "reboots"]}
    - {"id": "out-of-memory", "topic": "write-app", "x": 1690, "y": 325, "label": ["Running out of", "memory"]}
    - {"id": "one-led", "topic": "gpio", "x": 390, "y": 750, "label": ["Light one LED"], "workshop": true}
    - {"id": "read-button", "topic": "gpio", "x": 520, "y": 750, "label": ["Read a button"], "workshop": true}
    - {"id": "all-leds", "topic": "gpio", "x": 650, "y": 750, "label": ["Light all the", "LEDs"]}
    - {"id": "animate-leds", "topic": "gpio", "x": 780, "y": 750, "label": ["Animate without", "blocking"], "also": ["on-time"]}
    - {"id": "interrupts", "topic": "gpio", "x": 910, "y": 750, "label": ["Polling vs.", "interrupts"], "also": ["asyncio-basics"]}
    - {"id": "sao-blink", "topic": "gpio", "x": 1040, "y": 750, "label": ["Blink on the SAO"], "also": ["sao-pinout"]}
    - {"id": "sao-pinout", "topic": "i2c", "x": 520, "y": 665, "label": ["SAO pinout, and", "connect your", "sensor"], "workshop": true}
    - {"id": "i2c-scan", "topic": "i2c", "x": 650, "y": 665, "label": ["Scan for I2C", "devices"], "workshop": true}
    - {"id": "add-a-library", "topic": "i2c", "x": 780, "y": 665, "label": ["Add a library"], "workshop": true}
    - {"id": "use-a-library", "topic": "i2c", "x": 910, "y": 665, "label": ["Use a library"], "workshop": true}
    - {"id": "read-register", "topic": "i2c", "x": 1040, "y": 665, "label": ["Read a register"]}
    - {"id": "real-units", "topic": "i2c", "x": 1170, "y": 665, "label": ["Raw bytes to", "real units"]}
    - {"id": "draw-pixels", "topic": "display", "x": 780, "y": 410, "label": ["Draw pixels,", "shapes and", "charts"]}
    - {"id": "lvgl-hello", "topic": "display", "x": 910, "y": 410, "label": ["Hello, LVGL"]}
    - {"id": "app-screen", "topic": "display", "x": 1040, "y": 410, "label": ["Layout and fonts"]}
    - {"id": "eink-images", "topic": "display", "x": 1170, "y": 410, "label": ["Images on a", "3-color panel"]}
    - {"id": "use-red", "topic": "display", "x": 1300, "y": 410, "label": ["Use red on", "purpose"]}
    - {"id": "eink-refresh", "topic": "display", "x": 1430, "y": 410, "label": ["Why e-ink is", "slow"]}
    - {"id": "eink-updates", "topic": "display", "x": 1560, "y": 410, "label": ["Update the", "screen well"], "also": ["on-time"]}
    - {"id": "qr-code", "topic": "display", "x": 1690, "y": 410, "label": ["Show a QR code"]}
    - {"id": "sleep-with-image", "topic": "display", "x": 1820, "y": 410, "label": ["Sleep with your", "image showing"]}
    - {"id": "wifi-join", "topic": "wifi", "x": 390, "y": 835, "label": ["Join WiFi"]}
    - {"id": "web-data", "topic": "wifi", "x": 520, "y": 835, "label": ["Fetch data from", "the web"]}
    - {"id": "fetch-without-freezing", "topic": "wifi", "x": 650, "y": 835, "label": ["Fetch without", "freezing"], "also": ["asyncio-basics"]}
    - {"id": "ntp-time", "topic": "wifi", "x": 780, "y": 835, "label": ["Set the clock"]}
    - {"id": "espnow-hello", "topic": "espnow", "x": 520, "y": 920, "label": ["Badge-to-badge", "hello"]}
    - {"id": "espnow-in-app", "topic": "espnow", "x": 650, "y": 920, "label": ["Messages in your", "app"], "also": ["pass-data"]}
    - {"id": "espnow-messages", "topic": "espnow", "x": 780, "y": 920, "label": ["Design a message"]}
    - {"id": "espnow-nearby", "topic": "espnow", "x": 910, "y": 920, "label": ["Who's nearby?"]}
    - {"id": "break-and-restore", "topic": "crashes", "x": 910, "y": 240, "label": ["Read a traceback"]}
    - {"id": "post-mortem", "topic": "crashes", "x": 1040, "y": 240, "label": ["Inspect a crash"], "also": ["firmware-diagram"]}
    - {"id": "better-prints", "topic": "watch", "x": 780, "y": 495, "label": ["Print and log"]}
    - {"id": "log-and-plot", "topic": "watch", "x": 910, "y": 495, "label": ["Plot it"]}
    - {"id": "log-unplugged", "topic": "watch", "x": 1040, "y": 495, "label": ["Logs without a", "laptop"]}
    - {"id": "resets", "topic": "advanced", "x": 780, "y": 580, "label": ["Resets and", "start-up"]}
    - {"id": "drive-app", "topic": "advanced", "x": 910, "y": 580, "label": ["Drive your app", "by hand"]}
    - {"id": "drive-badge", "topic": "advanced", "x": 1040, "y": 580, "label": ["Drive the whole", "badge"], "also": ["asyncio-basics"]}
    - {"id": "simulator", "topic": "advanced", "x": 1170, "y": 580, "label": ["Run it in the", "simulator"]}
    - {"id": "unit-tests", "topic": "advanced", "x": 1300, "y": 580, "label": ["Test your app"]}
    - {"id": "ai-loop", "topic": "advanced", "x": 1430, "y": 580, "label": ["Let an AI run", "the tests"]}
# ── end of metro layout ──
---
Made for the *Badge Hacking for Beginners* workshop at Hackaday Supercon 2026, but
open to everyone. Each line is a topic; ride it in order, or hop off wherever you
like. Tick off a station with its circle (saved in this browser only). Stations
with a red ring are the ones the workshop covers.
