# The Facebook agent skill

[![test](https://github.com/ramkesh430/facebook-agent-skill/actions/workflows/test.yml/badge.svg)](https://github.com/ramkesh430/facebook-agent-skill/actions/workflows/test.yml)

Sixteen Claude skills that run a Facebook Page or profile. Free, MIT, no
signup, no API key, nothing to connect.

One writes your Reels off 24 hook formulas and scores the hook before you shoot
it. One finds the posts that are actually working in your niche and ranks them
by how far each beat its own account. One writes the post and shows you
exactly what a phone shows before **See more**, then fails it if it contains
engagement bait Meta demotes. One scores your Page out of 100. One runs your
Group. One plans a Live, one decides whether a post is worth boosting, and one
plans the week.

And one is the humanizer: it strips em dashes, stock vocabulary, "like and
share" bait and invisible characters out of a draft, then scores what's left
on a five-check panel before you see it.

**Nothing gets posted until you say yes. These skills write. You post.**

> A Facebook adaptation of [instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill)
> by Jake Schincariol (MIT). Same idea, rebuilt for how Facebook works:
> Groups, Messenger, Pages, link limits, engagement-bait rules and an older,
> more local audience. The Python tools here are rewritten from scratch.

## Install

One step, in Claude Code 2.1.275 or later:

```
/plugin install facebook-agent --marketplace ramkesh430/facebook-agent-skill
```

On older versions, add the marketplace first:

```
/plugin marketplace add ramkesh430/facebook-agent-skill
/plugin install facebook-agent
```

Or copy the skills by hand:

```bash
git clone https://github.com/ramkesh430/facebook-agent-skill.git
cp -r facebook-agent-skill/skills/fb-* ~/.claude/skills/
```

Project-local: copy the folders into your repo's `.claude/skills/`. Keep the
`fb-*` folders side by side; `swipe.py` borrows the hook scorer from `fb-reel`.

No Claude Code? Paste any single `SKILL.md` at the top of a chat and it runs as
a mode. You lose the Python tools, but the rest works.

Then spend ten minutes on `templates/voice.md`. Copy it to
`~/.claude/facebook/voice.md` and fill it in, or send Claude three of your own
posts and say "write my voice.md from these". Every skill reads it.

## The sixteen

| command | what it does |
|---|---|
| `/fb-reel` | One idea into a Reel. Three hooks from 24 formulas, scored, then the script, on-screen text and a timed beat sheet. |
| `/fb-viral` | Finds what's working in your niche, ranks it by multiple over each account's own median, names the formula, writes the swipe file. |
| `/fb-post` | Posts and captions, linted. Shows the ~150 characters mobile shows before See more. Fails engagement bait in English and Nepali. Handles links. |
| `/fb-photo` | Single photos, multi-photo posts and albums: which image leads, order, overlays, sizes, alt text. |
| `/fb-story` | The daily Story sequence, which sticker does which job, and the Messenger reply it starts. |
| `/fb-page` | Scores your Page on a 14-part, 100-point rubric, then rewrites in fix-first order. |
| `/fb-group` | Run your own Group (name, rules, welcome, weekly prompts) or post in others' without getting removed. |
| `/fb-live` | A Live from announcement to replay clips: run-of-show, the first 60 seconds, comment prompts, the ask. |
| `/fb-boost` | Whether a post is worth boosting, the goal, audience and copy. Never spends; you set up and pay. |
| `/fb-plan` | The week: what, which format, when, and the Pages and Groups to engage with. |
| `/fb-human` | The humanizer. Two scripts that actually run. |
| `/fb-comment` | Comments on other people's posts. Nine types, picked by what the post is. |
| `/fb-reply` | The thread under your own post: keyword / lead / complaint / question / substance / support / noise. |
| `/fb-dm` | Messenger: keyword delivery, first reply, instant replies and FAQs, collab pitch, two follow-ups. Inside Meta's rules. |
| `/fb-repurpose` | One video, podcast or blog into a week of standalone Facebook posts. |
| `/fb-audit` | Post-mortem on your own Insights. Ranks by outlier multiple and shares per reach, not views. |

## The tools that actually run

Standard library Python. No dependencies, no network, nothing uploaded.

```bash
python3 skills/fb-reel/hookscore.py hooks.txt          # rank hook options
python3 skills/fb-reel/beats.py script.txt --target 30 # time it before you shoot
python3 skills/fb-post/post.py post.txt --keywords "birthday cakes,lalitpur"
python3 skills/fb-human/humanize.py draft.txt --report # clean it, show changes
python3 skills/fb-human/detect.py before.txt after.txt # score and prove the delta
python3 skills/fb-viral/swipe.py captured.tsv --out ~/.claude/facebook/swipe.md
```

Try them on the sample files in `examples/`, and run the whole test suite
(49 checks, standard library only):

```bash
python3 tests/run_tests.py
```

### Nepali support

`post.py`, `hookscore.py` and the humanizer also catch engagement bait written
in Nepali, romanized or Devanagari: "like garnus", "bhane like", "sathi lai tag
garnus", "'ho' lekhnus", "शेयर गर्नुहोस्". Greetings like "Namaste sathi haru"
are treated as greetings. Add your own phrases to `slop.json`.

`post.py` on a typical "business announcement" post:

```
WHAT THE MOBILE FEED SHOWS
+--------------------------------------------------------+
| Hello everyone! 🌟 We are pleased to announce our new   |
| birthday cake menu, crafted with love for our valued   |
| customers in Kathmandu and beyond, so please           |
+------------------------------------------ ... See more +

WARN  FIRST LINE       159 characters, so mobile cuts it at 150 mid-thought
FAIL  ENGAGEMENT BAIT  share-bait ("Share before"); tag-bait ("tag a friend"). Meta demotes this
WARN  LINKS            1 link(s) in the body. Consider the first comment instead...
FAIL  HASHTAGS         6 tags. A hashtag wall reads as spam on Facebook
WARN  ONE ASK          2 different asks. Two asks is the same as none
VERDICT FIX 2 FAIL(S) · 4 warning(s) to decide on
```

## Facebook facts this pack is built on

Platform rules move. These were checked in October 2026; if Facebook is doing
something different when you read this, Facebook is right.

- **All videos are Reels** (rolled out from June 2025), with the old length
  limits removed. Meta suggests 10-30s for reach, longer for depth.
- **Unoriginal content is demoted** (announced July 2025): accounts that
  repeatedly repost others' videos, photos or text without meaningful
  additions lose reach and monetization. Commentary and reaction are fine.
- **Link post limit test** (December 2025): some Pages and professional-mode
  profiles without Meta Verified were limited to two link posts a month.
  Links in comments, affiliate links and Meta links were exempt.
- **Engagement bait is demoted** under Meta's content distribution guidelines:
  react-, vote-, share-, tag- and comment-bait.
- **See more** cuts at roughly 150 characters on mobile and ~477 on desktop.
  These vary by device; `post.py` lets you change them.
- **Messenger**: Pages can message people who messaged first, within Meta's
  messaging window. Automation only via Meta's tools or approved partners.

## The fine print

**These skills don't post to Facebook.** Meta's Graph API can publish to Pages,
but it needs a developer app, permissions, tokens and review, which a skill
can't hand you. Browser bots and third-party "auto-poster / DM blaster" tools
break Meta's Terms and get accounts restricted. So every skill ends with a
copy-ready block, and you post it.

**`/fb-viral` reads, it doesn't scrape.** A dozen accounts, at human speed,
with you driving your own browser. It never asks for your password.

**The detection checks are local heuristics**, not GPTZero, Originality or any
other service. They measure the same kinds of signals; they can't promise
those verdicts. Nobody can honestly sell "undetectable".

**The hook scorer catches weak hooks; it doesn't pick winners** between two
decent ones. That's decided by your face, edit, audio and who Facebook shows it
to. Kill the obviously weak hooks, then trust your own Insights.

**Nothing here fabricates.** If a draft needs a number you haven't given, it
comes back with `{{your number}}` and a flag.

## Files

```
skills/fb-reel/hooks.json      24 hook formulas + dealbreakers, with match regexes
skills/fb-reel/hookscore.py    five-property hook panel
skills/fb-reel/beats.py        script -> timed beat sheet
skills/fb-post/post.py         See-more preview and post linter
skills/fb-human/slop.json      ~195 terms, 20 invisible classes, 19 structural tells
skills/fb-human/humanize.py    the three cleaning passes
skills/fb-human/detect.py      the five-check panel
skills/fb-viral/swipe.py       outlier ranking and formula classification
skills/fb-page/rubric.json     the 100-point Page score
examples/                      sample hooks, script, posts (incl. Nepali), captured.tsv
tests/run_tests.py             end-to-end tests for every tool (run by GitHub Actions)
templates/voice.md             your voice profile. Fill this in first.
```

## License

MIT. Take it, change it, ship it. See `LICENSE`.
