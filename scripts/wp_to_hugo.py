#!/usr/bin/env python3
"""
Convert WordPress XML export to Hugo markdown files.
Handles multilingual content (English and Portuguese via Polylang).
"""

import re
import xml.etree.ElementTree as ET
from datetime import datetime
from html import unescape
from pathlib import Path
from urllib.parse import unquote

from markdownify import markdownify as md


def parse_cdata(text):
    """Extract text from CDATA sections."""
    if text is None:
        return ""
    return text.strip()


def get_language(item, ns):
    """Get the language of a post from Polylang categories."""
    for cat in item.findall("category"):
        if cat.get("domain") == "language":
            nicename = cat.get("nicename", "").lower()
            if nicename in ("en", "pt"):
                return nicename
    return "en"  # Default to English


def get_categories(item):
    """Get categories from a post."""
    categories = []
    for cat in item.findall("category"):
        if cat.get("domain") == "category":
            name = cat.text
            if name and "uncategorized" not in name.lower():
                categories.append(name)
    return categories


def get_tags(item):
    """Get tags from a post (excluding language tags)."""
    tags = []
    for cat in item.findall("category"):
        if cat.get("domain") == "post_tag":
            name = cat.text
            if name and name.lower() not in ("en", "pt"):
                tags.append(name)
    return tags


