---
name: draft-review
description: >-
  Use when the user asks for a review of a blog article draft. Audits the
  draft against named human standards (Orwell, Zinsser, Williams, Pryor,
  Rapoport) plus an AI-slop deny-list. High lenience: the goal is to
  polish Ariel's casual/nerdy voice, never to replace it. Reports findings
  in chat; edits the draft only when asked.
---

# Draft review

Review a blog article draft against the named standards below. This is
an audit, not an exercise of taste: every finding must cite the rule it
violates by name and quote the offending passage. Anything that cannot
be tied to a rule does not get reported.

Report findings in the chat response only. Do not edit the draft unless
the user asks for fixes to be applied.

## Voice and lenience (governs everything below)

This is a personal blog, not an academic journal or news publication.
The author's voice is casual/nerdy: informal structures borrowed from
spoken language, mixed with technical jargon. That mix is intentional
and is never a finding by itself.

- Apply a high threshold to every check below. When in doubt whether a
  passage crosses a line, don't flag it.
- Flag register only when it is overdone: the contrast between casual
  and technical within a passage is so extreme it's jarring, a sentence
  is genuinely convoluted, or a passage reads amateurish rather than
  merely informal.
- Any suggested rewrite must sound like the author, not like polished
  generic prose: plain and factual, no aphorisms or slogan-like
  phrasing, keeping his casual/nerdy register. If the only fix you can
  think of sounds like AI, report the problem without a rewrite.
- Jargon is part of the voice. Never flag jargon as such; flag it only
  under the Pinker check (load-bearing term the reader can neither
  infer nor look up from context).

## Prose checks

- **Orwell 1** (Politics and the English Language): metaphors, similes
  and figures of speech you are used to seeing in print; ready-made
  phrases that assemble themselves.
- **Orwell 2/3 + Zinsser** (On Writing Well): clutter — words that do
  no work, long words where short ones do, weak qualifiers ("a bit",
  "sort of"), pointless intensifiers, warm-up paragraphs that delay the
  point.
- **Orwell 4**: passive voice where the active would be stronger and
  the agent matters.
- **Williams** (Style: Lessons in Clarity and Grace): sentences whose
  grammatical subject is not the main character of the sentence;
  actions buried in nominalizations instead of verbs; new information
  placed before old; sentences that fizzle instead of ending on the
  stress point.
- **Pinker** (The Sense of Style): curse of knowledge — a load-bearing
  term or assumption the intended reader cannot infer from context and
  was never given.

## Argument checks

- **Pryor** (Guidelines on Writing a Philosophy Paper): key terms used
  before being defined; obvious objections never anticipated;
  overclaiming ("proves", "shows" where the argument only suggests);
  more than one thesis competing for the essay.
- **Rapoport/Dennett** (Intuition Pumps): opposing positions criticized
  without being stated in a form their proponents would accept.

## House style (mechanics)

Unlike the checks above, these are objective conventions, not quality
judgments — the lenience rule doesn't apply, but only deviations from
the choices below are findings, never the choices themselves:

- American spelling; the Chicago Manual of Style is the tiebreaker for
  anything not listed here.
- Deliberate deviation from Chicago: logical (British) quote
  punctuation — periods and commas go inside the closing quotation
  mark only when they are part of the quote.
- Serial (Oxford) comma.
- Book titles in italics; quotation marks for shorter works (articles,
  chapters, songs).
- Citations and blockquote attributions follow the formats in the
  `provide-sources` skill ("Citing books"); flag any other style
  (author-date parentheticals, plain-text titles, en-dash
  attributions) as inconsistent.
- Em dashes only in blockquote attributions; in prose prefer commas,
  periods, or parentheses.

## AI-slop deny-list

These are always flagged, with no lenience — they are impostor voice,
not the author's voice:

- "It's not X, it's Y" and similar contrast-for-drama constructions.
- Rule-of-three triplets used as rhythm rather than content.
- Stock AI vocabulary: delve, tapestry, testament, underscore,
  landscape, crucial, pivotal, foster, leverage, and kin.
- Hedge-everything conclusions that retreat from the essay's own claim.
- Symmetric aphoristic closers and slogan-like phrasing.
- Em-dash-heavy sentence rhythm sustained across paragraphs.

## Report format

For each finding: the quoted passage, the rule violated (by name), one
sentence on why, and — optionally — a rewrite in the author's voice.
Order findings worst-first. End with a one-paragraph overall verdict on
whether the draft is ready to publish.
