---
name: fb-viral
description: >-
  Research what is actually working on Facebook in the user's niche - Pages,
  creators and Groups - rank each post by how far it beat its own account,
  name the hook formula, and write a swipe file the other skills read. Use when
  the user asks "what's working on Facebook in my niche", "find viral posts",
  "research competitors' Pages", "why is their Page growing", or wants ideas
  grounded in evidence.
---

# fb-viral

Finds the posts that are outperforming in the user's niche and explains why.
Writes `~/.claude/facebook/swipe.md`, which `/fb-reel`, `/fb-post` and
`/fb-plan` read.

```bash
python3 swipe.py captured.tsv --out ~/.claude/facebook/swipe.md
```

## The rule that makes this useful

**Raw numbers are not evidence.** A 2M-follower Page doing 400k views had a
quiet day. A 4k-follower Page doing 400k found something. Rank by the
**multiple over each account's own median**, never by raw views.

## How to collect (reading, not scraping)

1. Ask for the niche, the location (Facebook is local; "bakeries in Kathmandu"
   beats "bakeries"), and 3-5 accounts they already know.
2. Find 8-12 accounts total: the user's list, Facebook search for the niche
   terms, Pages that show up under "Related Pages", and active public Groups.
3. For each account, read the last 10-15 posts **at human speed in the user's
   own browser, with the user driving**. Capture into a TSV:

```
account	metric	followers	format	hook	url
```

   - `metric`: views for Reels; reactions + comments + shares for other posts.
     Be consistent within a file. Shares count most on Facebook: if visible,
     note them.
   - `hook`: the first line of text, or the first spoken sentence.
   - `format`: reel, photo, text, link, album, live, group.
4. Run `swipe.py`. It needs 3+ posts per account for a real median; otherwise
   it falls back to followers x 0.10 and says so.

Never ask for a password, never log in as the user, never run a crawler or
bulk export. Automated collection breaks Meta's Terms and gets accounts
restricted. If the user wants more data, they collect more by hand.

## Reading the output

For each post at 3x or more over its baseline, write down:

- the hook formula (from `../fb-reel/hooks.json`) or "none" - many winners are
  just a good photo of a real moment
- the format and length
- the **share trigger**: why would someone send this to a friend or post it to
  a Group? Useful, funny, local, identity ("this is so us"), or outrage. Name it.
- what the comments are actually saying

Then the TOP vs BOTTOM third comparison: what separates them in hook score,
specificity, length and format.

## The swipe file

Write `~/.claude/facebook/swipe.md` with: the ranked table, 5-10 named patterns
("local-specific how-to Reels under 30s outperform 4x"), formats to stop
doing, and 10 post ideas that apply the patterns to the user's own proof.
Never copy a post. Patterns are fair game; the post is someone else's work, and
Meta now demotes unoriginal reposts.

## Measurement honesty

A text-based hook score catches weak hooks well and does not pick winners
between two decent hooks; that's decided by the visual, the edit, the timing
and who Facebook shows it to. Say this when you present results.
