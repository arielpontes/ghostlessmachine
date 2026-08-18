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

## Link to the passage, not the page

A source link's job is to let the reader verify the specific claim.
Linking a long page bare (an encyclopedia entry, a book commentary, a
full-text chapter) fails at that job even when the support is in there
somewhere — the reader can't find it. Whenever the supporting material
is one passage of a longer page, deep-link the passage with a
scroll-to-text fragment (`#:~:text=…`), generated and verified in one
step — never hand-build the fragment, the encoding rules are fiddly:

```bash
uv run scripts/text_fragment.py <url> "verbatim passage" ["second passage" …]
```

The script fetches the page, confirms each passage occurs in its
visible text (recovering the page's exact smart punctuation if the
input differs only in quotes/dashes), and prints the ready-to-paste
URL. Long passages are automatically shortened to a `start,end` range.
Supporting browsers (all major ones since 2024) scroll to and
highlight the passage; older ones just open the page, so the fragment
never hurts.

- Pick the shortest passage that states the cited point; pass several
  passages when the claim has several parts.
- The fragment earns its place only when the reader would otherwise
  have to hunt for the passage. Skip it when the support is already
  the first thing a visitor sees: if the highlight would land in the
  headline or subhead, it is by definition unnecessary, and the same
  goes for a page's opening sentences (e.g. an encyclopedia entry's
  lead definition).
- Also skip it when the whole page is the referent: a short lay
  article a quick skim of which visibly confirms the point, a
  definitional link to a concept, a Goodreads quote page.
- If the script can't find the passage (client-rendered page) or the
  site defeats fragments (`Document-Policy: force-load-at-top`),
  prefer a shorter page that makes the same point; as a last resort,
  quote the passage in the article itself as a blockquote with
  attribution and link the page bare.

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
- A reference link (a concept or definition link, as opposed to a
  passage citation) belongs on the term's first mention in the
  article, once. Working on one section is no excuse to skip this
  check — it needs two cheap greps of the full file, not a read:
  grep for a distinctive part of the URL (already linked anywhere →
  don't link again) and for the term itself (an earlier unlinked
  mention → put the link there instead of in the working section).
  Passage citations are exempt: linking different passages of the
  same page in support of different claims is fine.
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
