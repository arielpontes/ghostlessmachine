---
name: find-featured-image
description: >-
  Use when a blog post needs a featured image (the image front matter
  field shown in thumbnails and previews). Searches free stock sites
  first, then general image search as a fallback, presents candidates
  for the user to pick, then installs the chosen image into the post
  bundle(s) with a source caption.
---

# Find featured image

Every post has a featured image, stored in the post's page bundle next
to `index.md` and referenced by the `image:` front matter field.

## Finding candidates

1. Read the article (or draft) first — the image must reflect its
   actual thesis and mood, not just its title.
2. Before searching, propose a few thematic directions (visual
   metaphors — e.g. for a post on political tribalism: a fork in the
   road, opposing crowds, a tug of war) and let the user pick one or
   two. Don't jump straight from the article to search results: the
   direction is an aesthetic choice that belongs to the user.
3. Search free stock sites first: Unsplash, Pexels, Pixabay.
4. If nothing good turns up there, fall back to a general image search
   (Google Images). Using a non-free image is acceptable on this blog:
   the source is always cited, and the image gets taken down if the
   owner ever asks.
5. Verify candidates before presenting them: download small previews
   into `image-workshop/<post-slug>/` at the repo root (gitignored —
   never the session scratchpad or `/tmp`, which get wiped after a few
   days) and look at them — search-page text descriptions are often
   wrong or miss what the image actually conveys.
6. Present several candidates to the user as links, each with a
   one-line description of what it shows and where it's from. The user
   picks — never install an image without approval, since the choice is
   aesthetic.

## Installing the chosen image

1. Download the image into the post's bundle with curl, using a short
   descriptive filename in the style of existing posts (`ghost.jpeg`,
   `math.jpg`, `free-will.png`).
2. Set `image: "<filename>"` in the front matter.
3. Add a caption with the `image_caption` front matter field —
   free-form markdown rendered verbatim as a centered caption under the
   featured image on the post page (rendered by
   `layouts/_partials/article/components/header.html`, styled by
   `.article-image-caption` in `assets/scss/custom.scss`). It can be a
   bare source citation, a description, or both:

   ```yaml
   image_caption: "Source: [Body shaming is more dangerous than you
     think (2020, The Jakarta Post)](https://www.example.com/...)"
   ```

   When citing, link text format: page or photo title, then `(year,
   publisher or site)`. For stock photos, credit the photographer and
   the site, e.g. `[Photo by Jane Doe (Unsplash)](https://...)`. A
   descriptive caption can also weave the link into prose and add a
   sentence connecting the image to the article's thesis.
4. Bilingual posts are two separate page bundles (EN and PT). Copy the
   image file into both and set `image:` and `image_caption:` in both
   front matters (translate the caption for the PT version).
