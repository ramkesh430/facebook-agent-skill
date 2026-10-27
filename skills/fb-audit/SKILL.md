---
name: fb-audit
description: >-
  Post-mortem on what the user already posted on Facebook - rank posts by
  outlier multiple over their own median, weight shares and messages over
  views, and turn the pattern into next month's rules. Use when the user asks
  "what's working on my Page", "analyse my Facebook insights", "why did this
  post do well", "monthly review", or shares an Insights export.
---

# fb-audit

The user's own numbers beat any advice in this pack. This skill reads them.

## Collect

From Meta Business Suite > Insights > Content (or Professional Dashboard), the
last 30-90 days of posts. An export is best; screenshots work. Per post:
date, format, first line, reach, views, reactions, comments, **shares**,
link clicks, messages started (if shown), follows from post.

Also read `~/.claude/facebook/log.md` for which hook formula each post used.

## Rank on the right things

1. **Outlier multiple**: each post's reach divided by the median reach of the
   posts in this window. Same logic as `../fb-viral/swipe.py` (you can feed
   it a TSV with `account` set to the Page name and `metric` = reach).
2. **Shares per 1,000 reach**: the strongest distribution signal on Facebook.
3. **Messages / clicks per 1,000 reach**: the business signal.
4. Views alone are last. A post that got 50k views and no messages may be a
   worse post than one with 3k reach and 12 enquiries.

## Report

```
AUDIT · 42 posts · Aug 1 - Oct 27 · median reach 1,840
TOP BY MULTIPLE
  6.2x  Reel   "If you live in Patan..."      shares/1k 14.1  msgs 9
  4.8x  Photo  6am prep, 4 photos             shares/1k 8.0   msgs 3
BOTTOM
  0.2x  Link   "New blog post is up!"         shares/1k 0.4   msgs 0
PATTERNS
  - Local-named hooks: 4 of top 5
  - Link posts: median 0.3x (9 posts)
  - Shared-from-other-Pages: median 0.2x
RULES FOR NEXT MONTH
  1. Two Local Angle Reels a week.
  2. Links go in first comments only.
  3. Stop sharing other Pages' content.
```

Rules must come from the data. If the sample is under ~15 posts, say the
patterns are weak. Name confounders (a holiday, a boosted post, a Group share).

## Honest limits

Boosted/paid posts are separate; exclude or mark them. Facebook changes what
Insights shows; use what's there, don't fill gaps with guesses. Never invent a
number. Feed the rules to `/fb-plan`.
