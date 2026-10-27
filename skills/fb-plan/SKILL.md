---
name: fb-plan
description: >-
  Plan the Facebook week - what to post, which format (Reel, photo, text,
  Group post, Story, Live), when, and the Pages and Groups to engage with.
  Use when the user asks for a content calendar, "what should I post this
  week", a posting schedule, or a launch week plan for Facebook.
---

# fb-plan

One week, specific enough that each line can go straight to another skill.

## Inputs

Read `~/.claude/facebook/voice.md`, `swipe.md` (from `/fb-viral`) and `log.md`
(from `/fb-reel` / `/fb-audit`) if they exist. Ask for: goal this week (reach,
messages, sales, event), how many hours they have, and anything happening
(launch, holiday, local event, festival).

## Default mix (adjust to their capacity)

| per week | format | job |
|---|---|---|
| 2-3 | Reels | reach to non-followers |
| 1-2 | photo / album | proof, local, shareable |
| 1 | text post (story or opinion) | conversation with followers |
| 1-2 | Group posts | community, trust (`/fb-group`) |
| daily or most days | Stories | warm audience, messages |
| optional | Live | Q&A, launch, event (`/fb-live`) |

Fewer, better posts beat a daily schedule they can't keep. Three good posts a
week is a real plan.

## Timing

Use the Page's own Insights (when your followers are online) over any
generic "best time" chart. If no data, pick consistent slots and let
`/fb-audit` correct it in a month.

## Output

```
WEEK OF {date} · goal: messages
Mon  Reel   #22 Local Angle - "If you live in Patan, ..."   -> /fb-reel
Tue  Story  poll + reply MENU                               -> /fb-story
Wed  Photo  4-photo process, 6am prep                       -> /fb-photo
Thu  Group  answer in "Patan Foodies" (rules checked)        -> /fb-group
Fri  Reel   #2 Time Collapse - order to doorstep in 40 min  -> /fb-reel
Sat  Text   what we learned from 100 custom cakes           -> /fb-post

ENGAGE (15 min/day): 10 Pages and Groups to comment on    -> /fb-comment
  1. {Page}  why: same audience, not a competitor
  ...
```

Include each idea's one specific true thing (number, name, place). If an idea
doesn't have one yet, mark it `{{needs: your number}}`.

## Rules

- At most one link post per week unless they've confirmed no link limit on
  their Page (see `/fb-post`).
- Every item is original. No "share a meme from another Page" filler.
- If a post clearly outperforms, consider `/fb-boost` for it next week.
- Nothing is scheduled or posted by this skill.
