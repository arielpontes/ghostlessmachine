# ghostlessmachine

A bilingual (English/Portuguese) Hugo site migrated from WordPress, using the
[hugo-theme-stack](https://github.com/CaiJimmy/hugo-theme-stack).

## Article writing style

Articles present Ariel's original ideas and arguments, but they should also
be educational and informative without being too technical. When editing or
reviewing article drafts, favor adding references to specific events,
historical dates, and important individuals, and flag imprecise claims.

All article prose is governed by the `writing` skill
(`.claude/skills/writing/SKILL.md`). Load it BEFORE drafting, editing, or
rewriting any passage destined for an article, however small, and when
reviewing a draft, audit it against those same rules. Articles are
published primarily as podcast narrations, so every sentence must survive
being read aloud.

Two recurring pitfalls to check in every draft: an undefined audience
(passages addressing different camps without signaling the turn) and an
undefined goal (a conclusion that improvises a thesis never set up
earlier). The `writing` skill has the full checks.

## Python scripts

Python dependencies are managed with [uv](https://docs.astral.sh/uv/)
(`pyproject.toml` + `uv.lock`). Run scripts with
`uv run scripts/<name>.py` — never use pip or create virtualenvs manually.

## Hugo lessons

A `/hugo` skill at `.claude/skills/hugo/SKILL.md` collects lessons learned
during this migration (Stack theme quirks, WordPress export gotchas,
custom SCSS, multilingual content, cache busting).

**After fixing a Hugo issue, always offer to save the lessons learned to
the `/hugo` skill** so future sessions don't have to rediscover them.

## Markdown linting

Every markdown file delivered — written by hand OR produced by a generator
script (e.g. `scripts/import_medium.py`) — must pass `markdownlint`
(installed via Homebrew; repo config in `.markdownlint.yaml`). Before
finishing any task that creates or edits markdown, run:

```bash
markdownlint <changed files>
```

and fix every error. If a generator script produces non-compliant output,
fix the generator, not just the generated files.

## Known issues in old articles

Many old posts were damaged by the WordPress export: missing images,
leftover WordPress shortcodes, dead image URLs. `KNOWN-ISSUES.md` at the
repo root is the single backlog of these, one section per post. Whenever
you find a broken element in an article, add it there before finishing the
task, and remove entries you fix. `recovered-images/` holds images
recovered from web archives that have not yet been placed into posts.
