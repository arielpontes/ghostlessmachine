#!/usr/bin/env python3
"""Import a Medium article into a Hugo page bundle.

Fetches the article via Medium's GraphQL API (on the arielpontes.medium.com
subdomain, which is not behind Cloudflare), converts its paragraphs to
Markdown, downloads inline images into the page bundle, and rewrites the
bundle's index.md preserving the existing frontmatter (title, date, slug,
image, categories) while adding `medium_url` and `description`.

Usage:
    uv run scripts/import_medium.py <medium_url> [--slug SLUG] [--json FILE]
                                    [--force]

- <medium_url>: the article URL (post ID is taken from its last segment).
- --slug: local bundle name under content/post/. Defaults to a slugified
  version of the article title.
- --json: path to a saved GraphQL response for the post. Needed for
  member-only posts, where the anonymous API returns only a preview: run
  the query in a logged-in browser and save the response (see the /hugo
  skill, "Importing Medium posts").
- --force: overwrite a local post whose body is not a short stub.

Member-only posts fetched anonymously are detected (isLockedPreviewOnly)
and rejected with instructions instead of silently importing the preview.
"""

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

GRAPHQL_URL = "https://arielpontes.medium.com/_/graphql"
IMAGE_URL = "https://miro.medium.com/v2/resize:fit:1400/{id}"
CONTENT_QUERY = """
query PostContent($postId: ID!) {
  post(id: $postId) {
    id
    title
    firstPublishedAt
    mediumUrl
    previewImage { id }
    content {
      isLockedPreviewOnly
      bodyModel {
        sections { startIndex }
        paragraphs {
          name type text href layout
          markups { type start end href anchorType }
          metadata { __typename id originalWidth originalHeight }
          iframe { mediaResource { href iframeSrc iframeWidth iframeHeight } }
          mixtapeMetadata { href thumbnailImageId }
        }
      }
    }
  }
}
"""
POSTS_DIR = Path(__file__).resolve().parent.parent / "content" / "post"
STUB_WORD_LIMIT = 60


def http(url, data=None, headers=None, retries=4):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, data=data, headers={"User-Agent": "Mozilla/5.0", **(headers or {})}
            )
            return urllib.request.urlopen(req, timeout=60).read()
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  retry {attempt + 1} after error: {e}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))


def fetch_post(post_id):
    payload = json.dumps(
        {"query": CONTENT_QUERY, "variables": {"postId": post_id}}
    ).encode()
    data = json.loads(
        http(
            GRAPHQL_URL,
            data=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
    )
    post = (data.get("data") or {}).get("post")
    if not post:
        sys.exit(f"GraphQL returned no post: {json.dumps(data)[:500]}")
    return post


def slugify(title):
    text = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    text = re.sub(r"[''’]", "", text)
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text


def apply_markups(text, markups):
    """Apply Medium markups. Offsets are UTF-16 code units, not characters."""
    tokens = {
        "EM": ("*", "*"),
        "STRONG": ("**", "**"),
        "CODE": ("`", "`"),
    }
    u16_to_py = {}
    u = 0
    for i, ch in enumerate(text):
        u16_to_py[u] = i
        u += len(ch.encode("utf-16-le")) // 2
    u16_to_py[u] = len(text)
    insertions = []
    for i, m in enumerate(markups or []):
        if m["type"] == "A" and m.get("href"):
            open_tok, close_tok = "[", f"]({m['href']})"
        elif m["type"] in tokens:
            open_tok, close_tok = tokens[m["type"]]
        else:
            continue
        start = u16_to_py.get(m["start"], len(text))
        end = u16_to_py.get(m["end"], len(text))
        # Medium ranges often include boundary whitespace; markdown markers
        # must hug the text (markdownlint MD037/MD039), so shrink the range.
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1
        if start >= end:
            continue
        # Sort keys make markups nest: at equal positions, close inner-first
        # (larger start) and open outer-first (larger end). The markup index
        # breaks ties for identical ranges (opened later -> closed earlier).
        insertions.append(((start, 1, -end, i), open_tok))
        insertions.append(((end, 0, -start, -i), close_tok))
    for (pos, _, _, _), tok in sorted(insertions, reverse=True):
        text = text[:pos] + tok + text[pos:]
    return text


def image_filename(image_id, bundle_dir):
    name = image_id.replace("*", "-")
    if re.search(r"\.(png|jpe?g|gif|webp|svg)$", name, re.I):
        return name
    existing = list(bundle_dir.glob(name + ".*"))
    if existing:
        return existing[0].name
    return name  # extension appended after download


def download_image(image_id, bundle_dir):
    name = image_filename(image_id, bundle_dir)
    if (bundle_dir / name).exists():
        return name
    url = IMAGE_URL.format(id=image_id)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=60)
    body = resp.read()
    if not re.search(r"\.(png|jpe?g|gif|webp|svg)$", name, re.I):
        ctype = resp.headers.get("Content-Type", "")
        ext = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/svg+xml": ".svg",
        }.get(ctype.split(";")[0].strip(), ".jpg")
        name += ext
    (bundle_dir / name).write_bytes(body)
    print(f"  image: {name}")
    return name


