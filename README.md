# LightTurtles — Jekyll Site

A static Jekyll site for [lightturtles.github.io](https://lightturtles.github.io),
migrated from WordPress. Custom theme with no external dependencies beyond two Google Font
families and the standard `jekyll-feed` / `jekyll-seo-tag` plugins.

---

## Quick Start (local preview)

You need Ruby and Bundler installed.

```bash
# Install dependencies
bundle install

# Serve locally with live reload
bundle exec jekyll serve --livereload

# Browse to http://localhost:4000
```

---

## File Layout

```
_config.yml          ← Site-wide settings (title, author info, social links)
index.html           ← Landing page (hero, about, services, contact)
works.html           ← Filterable works archive
_layouts/
  default.html       ← Nav + footer wrapper used by all pages
  post.html          ← Individual post layout (extends default)
assets/
  css/main.css       ← All styles (custom theme, no framework)
  js/main.js         ← Nav toggle
  js/filter.js       ← Works page filtering & sorting
  docs/              ← Put PDFs and other downloadable files here
_posts/              ← Your published works (articles, talks, videos, etc.)
```

---

## Writing a New Post

Create a file in `_posts/` named `YYYY-MM-DD-slug-here.md`.

### Minimal front matter

```yaml
---
layout: post
title: "Your Post Title"
date: 2024-09-01
type: article          # article | video | talk | tutorial
subjects:
  - firmware           # add as many as apply
  - security
excerpt: >
  One-sentence description shown in the works listing.
---
```

### With attached documents

```yaml
---
layout: post
title: "Post With Documents"
date: 2024-09-01
type: article
subjects:
  - firmware
excerpt: A post that includes downloadable files.
documents:
  - title: "Reference Code (ZIP)"
    url: /assets/docs/my-code.zip
    type: zip
  - title: "Design Notes (PDF)"
    url: /assets/docs/my-notes.pdf
    type: pdf
---
```

Put the actual files in `assets/docs/` and commit them alongside the post.

### Available `type` values

| Value      | Tag color   | Use for                          |
|------------|-------------|----------------------------------|
| `article`  | amber       | Written articles, blog posts     |
| `video`    | purple      | YouTube, Vimeo, recorded talks   |
| `talk`     | green       | Conference/meetup presentations  |
| `tutorial` | cyan        | Step-by-step how-tos             |

### Available `subjects` (suggested — add new ones as needed)

`firmware`, `architecture`, `hardware`, `fpga`, `digital-design`, `security`,
`education`, `rtos`, `tooling`, `writing`

Subject filter buttons on the Works page are generated automatically from the
subjects present in your posts — no configuration required.

---

## Linking to Works with Filters Pre-Applied

From anywhere on the site (e.g. a service card on the landing page):

```
/works.html?type=video
/works.html?subject=firmware
/works.html?type=article&subject=security
```

---

## Contact Form

The contact form uses [Formspree](https://formspree.io) (free tier handles up
to 50 submissions/month). To activate it:

1. Sign up at formspree.io
2. Create a new form pointed at your email
3. Copy the form ID (looks like `xabc1234`)
4. In `index.html`, replace `YOUR_FORM_ID` in the form action URL:
   ```
   action="https://formspree.io/f/YOUR_FORM_ID"
   ```

Until you do this, the form renders fine but submissions go nowhere.

---

## Customization Tips

- **Colors / fonts** — all CSS custom properties are at the top of
  `assets/css/main.css` in the `:root` block.
- **Nav links** — edit the `<nav>` section in `_layouts/default.html`.
- **Services** — the six service cards live directly in `index.html`.
- **Social links** — update `author.linkedin`, `author.github`, `author.tindie`
  in `_config.yml`.
- **Business hours / contact info** — also in `_config.yml`.

---

## Deploying to GitHub Pages

Push to the `main` (or `master`) branch of your
`lightturtles/lightturtles.github.io` repository. GitHub Pages
builds Jekyll automatically. No Actions workflow needed for a standard setup.

If you add plugins beyond `jekyll-feed` and `jekyll-seo-tag`, you may need a
GitHub Actions workflow since GitHub Pages only supports a subset of plugins
natively. The existing two plugins are on the supported list.
