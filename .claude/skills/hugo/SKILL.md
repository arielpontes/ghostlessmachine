---
name: hugo
description: Hugo static-site lessons for the ghostlessmachine WordPress→Hugo migration. Covers Stack theme quirks (featured images as page bundles, sidebar avatar, custom SCSS overrides), multilingual content, cache busting, GitHub Pages deploys (CI Hugo version, Pages enablement), and WordPress export gotchas. Load when working with Hugo content, theme, config, deploy workflow, or migration scripts in this repo.
---

# Hugo Skills

## Stack Theme

This project uses the [hugo-theme-stack](https://github.com/CaiJimmy/hugo-theme-stack).

### Featured Images

**Important:** The Stack theme requires featured images to be **page resources**
(files in the same directory as the post), NOT static files in `/static/`.

```text
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

### Hiding Categories Site-Wide (July 2026)

Categories are hidden everywhere but kept in post front matter. The main
switch is disabling the taxonomy in `config/_default/hugo.toml`:

```toml
[taxonomies]
    tag = "tags"
```

With `categories` unregistered, Hugo generates no `/categories/` term
pages, and `GetTerms "categories"` returns empty — which auto-hides the
category grid on the archives page and all category links. Two companion
edits: the `categories` widget is commented out in `params.toml`, and the
badge guard in `layouts/_partials/article/components/details.html` uses
`GetTerms "categories"` instead of `.Params.categories` (the front-matter
check would render an empty `<header class="article-category">` while the
taxonomy is off).

To restore categories: add `category = "categories"` to `[taxonomies]`
and uncomment the widget line.

### Homepage Intro Card (July 2026)

The bio blurb above the homepage post grid lives in `content/_index.md`
and `content/_index.pt.md` (both carry `title: Ghostless Machine` so the
`<title>` tag and markdownlint's MD041 stay happy). The theme's
`home.html` ignores homepage content, so the site overrides
`layouts/home.html` to render `.Content` above the list — only when
`$paginator.HasPrev` is false, so `/page/2/` and beyond skip it.

Styling is `.homepage-intro` in `assets/scss/custom.scss`: the
`machine-bw.jpg` background (in `static/img/`, referenced from compiled
CSS as `url(../img/...)` relative to `/scss/`), fixed white text, and a
black overlay whose alpha is the one knob for image darkness:

```scss
--intro-overlay: rgba(0, 0, 0, 0.55);
```

Links are forced white/underlined because the theme's accent color
(light mode) and grey hover highlight are illegible on the dark image.

### Homepage Tabs — Articles / Podcasts (July 2026)

The homepage and `/podcasts/` are two separate templates styled as tabs.
Podcast posts carry `tags: ["Podcast"]`; the homepage excludes them, the
podcasts page (`content/page/podcasts/` + `layouts/podcasts.html`) lists
only them (from `site.Sites.Default` so the PT page shows the EN-only
episodes).

**Custom layouts silently drop baseof blocks and shared furniture.** This
caused two bugs in a row: `podcasts.html`, written from scratch, first
lost the right sidebar (Stack's `baseof.html` renders
`block "right-sidebar"` only if the layout defines it), then lost the
homepage hero when it was later added only to `home.html`. Rules:

- When adding a page meant to look like a sibling of an existing page,
  **copy that page's template and edit it** — never write it from scratch.
- Anything that must appear identically on sibling pages (hero, tab bar)
  lives in one shared partial (`_partials/home-tabs.html`, which takes
  `Active` and `ShowHero`), not duplicated per layout.

**`.Paginate` is first-call-wins.** The theme's `data/title.html`
paginates from inside `<head>`, before `main` renders, so filtering the
page list inside `home.html` has no effect. The podcast filter therefore
lives in the site override of `_partials/helper/paginator.html`
(homepage only, so archives/tags/search still include podcasts).

**Project `i18n/pt.toml` is shadowed** by the theme's `pt-br`/`pt-pt`
bundles for this site's bare `pt` language — `T` falls back to English.
The tab labels are inlined in the partial with a
`site.Language.Lang` check instead.

Two debugging gotchas from the same session: recent Hugo **strips HTML
comments from templates** (debug with a `<span hidden>` instead), and a
**running `hugo server` doesn't pick up a new file that shadows a theme
partial** — restart the server after creating one.

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

### Resources in Non-Default-Language Bundles

In a bundle that has no default-language page (e.g. `page/sobre/` with
only `index.pt.md`), a resource without a language suffix
(`me-2021.jpg`) attaches to the missing EN page and the PT page can't
see it — the theme's image hook then emits an `<img>` with no `src`.
Fix: add the language code to the resource filename
(`me-2021.pt.jpg`). Markdown keeps referencing the bare name
(`![...](me-2021.jpg)`); Hugo strips the code when naming the
resource.

## GitHub Pages Deployment

### Pages Must Be Enabled First

The deploy workflow (`.github/workflows/hugo.yml`) fails at the
"Setup Pages" step with `Get Pages site failed ... Not Found` if GitHub
Pages was never enabled on the repository. Enable it with the
"GitHub Actions" source (one-time setup):

```bash
gh api repos/<owner>/<repo>/pages -X POST -f build_type=workflow
```

### Keep CI Hugo Version in Sync with Local

`HUGO_VERSION` in `.github/workflows/hugo.yml` must be new enough for
the Stack theme. With Hugo 0.147.1 the build failed on every page with:

```text
can't evaluate field IsImageResourceWithMeta in type interface {}
```

because the theme calls `reflect.IsImageResourceWithMeta`, which that
version doesn't have. When the theme is updated or builds start failing
with "can't evaluate field X" template errors, bump `HUGO_VERSION` to
match the local Hugo version (`hugo version`) where the build passes.

### Dead Remote Image URLs Slow the Build

Posts still referencing dead `ghostlessmachine.com/wp-content/...`
URLs make the theme's image helper call `resources.GetRemote`, which
times out (~30s total per build) and logs WARNs. Not fatal, but each
of these renders as a broken image on the live site — see
`missing-images.txt` for the backlog.

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

## Importing Medium posts

Newer posts are published on Medium only; locally they were WordPress
"stubs" (frontmatter + featured image + subtitle as the only body line).
Use `scripts/import_medium.py` to pull the full article into the bundle:

```bash
uv run scripts/import_medium.py <medium_url> [--slug <local-slug>] [--force]
```

What it does:

- Fetches the article via Medium's GraphQL API. **Use the
  `arielpontes.medium.com` subdomain endpoint** (`/_/graphql`) — plain
  `medium.com` is behind Cloudflare and blocks curl/urllib.
- Converts paragraphs to Markdown (headings, lists, quotes, images,
  YouTube embeds). Markup offsets from Medium are **UTF-16 code units**,
  not characters — the script handles this.
- Downloads inline images from `miro.medium.com` into the page bundle.
- Preserves existing stub frontmatter and adds `medium_url` plus
  `description` (the Medium subtitle, shown as the card subtitle).
- Refuses to overwrite a non-stub body (> 60 words) without `--force`.

### Member-only (paywalled) posts

For posts with Medium's member paywall, the anonymous API returns only a
preview (`content.isLockedPreviewOnly: true`) and the script aborts. Fetch
the content from a **logged-in browser** instead: open any
`arielpontes.medium.com` page, run the `CONTENT_QUERY` from the script
against `/_/graphql` with `credentials: 'include'`, save the JSON response
to a file, and run the script with `--json <file>`.

### Enumerating all Medium posts

The full post list (IDs, titles, URLs) comes from the same GraphQL
endpoint with the `UserStreamOverview` query, `userId: "85e7326edac3"`,
paginating with `pagingOptions.to` cursors. The RSS feed
(`arielpontes.medium.com/feed`) only returns the 10 newest posts.

### Redirecting list cards to Medium

Posts with `medium_url` in frontmatter link to Medium from the homepage
and other list pages, while the local page still exists (reachable via
search, archives single view, direct URL). This is done by overriding the
theme partials in `layouts/_partials/article/components/header.html` and
`details.html`: when `IsList` is true and `.Params.medium_url` is set, the
card's image and title anchors use the Medium URL instead of
`.RelPermalink`.

As of July 2026, everything from "Performative language" (2020-06) onward
is imported with `medium_url` set. Older stubs (e.g. `conspiracy-theories`,
`on-jordan-peterson`, `why-im-not-a-theist`) are still stubs and could be
imported the same way.

### Redirecting podcast posts to YouTube

Podcast posts (🎙️ in the title) are stubs whose real content is a YouTube
video; on WordPress they were full redirects. Setting `redirect_url` in
frontmatter recreates this:

- The single page emits `<meta http-equiv="refresh" content="0; url=...">`
  via the site override of the theme's empty
  `layouts/_partials/head/custom.html` hook.
- List cards link directly to the URL — the same two partial overrides
  used for `medium_url` also honor `redirect_url` (which takes precedence
  if both are set).

Unlike `medium_url`, a `redirect_url` page is never really viewable
locally — even a direct visit bounces to the target.