def youtube_id(url):
    m = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)", url or "")
    return m.group(1) if m else None


def to_markdown(post, bundle_dir):
    """Convert paragraphs to (description, markdown_body)."""
    paragraphs = post["content"]["bodyModel"]["paragraphs"]
    section_starts = {
        s["startIndex"] for s in post["content"]["bodyModel"].get("sections") or []
    }
    preview_image_id = (post.get("previewImage") or {}).get("id")
    description = None
    blocks = []
    list_items = []  # (type, rendered_text)
    quote_paras = []  # rendered text of consecutive BQ/PQ paragraphs

    def flush_list():
        if not list_items:
            return
        lines = []
        for n, (ptype, txt) in enumerate(list_items, 1):
            prefix = f"{n}. " if ptype == "OLI" else "- "
            lines.append(prefix + txt)
        blocks.append("\n".join(lines))
        list_items.clear()

    def flush_quotes():
        # Consecutive quote paragraphs (e.g. quote + attribution) become ONE
        # blockquote with `>` continuation lines; separate `>` blocks split
        # by blank lines trip markdownlint MD028.
        if not quote_paras:
            return
        rendered = [
            "\n".join("> " + line for line in para.split("\n"))
            for para in quote_paras
        ]
        blocks.append("\n>\n".join(rendered))
        quote_paras.clear()

    for idx, p in enumerate(paragraphs):
        ptype = p["type"]
        if ptype not in ("ULI", "OLI") or (
            list_items and list_items[0][0] != ptype
        ):
            flush_list()
        if ptype not in ("BQ", "PQ"):
            flush_quotes()
        if idx in section_starts and idx > 0 and blocks:
            blocks.append("---")
        text = apply_markups(p.get("text") or "", p.get("markups"))

        if ptype == "H3" and idx == 0 and p["text"] == post["title"]:
            continue
        if ptype == "H4" and idx <= 2 and description is None and not blocks:
            description = p["text"]
            continue
        if ptype == "IMG":
            meta = p.get("metadata") or {}
            image_id = meta.get("id")
            if not image_id:
                continue
            if image_id == preview_image_id and not blocks:
                continue  # cover image; the bundle already has a featured image
            name = download_image(image_id, bundle_dir)
            alt = re.sub(r"[\[\]]", "", p.get("text") or "") or "Image"
            blocks.append(f"![{alt}]({name})")
            if text:
                blocks.append(f"*{text}*")
        elif ptype in ("ULI", "OLI"):
            list_items.append((ptype, text))
        elif ptype == "H3":
            blocks.append(f"## {text}")
        elif ptype == "H4":
            blocks.append(f"### {text}")
        elif ptype in ("BQ", "PQ"):
            quote_paras.append(text)
        elif ptype == "PRE":
            blocks.append("```\n" + (p.get("text") or "") + "\n```")
        elif ptype == "MIXTAPE_EMBED":
            href = (p.get("mixtapeMetadata") or {}).get("href")
            if href:
                label = (p.get("text") or href).split("\n")[0]
                blocks.append(f"[{label}]({href})")
        elif ptype == "IFRAME":
            media = (p.get("iframe") or {}).get("mediaResource") or {}
            href = media.get("href") or media.get("iframeSrc")
            vid = youtube_id(href)
            if vid:
                blocks.append(f"{{{{< youtube {vid} >}}}}")
            elif href:
                blocks.append(f"[{href}]({href})")
        elif ptype == "P":
            if text:
                blocks.append(text)
        else:
            print(f"  WARNING: unhandled paragraph type {ptype}: {text[:80]!r}")
            if text:
                blocks.append(text)
    flush_list()
    flush_quotes()
    return description, "\n\n".join(blocks) + "\n"


