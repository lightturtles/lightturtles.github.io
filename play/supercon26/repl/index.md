---
id: repl
title: Connect over USB-C; reach the REPL; run one line
label: Connect to the REPL
topic: setup
workshop: true
needs: []
time: 10 min
touches: []                     # firmware files this page depends on
verified_against: null          # firmware commit last checked on a real badge
video: null
---

{% include facts.html %}

**Goal:** Type Python into your laptop and have it run on the badge.

## You need

- Your badge
- A USB-C cable **that carries data** (many cables only charge, and those won't work)
- One of: [Thonny](https://thonny.org) (an app you install) or
  [ViperIDE](https://viper-ide.org) (runs in Chrome or Edge; no install)

## Steps

1. Plug the badge into your laptop.

2. Connect:

   **Thonny**
   1. **Run → Configure interpreter…**
   2. Interpreter: **{{ facts.thonny.interpreter }}**. Port: pick the badge,
      or **< Try to detect port automatically >**.
   3. Click **OK**.

   <!-- TODO(screenshot): Thonny "Configure interpreter" dialog with the right entries selected -->

   **ViperIDE**
   1. Open <https://viper-ide.org> in Chrome or Edge. Firefox and Safari can't reach USB devices.
   2. Click the connect icon and choose **USB/Serial**, then pick the badge in the pop-up.

   <!-- TODO(screenshot): ViperIDE connect menu + browser's serial-port picker -->

3. Find the `>>>` prompt in the bottom pane (Thonny's **Shell**, ViperIDE's terminal).
   No prompt? Click in that pane and press **Ctrl+C**.

4. Type this and press **Enter**:

   ```python
   print("Hello, Supercon!")
   ```

5. Now this one, which reports the firmware version:

   ```python
   import os; os.uname()
   ```

   You should see `sysname='esp32'`. An error means you're talking to your
   laptop's Python, not the badge (see *Stuck?*). Write down the `version=`
   part. It's the first thing anyone will ask if you need help.

<!-- TODO(screenshot): Shell pane showing both commands and their output -->

**✅ Done when** the badge prints `Hello, Supercon!` back to you.

## What just happened

The badge's chip ({{ facts.badge.mcu }}) runs **MicroPython**, a small Python
interpreter. The `>>>` prompt is its **REPL** (Read, Evaluate, Print, Loop). Your
laptop is just a keyboard and screen for it, and the code runs *on the badge*.

Pressing **Ctrl+C** stopped the badge's own program, so the screen and buttons may
freeze. Press **Ctrl+D** at an empty `>>>` to soft-reset and get the menu back.

<!-- TODO(diagram): laptop ⇄ USB cable ⇄ badge chip running MicroPython; keystrokes go in, printed text comes out -->

## Stuck?

| Symptom | Fix |
|---|---|
| No port shows up | Try a different cable (the usual culprit), then a different USB port. Plug straight into the laptop, not a hub or dock. |
| Several ports; which is the badge? | Unplug the badge, check the list, plug it back in. The badge is the one that appears. |
| Port keeps appearing and disappearing | The badge is crashing and restarting. See [[recover]]. |
| `os.uname()` gives an error | Thonny is using your laptop's Python. Redo step 2 and pick **{{ facts.thonny.interpreter }}**. |
| "Port busy" / "could not open" | Only one program can use the badge at a time. Close the other app or browser tab (Arduino IDE and 3D-printer software are common culprits). |
| Connected, but no `>>>` | Click in the shell pane and press **Ctrl+C**, then **Enter**. |
| Thonny: "Device is busy or does not respond" | Click **Stop** (or press **Ctrl+F2**), then **Ctrl+C** in the shell. |
| Says `raw REPL; CTRL-B to exit`, or typing does nothing | Press **Ctrl+B**. |
| Work laptop won't allow it | IT policies often block USB devices. Pair up with a neighbor. |

Still stuck? See *Troubleshooting by OS* at the bottom of this page.

## Prefer the command line? Use `mpremote`

```bash
pipx install mpremote
mpremote          # finds the badge and opens the REPL
```

No `pipx`? `pip install mpremote` works too, unless it complains about an
"externally-managed-environment" (newer Ubuntu, Debian, Homebrew). If you get
"command not found" afterwards, run `python -m mpremote` instead.

Exit with **Ctrl+]**. You'll use `mpremote` again in [[backup]].

## Have fun!

It's like learning Python for the first time! Make an insult generator, or compute the first 50 numbers in the Fibonacci sequence.

## Troubleshooting by OS

### Linux

- **"Permission denied":** add yourself to the serial group, then log out
  and back in (sometimes a reboot is needed):
  `sudo usermod -aG dialout $USER` (Debian, Ubuntu, Fedora) or
  `sudo usermod -aG uucp $USER` (Arch). Check with `groups`.
- **Port busy for ~10 s after plugging in:** that's ModemManager probing the
  badge. Wait, or run `sudo systemctl stop ModemManager`.
- **ViperIDE can't see the badge in Ubuntu's Chromium:** the snap version is
  sandboxed. Run `sudo snap connect chromium:raw-usb`, or use Google Chrome.
  Snap/Flatpak versions of Thonny have similar trouble; the version from
  [thonny.org](https://thonny.org) doesn't.
  <!-- TODO: keep only if facts.usb.bridge is CH340 -->
- **Port appears, then vanishes (CH340 chips, Ubuntu 22.04+):** the Braille
  display service grabbed it. `sudo apt remove brltty`.

### macOS

- **Badge never shows up:** you may have dismissed the "Allow accessory to
  connect?" prompt. Go to **System Settings → Privacy & Security → Allow
  accessories to connect**.
- **Picking a port:** choose `/dev/cu.usbmodem…`, not `/dev/tty.…`.

### Windows

- **Which COM port?** Open **Device Manager → Ports (COM & LPT)**.
<!-- TODO: keep only if facts.usb.bridge is not native -->
- **Yellow triangle or "Unknown device":** install the
  {{ facts.usb.bridge }} driver.

### Browsers (ViperIDE)

- Works in Chrome and Edge. **Brave** has it switched off by default.
  **Firefox** and **Safari** can't do it at all; use Thonny instead.
