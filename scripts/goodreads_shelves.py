"""Print Ariel's Goodreads shelves (currently-reading + read) as compact text.

One line per book: author<TAB>title, grouped under a "# <shelf>" header.
Used by the provide-sources skill to prioritize familiar sources without
loading raw RSS XML into context.
"""

import urllib.request
import xml.etree.ElementTree as ET

USER_ID = "17536885"
SHELVES = ["currently-reading", "read"]
URL = "https://www.goodreads.com/review/list_rss/{user}?shelf={shelf}&page={page}"


def fetch_shelf(shelf):
    books = []
    page = 1
    while True:
        url = URL.format(user=USER_ID, shelf=shelf, page=page)
        with urllib.request.urlopen(url) as resp:
            root = ET.fromstring(resp.read())
        items = root.findall("./channel/item")
        if not items:
            return books
        for item in items:
            author = (item.findtext("author_name") or "").strip()
            title = (item.findtext("title") or "").strip()
            books.append((author, title))
        page += 1


def main():
    for shelf in SHELVES:
        print(f"# {shelf}")
        for author, title in fetch_shelf(shelf):
            print(f"{author}\t{title}")


if __name__ == "__main__":
    main()
