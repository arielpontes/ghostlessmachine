---
name: hugo
description: Hugo static-site lessons for the ghostlessmachine WordPress→Hugo migration. Covers Stack theme quirks (featured images as page bundles, sidebar avatar, custom SCSS overrides), multilingual content, cache busting, and WordPress export gotchas. Load when working with Hugo content, theme, config, or migration scripts in this repo.
---

# Hugo Skills

## Stack Theme

This project uses the [hugo-theme-stack](https://github.com/CaiJimmy/hugo-theme-stack).

### Featured Images

**Important:** The Stack theme requires featured images to be **page resources**
(files in the same directory as the post), NOT static files in `/static/`.

```
content/post/my-post/
├── index.md          # Post content
└── featured.jpg      # Featured image (same directory)
```

In frontmatter, reference just the filename:

```yaml
---
title: "My Post"
image: "featured.jpg"
---
```

Images in `/static/uploads/` will NOT work as featured images - the theme's
`helper/image` partial uses `.Resources.Get` which only finds page bundle
resources.

### Sidebar Avatar

Configure in `config/_default/params.toml`:

```toml
[sidebar]
    avatar = "img/avatar.jpg"
```

Place the image in `assets/img/avatar.jpg`.

## Custom CSS

### How to Override Theme Styles

1. Copy `themes/hugo-theme-stack/assets/scss/style.scss` to `assets/scss/style.scss`
2. Create `assets/scss/custom.scss` with your overrides
3. The theme imports `custom.scss` at the end of `style.scss`

**Important:** Hugo won't pick up `custom.scss` overrides unless `style.scss`
is also in the project's `assets/scss/` folder.

### CSS Variable Overrides

Theme variables are often scoped to specific selectors, not `:root`. Check
the theme's SCSS to find the correct selector.

**Wrong** (won't work):

```scss
:root {
    --sidebar-avatar-size: 200px;
}
```

**Correct** (matches theme's scope):

```scss
.sidebar {
    --sidebar-avatar-size: 200px !important;
}
```

### Featured Image Aspect Ratio

Default theme uses fixed height (`--article-image-height`). To use 16:9:

```scss
// assets/scss/custom.scss
.article-list article .article-image img {
    height: auto;
    aspect-ratio: 16 / 9;
}
```

## Local Dev URLs

The site's `baseURL` is `https://arielpontes.github.io/ghostlessmachine/`
(GitHub Pages project-site form: `https://<username>.github.io/<repo-name>/`).
`hugo server` preserves the `/ghostlessmachine/` path prefix.

**Always include the prefix when giving local dev URLs**, e.g.:

- A page → `http://localhost:1313/ghostlessmachine/about/`
- A post → `http://localhost:1313/ghostlessmachine/p/<slug>/`
- A PT post → `http://localhost:1313/ghostlessmachine/pt/p/<slug>/`

Bare `/about/` will 404. If you ever migrate to a custom domain at the
apex (e.g. `https://ghostlessmachine.com/`), update `baseURL` and the
prefix goes away.

## Hugo Cache

When SCSS changes aren't applying, clear Hugo's cache:

```bash
rm -rf resources public && hugo --gc
```

## Multilingual Content

For Stack theme with multiple languages (e.g., English + Portuguese):

- Default language: `content/post/my-post/index.md`
- Other languages: `content/post/my-post/index.pt.md`

Configure in `config/_default/languages.toml`:

```toml
[en]
    languageName = "English"
    weight = 1

[pt]
    languageName = "Português"
    weight = 2
```

## WordPress Migration

### Export Process

1. WordPress XML export contains metadata only, NOT actual media files
2. Download media separately via hosting file manager or FTP
3. Featured images in WordPress are stored as `_thumbnail_id` postmeta
   referencing an attachment ID

### Image URL Conversion

After migration, update image URLs in markdown files:

```bash
find content -name "*.md" -exec sed -i '' \
  's|https://example.com/wp-content/uploads/|/uploads/|g' {} \;
```

### Featured Images for Stack Theme

WordPress featured images need to be copied into each post's directory
since Stack theme requires page bundle resources. See the
`scripts/fix_featured_images.py` script.