def slugify(text):
    """Create a URL-friendly slug from text."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def html_to_markdown(html_content):
    """Convert HTML content to Markdown."""
    if not html_content:
        return ""

    # Unescape HTML entities
    content = unescape(html_content)

    # Convert to markdown
    markdown = md(content, heading_style="ATX", bullets="-")

    # Clean up excessive newlines
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)

    return markdown.strip()


def create_frontmatter(
    title, date, categories, tags, slug, draft=False, image=None
):
    """Create Hugo frontmatter."""
    lines = ["---"]

    # Escape title for YAML
    escaped_title = title.replace('"', '\\"')
    lines.append(f'title: "{escaped_title}"')

    if date:
        lines.append(f"date: {date}")

    if slug:
        escaped_slug = slug.replace('"', '\\"')
        lines.append(f'slug: "{escaped_slug}"')

    if draft:
        lines.append("draft: true")

    if image:
        lines.append(f'image: "{image}"')

    if categories:
        lines.append("categories:")
        for cat in categories:
            escaped_cat = cat.replace('"', '\\"')
            lines.append(f'  - "{escaped_cat}"')

    if tags:
        lines.append("tags:")
        for tag in tags:
            escaped_tag = tag.replace('"', '\\"')
            lines.append(f'  - "{escaped_tag}"')

    lines.append("---")
    return "\n".join(lines)


def process_wordpress_export(xml_path, output_dir):
    """Process WordPress XML export and create Hugo content files."""

    # Define namespaces
    ns = {
        "content": "http://purl.org/rss/1.0/modules/content/",
        "wp": "http://wordpress.org/export/1.2/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "excerpt": "http://wordpress.org/export/1.2/excerpt/",
    }

    # Parse XML
    print(f"Parsing {xml_path}...")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Find all items
    channel = root.find("channel")
    items = channel.findall("item")

    # Build attachment ID to URL mapping
    attachment_map = {}
    for item in items:
        post_type_elem = item.find("wp:post_type", ns)
        if (
            post_type_elem is not None
            and parse_cdata(post_type_elem.text) == "attachment"
        ):
            post_id_elem = item.find("wp:post_id", ns)
            attachment_url_elem = item.find("wp:attachment_url", ns)
            if post_id_elem is not None and attachment_url_elem is not None:
                post_id = parse_cdata(post_id_elem.text)
                url = parse_cdata(attachment_url_elem.text)
                # Convert to local path
                if "wp-content/uploads/" in url:
                    local_path = (
                        "/uploads/" + url.split("wp-content/uploads/")[-1]
                    )
                    attachment_map[post_id] = local_path

    print(f"  Found {len(attachment_map)} attachments")

    stats = {"posts": 0, "pages": 0, "skipped": 0}

    for item in items:
        # Get post type
        post_type_elem = item.find("wp:post_type", ns)
        if post_type_elem is None:
            continue
        post_type = parse_cdata(post_type_elem.text)

        # Only process posts and pages
        if post_type not in ("post", "page"):
            continue

        # Get status
        status_elem = item.find("wp:status", ns)
        status = (
            parse_cdata(status_elem.text)
            if status_elem is not None
            else "draft"
        )

        # Skip private/trash posts
        if status in ("private", "trash", "inherit"):
            stats["skipped"] += 1
            continue

        # Get basic info
        title = item.find("title").text or "Untitled"

        # Get content
        content_elem = item.find("content:encoded", ns)
        content = (
            parse_cdata(content_elem.text) if content_elem is not None else ""
        )

        # Skip empty posts
        if not content.strip():
            stats["skipped"] += 1
            continue

        # Get date
        date_elem = item.find("wp:post_date", ns)
        date_str = parse_cdata(date_elem.text) if date_elem is not None else ""

        # Parse and format date
        formatted_date = ""
        if date_str and date_str != "0000-00-00 00:00:00":
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                formatted_date = dt.strftime("%Y-%m-%dT%H:%M:%S")
            except ValueError:
                pass

        # Get slug
        slug_elem = item.find("wp:post_name", ns)
        slug = parse_cdata(slug_elem.text) if slug_elem is not None else ""
        # Decode URL-encoded slugs and make ASCII-safe
        if slug:
            slug = unquote(slug)
            slug = slugify(slug)
        if not slug:
            slug = slugify(title)

        # Get language
        lang = get_language(item, ns)

        # Get categories and tags
        categories = get_categories(item)
        tags = get_tags(item)

        # Get featured image (thumbnail)
        featured_image = None
        for postmeta in item.findall("wp:postmeta", ns):
            meta_key = postmeta.find("wp:meta_key", ns)
            meta_value = postmeta.find("wp:meta_value", ns)
            if (
                meta_key is not None
                and parse_cdata(meta_key.text) == "_thumbnail_id"
            ):
                thumbnail_id = parse_cdata(meta_value.text)
                if thumbnail_id in attachment_map:
                    featured_image = attachment_map[thumbnail_id]
                break

        # Determine if draft
        is_draft = status != "publish"

        # Convert content to markdown
        markdown_content = html_to_markdown(content)

        # Create frontmatter
        frontmatter = create_frontmatter(
            title,
            formatted_date,
            categories,
            tags,
            slug,
            is_draft,
            featured_image,
        )

        # Determine output path
        if post_type == "post":
            content_type = "post"
            stats["posts"] += 1
        else:
            content_type = "page"
            stats["pages"] += 1

        # Create directory structure for multilingual
        # Hugo Stack theme uses: content/post/my-post/index.md for
        # default language and content/post/my-post/index.pt.md for
        # Portuguese

        output_subdir = Path(output_dir) / content_type / slug
        output_subdir.mkdir(parents=True, exist_ok=True)

        if lang == "en":
            output_file = output_subdir / "index.md"
        else:
            output_file = output_subdir / f"index.{lang}.md"

        # Write file
        full_content = f"{frontmatter}\n\n{markdown_content}\n"
        output_file.write_text(full_content, encoding="utf-8")

        print(f"  Created: {output_file}")

    print(
        f"\nDone! Created {stats['posts']} posts, "
        f"{stats['pages']} pages, "
        f"skipped {stats['skipped']} items."
    )


if __name__ == "__main__":
    import sys

    script_dir = Path(__file__).parent
    project_dir = script_dir.parent

    xml_path = project_dir / "wordpress-export.xml"
    output_dir = project_dir / "content"

    if not xml_path.exists():
        print(f"Error: WordPress export not found at {xml_path}")
        sys.exit(1)

    process_wordpress_export(xml_path, output_dir)