def update_index(bundle_dir, post, description, body, force):
    index = bundle_dir / "index.md"
    medium_url = post.get("mediumUrl") or ""
    if index.exists():
        content = index.read_text()
        m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", content, re.S)
        if not m:
            sys.exit(f"Cannot parse frontmatter in {index}")
        frontmatter, old_body = m.groups()
        if len(old_body.split()) > STUB_WORD_LIMIT and not force:
            sys.exit(
                f"{index} body has more than {STUB_WORD_LIMIT} words — not a stub. "
                "Use --force to overwrite."
            )
        if "medium_url:" not in frontmatter:
            frontmatter += f'\nmedium_url: "{medium_url}"'
        if description and "description:" not in frontmatter:
            escaped = description.replace('"', '\\"')
            frontmatter += f'\ndescription: "{escaped}"'
    else:
        date = time.strftime(
            "%Y-%m-%dT%H:%M:%S", time.localtime(post["firstPublishedAt"] / 1000)
        )
        lines = [
            f'title: "{post["title"]}"',
            f"date: {date}",
            f'slug: "{bundle_dir.name}"',
        ]
        preview_id = (post.get("previewImage") or {}).get("id")
        if preview_id:
            lines.append(f'image: "{download_image(preview_id, bundle_dir)}"')
        lines.append(f'medium_url: "{medium_url}"')
        if description:
            lines.append(f'description: "{description.replace(chr(34), chr(92) + chr(34))}"')
        frontmatter = "\n".join(lines)
    index.write_text(f"---\n{frontmatter}\n---\n\n{body}")
    print(f"  wrote {index}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("medium_url")
    parser.add_argument("--slug", help="local bundle name under content/post/")
    parser.add_argument("--json", help="saved GraphQL response for member-only posts")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    post_id = args.medium_url.rstrip("/").split("-")[-1].split("?")[0]
    if not re.fullmatch(r"[0-9a-f]+", post_id):
        sys.exit(f"Cannot extract post ID from {args.medium_url}")

    if args.json:
        data = json.loads(Path(args.json).read_text())
        post = (data.get("data") or {}).get("post") or data.get("post") or data
        if "content" not in post:
            sys.exit(f"{args.json} does not look like a PostContent response")
    else:
        post = fetch_post(post_id)

    if post["content"].get("isLockedPreviewOnly"):
        sys.exit(
            "This post is member-only and the anonymous API only returns a "
            "preview. Run the PostContent GraphQL query in a logged-in browser, "
            "save the response, and re-run with --json <file>. See the /hugo "
            'skill, section "Importing Medium posts".'
        )

    slug = args.slug or slugify(post["title"])
    bundle_dir = POSTS_DIR / slug
    bundle_dir.mkdir(exist_ok=True)
    print(f"{post['title']} -> {bundle_dir.relative_to(POSTS_DIR.parent.parent)}")
    description, body = to_markdown(post, bundle_dir)
    update_index(bundle_dir, post, description, body, args.force)


if __name__ == "__main__":
    main()
