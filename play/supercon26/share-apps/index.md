---
id: share-apps
title: Install someone else's app, and share yours
label: Share and install apps
topic: modify-app
workshop: true
needs: [update-firmware]
time: 20 min
touches: [main.py, apps/userB.py]   # TODO: facts.firmware.app_list, facts.firmware.user_app_2
verified_against: null
video: null
---

{% include facts.html %}

<!-- TODO(verify): how apps are registered (2025: main.py imports each one and adds it to a menu list) -->

**Goal:** Put an app someone else wrote on your badge's menu, and package one of yours
so someone else can do the same.

## You need

- Your badge, on the latest firmware (see [[update-firmware]]), and a fresh [[backup]]
- An app to install: a neighbor's, or one from the workshop. It's a single `.py` file
  with a class called `App` in it.

## Steps

### Install an app

1. **Read it first.** Open the file on your laptop and skim it. It's code that will run
   on your badge, so check the top for a comment that says what it does and what it
   needs (a sensor? WiFi? a library in `{{ facts.firmware.lib_dir }}/`?).

2. **The quick way: use a spare slot.** The badge has empty app slots meant for you
   ({{ facts.firmware.user_apps }}). They're already on the menu. Pick one you aren't
   using, say `{{ facts.firmware.user_app_2 }}`, back it up, and upload the new app
   over it: in Thonny's top pane, right-click the file → **Upload to …**, then rename it
   on the badge to match the slot (right-click → **Rename**).

3. Press **Ctrl+D** and open the slot from the menu. The app runs under the slot's name.

4. **The proper way: give it its own name.** Upload the file to `apps/` with its own
   name, say `apps/weather.py`. Then open `{{ facts.firmware.app_list }}` and find where
   the user apps are set up. Copy the lines for one of them and change the names:

   ```python
   from apps import weather
   # ...next to the other apps
   weather_app = weather.App("Weather", badge)
   ```

   Then add `weather_app` wherever the others are added to the menu.

   <!-- TODO(verify): the exact lines in this year's main.py; is there a registry file instead? -->

5. Save, **Ctrl+D**, and find **Weather** on the menu.

### Share yours

6. **Make it one file.** Everything your app needs should be in its `.py` file, or
   in a library that's easy to find. Put a short comment at the very top:

   ```python
   """Weather: shows the temperature in Pasadena.

   Needs: WiFi (set your network in the first lines below).
   Buttons: {{ facts.buttons.app_1_label }} refreshes, {{ facts.buttons.home_label }} goes home.
   Install: copy to apps/ and add it to main.py (or drop it into a spare user slot).
   By: you, Supercon 2026.
   """
   ```

7. **Hand it over.** Pick one:
   - **AirDrop, chat or a USB stick:** just send the file.
   - **A gist or repo:** paste it into a [GitHub gist](https://gist.github.com), or
     put it in a repo with a `README.md` that says the same as your comment, plus a photo.
   - **A pull request** to the badge's repo, if it accepts community apps. Read its
     README first to see where apps go. <!-- TODO: link the badge repo's contributing notes, if any -->

**✅ Done when** you've run someone else's app on your badge, and someone else has your
app's file and knows how to install it.

## What just happened

An app is just a file with an `App` class that the firmware knows how to drive (see
[[first-app]]). The menu is built in `{{ facts.firmware.app_list }}`: it imports each app,
creates it, and adds it to a list. Installing an app is "copy the file, then add it
to that list."

The user slots save you the second step: the firmware already imports and lists them.
The catch is that only a few exist, and they show the slot's name, not the app's.

Installing an app makes `{{ facts.firmware.app_list }}` one of *your* files too. When you
update the firmware, that's a conflict you'll have to redo by hand (see
[[update-firmware]]). Keeping your change to two lines makes that easy.

## Stuck?

| Symptom | Fix |
|---|---|
| `ImportError` at boot | The file's name doesn't match the `import` line, or it needs a library you don't have. |
| `AttributeError: ... has no attribute 'App'` | The file's class has a different name. Keep it `App`. |
| Badge won't boot after editing `main.py` | Read the traceback (see [[break-and-restore]]); still stuck, see [[recover]]. |
| The app runs but does nothing | Read its top comment: does it need WiFi, a sensor or a library? |

## Prefer the command line?

```bash
mpremote cp weather.py :apps/weather.py
mpremote edit :main.py
mpremote soft-reset
```

## Have fun!

- Swap apps with three neighbors. Which one would you keep?
- Start a shared folder for your table: everyone's apps, one README listing them.
