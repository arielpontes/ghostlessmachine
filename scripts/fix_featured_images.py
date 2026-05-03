#!/usr/bin/env python3
"""
Move featured images from static/uploads to post directories for
Hugo Stack theme.
"""

import re
import shutil
from pathlib import Path


def process_post(post_dir, static_dir):
    """Process a single post directory."""
    # Find markdown files
    for md_file in post_dir.glob("index*.md"):
        content = md_file.read_text(encoding="utf-8")

        # Find image in frontmatter
        match = re.search(
            r'^image:\s*["\']?(/uploads/[^"\'"\n]+)["\']?',
            content,
            re.MULTILINE,
        )
        if not match:
            continue

        image_path = match.group(1)  # e.g., /uploads/2021/02/illusion.jpg

        # Build source path
        source = static_dir / image_path.lstrip("/")
        if not source.exists():
            print(f"  Warning: {source} not found")
            continue

        # Copy to post directory
        filename = source.name
        dest = post_dir / filename

        if not dest.exists():
            shutil.copy2(source, dest)
            print(f"  Copied: {filename}")

        # Update frontmatter to use just filename
        new_content = re.sub(
            r'^(image:\s*)["\']?/uploads/[^"\'"\n]+["\']?',
            f'\\1"{filename}"',
            content,
            flags=re.MULTILINE,
        )

        if new_content != content:
            md_file.write_text(new_content, encoding="utf-8")
            print(f"  Updated: {md_file.name}")


def main():
    project_dir = Path(__file__).parent.parent
    static_dir = project_dir / "static"
    content_dir = project_dir / "content"

    # Process posts
    print("Processing posts...")
    for post_dir in (content_dir / "post").iterdir():
        if post_dir.is_dir():
            process_post(post_dir, static_dir)

    # Process pages
    print("\nProcessing pages...")
    for page_dir in (content_dir / "page").iterdir():
        if page_dir.is_dir():
            process_post(page_dir, static_dir)

    print("\nDone!")


if __name__ == "__main__":
    main()
