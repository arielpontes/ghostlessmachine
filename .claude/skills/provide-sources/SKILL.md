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
2. Fall back to proper academic articles (journal papers, working
   papers) only when no good lay article covers the claim.
3. Always open each candidate source (WebFetch, or curl if blocked) and
   confirm it actually supports the specific claim as written. Never
   cite based on search-result snippets alone.

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
