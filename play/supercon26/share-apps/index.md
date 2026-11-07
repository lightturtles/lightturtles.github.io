---
id: share-apps
title: Install someone else's app, and share yours
label: Share and install apps
topic: modify-app
workshop: true
needs: [update-firmware]
time: 15 min
touches:
  - lib/app_switcher.py#AppSwitcher.__init__   # finds apps/*.py; skips _*, base_app, template; builds every BaseApp subclass
  - apps/base_app.py            # what makes a class an app
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Put an app someone else wrote on your badge's menu, and package one of yours
so someone else can do the same.

## You need

- Your badge, on the latest firmware (see [[update-firmware]]), and a fresh [[backup]]
- An app to install: a neighbor's, or one from the workshop. It's a single `.py` file.
  <!-- TODO: a workshop example app to install, if neighbors don't have one yet -->

## Steps

### Install an app

Installing an app is the same move as [[add-a-library]], into a different folder:
`apps/` instead of `{{ facts.firmware.lib_dir }}/`.

1. **Read it first.** Open the file on your laptop and skim it. It's code that will run
   on your badge, so check the top for a comment that says what it does and what it
   needs (a sensor? WiFi? a library in `{{ facts.firmware.lib_dir }}/`?). Look for
   `self.name = "…"` too: that's what the menu will call it.

2. **Copy it into `apps/`**, the same way you copied your library into
   `{{ facts.firmware.lib_dir }}/`. Give the file a name of its own, all lower-case, and
   not one that's already there (uploading over `nametag.py` would replace your name badge).

3. **Restart:** click in the shell and press **Ctrl+D**. Watch the shell as the badge starts:

   ```
   Found app mods: ['gallery', 'nametag', 'schedule', 'template', 'weather']
   ...
   Added app: Weather
   ```

4. **Find it on the menu** (see [[use-badge]]) and start it. The menu order may have
   changed: the badge doesn't sort its apps.

### Share yours

5. **Give it its own name.** Sharing the name badge you made in [[sensor-badge]]? It's
   still called `nametag.py` and "Nametag", so on someone else's badge it would replace
   theirs. Save a copy under a new file name (say `ada_badge.py`), and change
   `self.name = "Nametag"` in it to something new.

6. **Make it one file.** Everything your app needs should be in its `.py` file, or
   in a library that's easy to find. Put a short comment at the very top:

   ```python
   """Weather: shows the temperature in Pasadena.

   Needs: WiFi (set your network in the first lines below).
   Buttons: {{ facts.buttons.app_1_label }} refreshes.
   Install: copy to apps/ and restart the badge.
   By: you, Supercon 2026.
   """
   ```

7. **Hand it over.** Pick one:
   - **AirDrop, chat or a USB stick:** just send the file.
   - **A gist or repo:** paste it into a [GitHub gist](https://gist.github.com), or
     put it in a repo with a `README.md` that says the same as your comment, plus a photo.
   - **A pull request to the badge's repo.** Its README invites them: "If you come up with
     additional apps that you'd like to share, feel free to make a pull request." Apps
     go in `{{ facts.firmware.folder }}/apps/`.

**✅ Done when** you've run someone else's app on your badge, and someone else has your
app's file and knows how to install it.

## What just happened

Every time the badge starts, it looks in `apps/` for `.py` files, imports each one, and
makes one of every app class it finds (every class built on `BaseApp`). The menu is
just that list. So installing an app is only "put the file there", and removing one is
"delete the file".

Three files are skipped on purpose: `base_app.py` (the thing apps are built on),
`template.py` (a starting point for your own, see [[first-app]]), and anything starting
with `_`. Rename an app to `_weather.py` to hide it without deleting it.

The new app is one of *your* files (see [[map-firmware]]): it's not in the official
folder, so back it up. Updates won't touch it.

## Stuck?

| Symptom | Fix |
|---|---|
| The badge stops at `>>>` after **Ctrl+D** | The new file has a typo the badge can't read (`SyntaxError`). One bad app file stops *every* app. Read the traceback (see [[break-and-restore]]), then fix or delete the file. |
| The shell says `Failed to load app module` | The app crashed while it was being set up (in its `__init__`). The others still work. The traceback below it says why. |
| It's not on the menu, and no error | Its file name starts with `_`, or is `template.py`, or it has no `BaseApp` class. |
| `ImportError` for a library | It needs a library you don't have. Install it in `/{{ facts.firmware.lib_dir }}` (see [[add-a-library]]). |
| The app starts but does nothing | Read its top comment: does it need WiFi, a sensor or a library? |
| Two apps with the same name on the menu | Both set the same `self.name`. Change one. |

## Prefer the command line?

```bash
mpremote cp weather.py :apps/weather.py
mpremote soft-reset
```

## Have fun!

- Swap apps with three neighbors. Which one would you keep?
- Start a shared folder for your table: everyone's apps, one README listing them.
- Hide an app you never use: rename it so it starts with `_`.
