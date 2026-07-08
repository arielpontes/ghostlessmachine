# ghostlessmachine

A bilingual (English/Portuguese) Hugo site migrated from WordPress, using the
[hugo-theme-stack](https://github.com/CaiJimmy/hugo-theme-stack).

## Hugo lessons

A `/hugo` skill at `.claude/skills/hugo/SKILL.md` collects lessons learned
during this migration (Stack theme quirks, WordPress export gotchas,
custom SCSS, multilingual content, cache busting).

**After fixing a Hugo issue, always offer to save the lessons learned to
the `/hugo` skill** so future sessions don't have to rediscover them.

## Broken images from the WordPress migration (paused, not abandoned)

Some old posts lost images during the WordPress export. An effort to recover
them (from web archives etc.) was paused in mid-2026; a few images were
recovered, most were not. If a post with missing images ever needs fixing,
these are the working files:

- `missing-images.txt` — per-post list of image filenames still missing.
- `recovered-images/` — images recovered but not yet placed into posts.
- `content/page/review/index.md` — a `draft: true` page linking every
  affected post. Not built in production; view it with `hugo server -D`
  at `/review/`.

Keep these files in the repo, and keep the review page a draft so it never
surfaces on the live site.
