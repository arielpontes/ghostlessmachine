# Ghostless Machine

A Hugo-powered static blog migrated from WordPress, using the
[hugo-theme-stack](https://github.com/CaiJimmy/hugo-theme-stack) theme.

## Requirements

- [Hugo](https://gohugo.io/) (extended version recommended)
- [uv](https://docs.astral.sh/uv/) (for migration scripts only; manages
  Python 3.14+ and dependencies via `pyproject.toml`/`uv.lock`)

## Local Development

```bash
# Start the development server
hugo server -D

# Build the site
hugo --minify
```

The site will be available at `http://localhost:1313/`.

## Project Structure

```text
.
├── assets/
│   ├── img/avatar.jpg          # Sidebar avatar
│   └── scss/
│       ├── style.scss          # Copied from theme to enable custom.scss
│       └── custom.scss         # CSS overrides
├── config/_default/
│   ├── hugo.toml               # Main Hugo config
│   ├── languages.toml          # Multilingual settings (en, pt)
│   ├── markup.toml             # Markdown rendering config
│   └── params.toml             # Theme parameters
├── content/
│   ├── page/                   # Static pages
│   └── post/                   # Blog posts (page bundles)
├── scripts/                    # Migration scripts
├── static/uploads/             # Media files from WordPress
└── themes/hugo-theme-stack/    # Theme (git submodule)
```

## Multilingual Content

The site supports English and Portuguese:

- Default (English): `content/post/my-post/index.md`
- Portuguese: `content/post/my-post/index.pt.md`

## Migration Scripts

Scripts used to migrate from WordPress. Only needed once.

Dependencies are managed with [uv](https://docs.astral.sh/uv/): running any
script with `uv run` automatically creates the virtualenv and installs the
locked dependencies from `uv.lock`.

### Convert WordPress Export

```bash
uv run scripts/wp_to_hugo.py
```

Converts `wordpress-export.xml` to Hugo markdown files in `content/`.

### Fix Featured Images

```bash
uv run scripts/fix_featured_images.py
```

Copies featured images from `static/uploads/` into each post's directory
(required by the Stack theme's page bundle approach).

## TODO

Pages migrated from WordPress that need review (decide whether to keep,
delete, or repurpose):

- `content/page/14d9b-about-me/` — looks like an old/duplicate About page
- `content/page/14d9b-contact/` — looks like an old/duplicate Contact page
- `content/page/home/` — legacy WordPress home page (en)
- `content/page/home-pt/` — legacy WordPress home page (pt)
- `content/page/anniversaries/` — purpose unclear
- `content/page/mailing-list/` — contains only `[newsletter]` shortcode
- `content/page/rocitizen-app-privacy-policy/` — privacy policy for an app

## Deployment

The site is deployed to GitHub Pages via GitHub Actions. Push to `master` to
trigger a build.

## Customization

### Featured Image Aspect Ratio

The theme's default featured image height is overridden to use 16:9 aspect
ratio. See `assets/scss/custom.scss`.

### Sidebar Avatar

Configure in `config/_default/params.toml`:

```toml
[sidebar]
    avatar = "img/avatar.jpg"
```

Place the image in `assets/img/`.

### Comments

Disqus is configured in `config/_default/params.toml`. Set the shortname to
enable comments.
