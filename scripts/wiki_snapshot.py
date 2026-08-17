"""Print permanent-snapshot links for Wikipedia articles, verifying quotes.

For each title: the latest revision id and its "Permanent link" (oldid)
URL, ready to paste into an article. With --quote, also checks that the
quoted text appears verbatim in that revision's plain text, so drafts
never quote wording that has drifted. Bracketed alterations ("[It]",
"[...]") in the quote are skipped: each remaining span must match.
Used by the provide-sources skill to snapshot living documents without
loading full articles into context.
"""

import argparse
import difflib
import json
import re
import sys
import urllib.parse
import urllib.request

API = "https://en.wikipedia.org/w/api.php"
PERMALINK = "https://en.wikipedia.org/w/index.php?title={title}&oldid={rev}"
USER_AGENT = "ghostlessmachine-wiki-snapshot (pontes.ariel@gmail.com)"
CONTEXT_CHARS = 200

TRANSLATE = str.maketrans(
    {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "–": "-",
        "—": "-",
        " ": " ",
    }
)


def normalize(text):
    text = text.translate(TRANSLATE).replace("…", "...")
    return re.sub(r"\s+", " ", text).strip()


def fetch_article(title):
    params = {
        "action": "query",
        "prop": "revisions|extracts",
        "titles": title,
        "rvprop": "ids",
        "explaintext": 1,
        "exlimit": 1,
        "redirects": 1,
        "format": "json",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request) as resp:
        pages = json.load(resp)["query"]["pages"]
    page = next(iter(pages.values()))
    if "missing" in page:
        sys.exit(f"error: no Wikipedia article named {title!r}")
    revid = page["revisions"][0]["revid"]
    return page["title"], revid, page.get("extract", "")


def check_quote(quote, text):
    """Return the first quoted span missing from text, or None if all match."""
    spans = re.split(r"\[[^\]]*\]", normalize(quote))
    for span in spans:
        span = span.strip()
        if len(span) > 3 and span not in text:
            return span
    return None


def closest_context(span, text):
    match = difflib.SequenceMatcher(None, text, span).find_longest_match()
    start = max(0, match.a - CONTEXT_CHARS // 2)
    end = match.a + match.size + CONTEXT_CHARS // 2
    return text[start:end]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("titles", nargs="+", help="Wikipedia article titles")
    parser.add_argument(
        "--quote",
        help="verbatim quote to verify (single title only)",
    )
    args = parser.parse_args()
    if args.quote and len(args.titles) > 1:
        parser.error("--quote requires exactly one title")
    for title in args.titles:
        canonical, revid, extract = fetch_article(title)
        quoted = urllib.parse.quote(canonical.replace(" ", "_"))
        print(f"# {canonical}")
        print(f"revid: {revid}")
        print(f"permalink: {PERMALINK.format(title=quoted, rev=revid)}")
        if args.quote:
            missing = check_quote(args.quote, normalize(extract))
            if missing is None:
                print("quote: OK (verbatim in this revision)")
            else:
                print("quote: NOT FOUND")
                print(f"missing span: {missing}")
                print(
                    "closest match in article: ..."
                    + closest_context(missing, normalize(extract))
                    + "..."
                )


if __name__ == "__main__":
    main()
