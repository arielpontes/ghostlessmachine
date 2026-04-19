# Ghostless Machine

A Hugo-powered static blog migrated from WordPress, using the
[hugo-theme-stack](https://github.com/CaiJimmy/hugo-theme-stack) theme.

## Requirements

- [Hugo](https://gohugo.io/) (extended version recommended)
- Python 3.14+ (for migration scripts only)

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

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Convert WordPress Export

```bash
python scripts/wp_to_hugo.py
```

Converts `wordpress-export.xml` to Hugo markdown files in `content/`.

### Fix Featured Images

```bash
python scripts/fix_featured_images.py
```

Copies featured images from `static/uploads/` into each post's directory
(required by the Stack theme's page bundle approach).

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
