"""Build a verified text-fragment URL (#:~:text=...) for a web page.

Given a URL and a verbatim passage, fetches the page, confirms the
passage occurs in its visible text, and prints the URL with a
scroll-to-text fragment appended, ready to paste into an article.
Supporting browsers scroll to and highlight the passage; others just
open the page. If the passage differs from the page only in "smart"
punctuation (curly quotes, dashes, ellipses, non-breaking spaces),
the page's exact wording is used and the substitution is reported.
Long passages are shortened to a start,end range so URLs stay sane.
Several passages may be given; each becomes its own highlight.
Used by the provide-sources skill to deep-link long pages.
"""

import argparse
import html.parser
import re
import sys
import urllib.parse
import urllib.request

USER_AGENT = "Mozilla/5.0 (ghostlessmachine-text-fragment)"
RANGE_ABOVE_WORDS = 12
EDGE_WORDS = 5

SMART = str.maketrans(
    {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "–": "-",
        "—": "-",
        "…": ".",
        " ": " ",
    }
)


class TextExtractor(html.parser.HTMLParser):
    SKIP = {"script", "style", "noscript"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)


def fetch_text(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request) as resp:
        raw = resp.read()
    charset = resp.headers.get_content_charset() or "utf-8"
    extractor = TextExtractor()
    extractor.feed(raw.decode(charset, errors="replace"))
    return " ".join(extractor.parts)


def fold(text):
    """Collapse whitespace and smart punctuation; keep an index map."""
    out, index = [], []
    prev_space = False
    for i, ch in enumerate(text):
        if ch.isspace() or ch == " ":
            if prev_space:
                continue
            out.append(" ")
            prev_space = True
        else:
            out.append(ch.translate(SMART))
            prev_space = False
        index.append(i)
    return "".join(out), index


def find_passage(page, quote):
    """Return the page's exact substring matching quote, else None."""
    folded_page, index = fold(page)
    folded_quote, _ = fold(quote)
    folded_quote = folded_quote.strip()
    pos = folded_page.find(folded_quote)
    if pos < 0:
        return None, 0
    count = folded_page.count(folded_quote)
    first = index[pos]
    stop = index[pos + len(folded_quote) - 1] + 1
    exact = page[first:stop]
    return re.sub(r"\s+", " ", exact), count


def encode(text):
    return urllib.parse.quote(text, safe="").replace("-", "%2D")


def shorten(passage, folded_page):
    """Pick unambiguous start,end word runs for a long passage."""
    words = passage.split(" ")
    folded_passage, _ = fold(passage)
    passage_at = folded_page.find(folded_passage)
    for n in range(EDGE_WORDS, len(words) // 2 + 1):
        start = " ".join(words[:n])
        end = " ".join(words[-n:])
        folded_start, _ = fold(start)
        folded_end, _ = fold(end)
        end_at = folded_page.find(folded_end, passage_at + len(folded_start))
        starts_here = folded_page.find(folded_start) == passage_at
        ends_here = end_at == passage_at + len(folded_passage) - len(
            folded_end
        )
        if starts_here and ends_here:
            return start, end
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="page URL")
    parser.add_argument(
        "quotes",
        nargs="+",
        help="verbatim passage(s) the link supports",
    )
    args = parser.parse_args()

    page = fetch_text(args.url)
    folded_page, _ = fold(page)
    fragments = []
    for quote in args.quotes:
        passage, count = find_passage(page, quote)
        if passage is None:
            sys.exit(
                f"error: passage not found in the page's visible "
                f"text: {quote}\n"
                "Check the wording against the page (the fragment must "
                "match the page exactly for the browser to highlight it)."
            )
        if passage != re.sub(r"\s+", " ", quote.strip()):
            print(f"note: using the page's exact wording: {passage}")
        if count > 1:
            print(
                f"warning: passage occurs {count} times; "
                "the browser highlights the first occurrence"
            )
        fragment = encode(passage)
        if len(passage.split(" ")) > RANGE_ABOVE_WORDS:
            edges = shorten(passage, folded_page)
            if edges:
                fragment = f"{encode(edges[0])},{encode(edges[1])}"
        fragments.append(fragment)
    base = urllib.parse.urldefrag(args.url).url
    print(f"{base}#:~:text=" + "&text=".join(fragments))


if __name__ == "__main__":
    main()
