---
id: use-badge
title: "Start here: the buttons, the menu, and the apps that came on your badge"
label: Use your badge
topic: setup
workshop: true
needs: []
time: 5 min
touches:                        # firmware files this page depends on
  - main.py#main                # start-up counter, splash, the 42nd start-up
  - lib/app_switcher.py#AppSwitcher.arun   # menu: which buttons do what
  - lib/led_bar.py#LedBar.menu_display     # menu colors on the LED bar
  - lib/button.py               # button names (and the swapped +/− labels)
  - apps/nametag.py
  - apps/gallery.py#GalleryApp.__init__   # maximage = 44, updatetime = 300 (s)
  - apps/schedule.py
  - data/user_apps.py           # menu order = the order dir() lists this module's names
verified_against: null          # firmware commit last checked on a real badge
video: null
---

{% include facts.html %}

**Goal:** Get around your badge without a laptop: pick an app, run it, and get back
to the menu.

## You need

- Your badge, switched on. It runs on its battery; plugging in USB-C powers it too.
  <!-- TODO(verify): battery type, and where the power switch is (facts.power) -->

<!-- TODO(screenshot): photo of the front of the badge with the five buttons, the LED bar and RESET labelled -->

## Steps

1. **Find the menu.** When the badge starts, it goes straight to its menu. The screen
   doesn't change: e-ink keeps showing its last picture even with the power off. The
   **row of {{ facts.leds.count }} LEDs** is the menu instead. One LED for each app,
   and the brighter, whiter one is the app that's selected.

   <!-- TODO(screenshot): LED bar in menu mode, one app selected -->

2. **Move through the menu** with the two **Menu** buttons.

   <!-- TODO(verify): the source says the + and − labels are swapped on the board. Confirm which way each one moves. -->
   The **+** and **−** labels on the board are the wrong way round, so if the
   selection goes the "wrong" way, that's not you.

3. **Start the selected app** with **User A** or **User B**. Your badge comes with these:

   | # | App | What it does |
   |---|---|---|
   | 1 | **Workshops** | The workshop schedule. |
   | 2 | **Sat Talks** | Saturday's talks on both stages. |
   | 3 | **Sun Talks** | Sunday's talks. |
   | 4 | **Gallery** | A random picture from the badge's art gallery, and a new one every 5 minutes. |
   | 5 | **{{ facts.name_badge.app }}** | A "HELLO I am" name tag… with nothing written in it yet. Filling it in is your first hack: [[name-badge]]. |

   Add or rename an app and this order can change. The badge doesn't sort its apps; it
   takes them in whatever order Python happens to list them.

   While an app draws, the LEDs go **cyan**. When they turn **green** the picture is
   done. An e-ink refresh takes a few seconds and the screen flashes while it does.
   That's normal.

   <!-- TODO(screenshot): Nametag on the screen; a schedule page -->

4. **Get back to the menu** with either **Menu** button. The app stops, and its picture
   stays on the screen until another app draws over it.

5. **Restart the badge** with **{{ facts.power.reset_button }}**. The badge starts up
   in the menu again.

**✅ Done when** you've run two different apps and come back to the menu in between.

## What just happened

The badge runs one program, `main.py`, from the moment it starts. It watches the buttons,
drives the LEDs and the screen, and runs **one app at a time**: the one you picked. While
the menu is showing, no app runs at all.

Each app is just a Python file in the badge's `apps/` folder. The badge finds them by
itself every time it starts, so adding your own app is mostly "put a file there"
([[share-apps]]). You'll meet `main.py` properly in [[map-firmware]] and [[firmware-diagram]].

Next: plug the badge into your laptop and talk to it in [[repl]].

<details markdown="1">
<summary><strong>Why does something odd happen on the 42nd start-up?</strong></summary>

Every time the badge starts, `main.py` adds one to a counter it keeps in
`{{ facts.config.file }}`. It uses the counter twice:

- On the **first** start-up it shows a splash screen.
- On the **42nd** it shows a special picture. 42 is the Answer to the Ultimate Question of
  Life, the Universe, and Everything, according to *The Hitchhiker's Guide to the Galaxy*.

Pressing **{{ facts.power.reset_button }}**, unplugging the badge and plugging it back in,
and pressing **Ctrl+D** at the REPL all count as start-ups. Don't want to wait for 42? Once you can reach the REPL,
you can change the counter yourself:

```python
import lib.json_configs as c
c.load()                              # see the current count
c.append(41, "load_counter")          # the next start-up is number 42
```

Then press **{{ facts.power.reset_button }}**.

<!-- TODO(verify) on a real badge before the workshop: main.py:46 loads
     /data/graphics/never-epd.png, but the file is never_epd.png. Boot 42 probably
     ends in a traceback (on the REPL) instead of a picture. If so, either say so here
     ("you just found a real bug — read the traceback") or get it fixed upstream. -->

</details>

## Stuck?

| Symptom | Fix |
|---|---|
| A button does nothing | **Wait!** If the LEDs are cyan, the badge is still drawing a picture and isn't watching the buttons. Press again once they turn green. |
| Nothing lights up | Check the power switch. Then try plugging in USB-C. |
| Pressing **User A** / **User B** does nothing | You're probably already in an app. Press a **Menu** button first. |
| Pressing **Menu** doesn't move the selection | The first press only brings the menu back. Press again to move. |
| Gallery starts but the picture doesn't change | Known bug: the app picks from 44 pictures, but your badge may not have all of them. Go back to the menu and start Gallery again. |
| Badge seems frozen | Give it a few seconds first (see the first row). Still stuck? Press **{{ facts.power.reset_button }}**. |

## Have fun!

- How many times have you started your badge? Guess now; you'll be able to check in [[map-firmware]].
- Which button does nothing in any of the stock apps? (Hint: there are five, plus **{{ facts.power.reset_button }}**.)
