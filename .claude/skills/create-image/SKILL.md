---
name: create-image
description: >-
  Use when a post needs a custom image that no stock photo satisfies
  and that can be composed programmatically: symbol collages, flat
  graphic compositions, text-based graphics. Sources SVG elements from
  Wikimedia Commons, composes them with a Python script, and iterates
  with the user until approval.
---

# Create image

For simple graphic compositions (symbol collages, flat posters), no
image-generation model is needed — compose the image with a script.
This only produces graphic-design-style images (flat elements layered
on a canvas); photorealistic or painterly images are out of scope, so
say so instead of attempting them.

## Sourcing elements

- Wikimedia Commons has clean SVGs for most symbols, flags, and logos,
  served raw at
  `https://commons.wikimedia.org/wiki/Special:FilePath/<File_name>.svg`.
- Always send a descriptive User-Agent
  (`curl -A "ghostlessmachine-featured-image/1.0 (<email>)"`): with
  curl's default UA, Wikimedia throttles you into persistent 429s
  after a handful of requests; with a proper UA it doesn't.
- Don't guess filenames one by one — query the search API, which
  returns real file titles in one request:
  `https://commons.wikimedia.org/w/api.php?action=query&list=search&srnamespace=6&format=json&srsearch=<terms>%20filetype:drawing`.
  Then verify individual titles with `curl -I -L` on Special:FilePath
  (404 = doesn't exist).
- Simple glyphs (a dollar sign, a letter) don't need an SVG: render
  text with Pillow using a system font from
  `/System/Library/Fonts/Supplemental/`.
- Save working files (downloaded SVGs, generated variants) to
  `image-workshop/<post-slug>/` at the repo root — never to the
  session scratchpad or `/tmp`, which get wiped after a few days. The
  folder is gitignored; only the final approved PNG enters the post
  bundle.

## Composing

- `scripts/symbol_collage.py` scatters SVG symbols over a 16:9 canvas:
  rasterized with `rsvg-convert` (Homebrew), composed with Pillow
  (already a uv dependency). Adapt it, or write a sibling script for a
  different kind of composition.
- Keep scripts deterministic (seeded RNG, no wall-clock input) so a
  look the user liked can be reproduced and then tweaked.
- Default the canvas to 1600x900: the featured-image grid crops
  thumbnails to 16:9.

## Iterating

- Always look at the generated PNG yourself (Read it) before showing
  it, and fix obvious defects first: clipped elements, clumping, big
  empty patches, symbols invisible against the background.
- Generate 2-3 variants (different seeds or parameters) and give the
  user the file paths to look at. Iterate until they approve — never
  install without approval.

## Installing

Install like in the `find-featured-image` skill: copy the PNG into the
post's page bundle(s), set `image:` in the front matter. A composed
image made only of public-domain/CC Wikimedia Commons elements needs no
`image_caption` credit by default; if the user wants one, link the
Commons file pages.
