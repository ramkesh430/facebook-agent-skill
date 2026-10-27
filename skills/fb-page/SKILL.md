---
name: fb-page
description: >-
  Score a Facebook Page or professional-mode profile out of 100 on a 14-part
  rubric, then rewrite what lost points in fix-first order - name, intro, about,
  cover, action button, pinned post, contact details. Use when the user says
  "audit my Facebook page", "fix my page", "write my page bio", "why isn't my
  page getting messages", or shares a Page link or screenshots.
---

# fb-page

Scores the Page against `rubric.json` (14 parts, 100 points), then rewrites
the parts that lost the most points first.

## Collect

Ask for the Page link and screenshots of: the top of the Page on mobile, the
intro/about, the pinned post, and (if they'll share) the inbox response stats.
If the browser is available and the Page is public, read it, but never log in
as the user. Also ask: who is the Page for, and what's the one action a
visitor should take?

## Score

For each part in `rubric.json`: full points, half, or zero, with one line of
evidence. Total it and band it (STRONG 85+, OK 65+, WEAK).

```
PAGE SCORE  61 / 100  WEAK
  intro           0/12  "Welcome to our official page!" - no audience, no promise
  action button   4/8   "Learn more" -> homepage; visitors want to message
  recent          5/10  last post 19 days ago; 6 of last 10 are shares from other Pages
  ...
```

## Fix, in order of points lost

For each fix, give the copy-ready replacement:

- **Name**: what people would search. Brand + what/where if the brand says nothing.
- **Intro (101 chars)**: for whom + what they get + one proof. Three options.
- **About / description (155-255 chars)**: the search words, in sentences.
- **Cover**: a brief for the image and its one line of text; mobile-safe.
- **Action button**: one, matched to the one action.
- **Pinned post**: write it with `/fb-post` - what you do, proof, how to start.
- **Contact**: list exactly what's missing or out of date.
- **Messages**: instant reply and 3-5 FAQ answers in the user's voice.

Run every piece of copy through `/fb-human`.

## Rules

- Never invent reviews, numbers, awards or customers. Use `{{your number}}`.
- Don't recommend buying followers, likes or reviews, or review-for-discount
  swaps; they break Meta's rules and erode trust.
- The user makes the changes. This skill writes them.
