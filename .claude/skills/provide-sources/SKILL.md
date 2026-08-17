---
name: provide-sources
description: >-
  Use whenever the user asks to provide sources for claims in a piece of
  writing. Finds credible sources, inserts them as inline links in the
  text, and reports a per-claim confidence assessment in the chat
  response.
---

# Provide sources

Use this skill whenever the user asks to provide sources for one or more
claims in a piece of writing.

## Source selection

1. Prefer lay articles from credible sources: mainstream news
   organizations, university blogs and press releases, reputable
   magazines, book summaries or reviews.
2. Books are also acceptable when a book is the best authority for the
   claim (e.g. the claim is about an author's argument). Cite them
   using the formats in "Citing books" below.
3. Fall back to proper academic articles (journal papers, working
   papers) only when no good lay article or book covers the claim.
4. Always open each candidate source (WebFetch, or curl if blocked) and
   confirm it actually supports the specific claim as written. Never
   cite based on search-result snippets alone. For a book, verify
   through what is accessible — excerpts, quote pages, reviews,
   publisher summaries — and lower the source confidence if the
   supporting passage itself couldn't be read.

## Prioritizing familiar sources

The author's Goodreads shelves list the books he has read or is
reading. Fetch both shelves at the start of source selection:

```bash
uv run scripts/goodreads_shelves.py
```

It prints one `author<TAB>title` line per book under `# currently-reading`
and `# read` headers — never fetch the Goodreads RSS directly, the raw
XML wastes tokens.

Use the shelves as a preference order when several sources could
support a claim:

1. A book on the shelves.
2. A work by an author who appears on the shelves.
3. An article or study cited inside a book on the shelves, when you
   know of one.
4. Anything else, per the source-selection rules above.

This is a tie-breaker, not a filter: a familiar source must still pass
the verification rule above (confirm it supports the specific claim as
written), and an unfamiliar source that supports the claim beats a
familiar one that doesn't.

## Citing books and quotes

House style — use these formats and no others:

- Book titles are always in italics, never in quotation marks
  (quotation marks are for shorter works: articles, chapters, songs).
- Link target: a page containing the relevant passage if one exists;
  otherwise the book's Goodreads page.
- Inline mention: casual, with the title as an italicized link —
  `As Chomsky argues in [*On Anarchism*](url), …`. No author-date
  parentheticals like "(Chomsky, 2005)" — the blog has no reference
  list for a year to resolve against. Mention the year in prose only
  when the date matters to the argument.
- Direct quote: markdown blockquote with the attribution as its own
  paragraph inside the blockquote (a lone `>` line separates it from
  the quote text), in the format `— Author Fullname, [Source](url),
  year`, with an em dash. The source is whatever the words originally
  appeared in: an italicized book title, a plain-text publication name
  (`[New York Post](url)`), or a short description (`[interview with
  Harry Kreisler](url)`). The year is always included, and it is the
  year of original publication or utterance — an interview's year, not
  the year of a book that later reprinted it.
- Quoted text must be verbatim. Check the exact wording against the
  source; if the draft paraphrases inside quotation marks or a
  blockquote, correct it to the original wording and flag the change
  in the response.
- A quotation inside a running sentence (e.g. a quoted definition)
  takes the link on the term or phrase being discussed — never a
  trailing parenthetical like `([Wikipedia](url))`.
- A blockquote introduced by a lead-in sentence that names the source
  ("According to Wikipedia:") takes the link on the source name in the
  lead-in and no attribution line — attribution lines are for quotes
  that stand on their own.
- Authorless collective sources (Wikipedia and the like) put the
  publication in the author slot and the article title, in quotation
  marks, in the source slot: `— Wikipedia, ["Neoliberalism"](url)`.
  Omit the year: a continuously edited source has no year of original
  utterance.
- When quoting a living document verbatim, link a permanent snapshot
  of the revision the quote was checked against — for Wikipedia, the
  "Permanent link" (`oldid`) URL — so the linked text keeps matching
  the quote. Live URLs remain the right target for reference links
  that don't quote the page. For Wikipedia, get the permalink and
  verify the quote in one step — never call the API by hand:

  ```bash
  uv run scripts/wiki_snapshot.py "Article title" --quote "quoted text"
  ```

  It prints the revision's permalink URL and `quote: OK` when the
  quote is verbatim in that revision; on `NOT FOUND` it prints the
  closest matching passage so the drift can be fixed. Bracketed
  alterations ("[It]", "[…]") in the quote are skipped automatically.
- When the draft already cites a source in another style (author-date,
  plain-text book title, en-dash attribution, missing year, missing
  `>` separator line), normalizing it to these formats is an allowed
  edit, as an exception to the wrap-existing-words-only rule below.

## Editing the text

- Insert each source as an inline markdown link on the most relevant
  existing phrase — never as footnotes or a references section.
- The only change to the text is wrapping existing words in links. Do
  not reword claims, and do not add commentary, confidence levels, or
  caveats to the text itself.
- If a claim is not defensible (see below), do not link anything for it;
  flag it in the response instead.

## The response to the user

After editing, report an assessment for every claim, including two
separate confidence levels:

- **Claim confidence** — how well the claim holds up against current
  scientific/academic knowledge:
  - **Solid**: a mainstream, well-supported position.
  - **Defensible but a stretch**: can reasonably be argued, but is
    overstated, contested, or stronger than the evidence — say in what
    way.
  - **Not defensible**: unsupported by or contradicted by current
    scholarship. Tell the user plainly and leave it unsourced.
- **Source confidence** — high / medium / low confidence that the
  chosen source actually corroborates the claim as written, noting any
  gap between what the claim says and what the source shows.

Before calling a claim a stretch, parse its actual scope carefully. A
qualifying clause often already restricts the claim to something
defensible (e.g. "an approach to economics that disregards evidence"
criticizes that specific approach, not economics as a discipline).
Don't propose rewrites that soften the author's criticism to fix a
misreading the sentence doesn't actually invite — flag only what the
sentence, read carefully, really claims. A gap between the claim's
scope and the source's scope belongs under source confidence, not in a
rewording proposal.

Keep all of this assessment in the chat response only.
