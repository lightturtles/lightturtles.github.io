---
id: name-badge
title: Make it your name badge (in the app, then in code)
label: Your name badge
tier: core
difficulty: 4
group: editing
icon: id-card
needs: [backup]
time: 20 min
touches: [apps/nametag.py]     # TODO: facts.name_badge.file
verified_against: null
video: null
---

{% include facts.html %}

**Goal:** Put your name on the badge, then change one line of the firmware and see
your change on the screen.

## You need

- Your badge, connected (see [[repl]])
- A fresh [[backup]]. You're about to edit a file on the badge.

## Steps

1. **The easy way first.** On the badge, open **{{ facts.name_badge.app }}** from the menu
   and set your name. No laptop needed.

   <!-- TODO(verify): how this year's app sets the name (on-badge keyboard? config app?) -->

2. **Now the hacker's way.** In Thonny's **Files** view, double-click
   `{{ facts.name_badge.file }}` in the bottom (badge) pane. It opens in the editor, and
   the tab's title says `[ {{ facts.name_badge.file }} ]` with brackets: that means
   you're editing the copy *on the badge*.

3. Find the line with `{{ facts.name_badge.find }}` (**Ctrl+F**). It sets
   {{ facts.name_badge.what }}.

4. Change `{{ facts.name_badge.find }}` to `{{ facts.name_badge.replace }}`. Change
   nothing else.

5. Save with **Ctrl+S** (**Cmd+S**). That writes the file to the badge's flash.

6. Restart the badge's program: click in the shell and press **Ctrl+D** (or press
   **{{ facts.power.reset_button }}**). Open **{{ facts.name_badge.app }}** again.

   <!-- TODO(photo): name badge before and after the change -->

**✅ Done when** the badge shows your name with your change.

## What just happened

Saving in Thonny wrote a new copy of the file to the badge, but the old version was
still loaded in RAM. Python reads a file when it's **imported**, and the badge only
imports its apps once, at startup. So a change takes effect after a restart.

Your edit also changed what kind of file this is (see [[map-firmware]]):
`{{ facts.name_badge.file }}` used to match the folder, and now it's **yours**. Back it up.
When an update changes the same file, you'll have to choose between your version and
theirs (see [[update-firmware]]).

<!-- TODO(diagram): editor → Ctrl+S → flash (file) → Ctrl+D → import → RAM (running app) -->

## Stuck?

| Symptom | Fix |
|---|---|
| Nothing changed | Did you save (no `*` on the tab)? Did you restart (**Ctrl+D**)? |
| The tab title has no brackets | You opened the laptop's copy. Open the file from the bottom (badge) pane. |
| Badge shows an error, or a blank screen | Perfect timing: that's the next skill, [[break-and-restore]]. |
| Can't find the line | The firmware may have changed. Search for `font` or your name instead, or ask a helper. |

## Prefer the command line?

```bash
mpremote edit :{{ facts.name_badge.file }}    # opens it in $EDITOR, saves back to the badge
mpremote reset
```

Don't edit the files in the official folder itself. It's your reference for what
"unchanged" looks like.

## Have fun!

- Change a color, a word on the screen, or the image it shows.
- Make the change and its opposite a few times. How long does each round trip take?
  [[mount-and-run]] makes it shorter.
