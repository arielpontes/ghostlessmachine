"""Archive the WordPress-era reader comments as a Hugo data file.

Reads `wordpress-export.xml` at the repo root and writes
`data/archived_comments.json`: approved, human-written comments (no
pingbacks, trackbacks or spam) grouped by post slug, so they can be
rendered again later if wanted. Commenter emails and IP addresses are
left out on purpose.

    uv run scripts/export_comments.py
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORT = ROOT / "wordpress-export.xml"
OUTPUT = ROOT / "data" / "archived_comments.json"
NS = {"wp": "http://wordpress.org/export/1.2/"}


def text(node, tag):
    return (node.findtext(tag, namespaces=NS) or "").strip()


def human_comments(item):
    for c in item.findall("wp:comment", NS):
        if text(c, "wp:comment_approved") != "1":
            continue
        if text(c, "wp:comment_type") not in ("", "comment"):
            continue
        yield {
            "id": int(text(c, "wp:comment_id")),
            "parent": int(text(c, "wp:comment_parent")),
            "author": text(c, "wp:comment_author"),
            "author_url": text(c, "wp:comment_author_url"),
            "date_gmt": text(c, "wp:comment_date_gmt"),
            "content": text(c, "wp:comment_content"),
        }


def main():
    posts = {}
    for item in ET.parse(EXPORT).getroot().iter("item"):
        if text(item, "wp:post_type") != "post":
            continue
        comments = sorted(human_comments(item), key=lambda c: c["id"])
        if not comments:
            continue
        posts[text(item, "wp:post_name")] = {
            "title": text(item, "title"),
            "wordpress_url": text(item, "link"),
            "comments": comments,
        }
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n")
    total = sum(len(p["comments"]) for p in posts.values())
    print(f"wrote {total} comments on {len(posts)} posts to {OUTPUT}")


if __name__ == "__main__":
    main()
