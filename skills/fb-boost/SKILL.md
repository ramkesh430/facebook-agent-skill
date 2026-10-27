---
name: fb-boost
description: >-
  Decide whether a Facebook post is worth boosting, then write the boost or
  ad - which post, goal, audience, budget sanity check, primary text and
  headline within the truncation limits - without ever spending money. Use
  when the user asks "should I boost this post", "write a Facebook ad",
  "how much should I spend", "who should I target", or "my boost didn't work".
---

# fb-boost

Boosting is the cheapest paid lever on Facebook and the easiest to waste money
on. This skill makes the decision and writes the copy. **It never spends,
never logs in to Ads Manager, never enters payment details.** The user sets up
and pays for the boost themselves.

Not financial advice. It's a checklist for spending a small budget carefully.

## Step 1: should this be boosted at all?

Boost a post only if it **already worked organically**. Run `/fb-audit` or ask
for the post's numbers. A good candidate:

- did 2x+ the Page's median reach, or got real shares and messages
- is still true and in stock (no expired dates or prices)
- has one clear action

Don't boost a post to "fix" weak reach. Paid reach on a post people ignore is
paying to be ignored.

## Step 2: one goal

Pick the goal Facebook offers that matches the one action:

| user wants | goal to choose |
|---|---|
| people to message | Messages (Messenger / WhatsApp) |
| visits to a website | Link clicks / traffic |
| more people to see a Reel | Engagement or video views |
| calls | Calls |
| local foot traffic | the local-awareness / store-visit option, if offered |

If the user doesn't know, it's almost always **Messages** for a small local business.

## Step 3: audience

- **Location first.** Radius around the shop, or the cities served. Most
  wasted boosts are shown to the wrong country.
- **Age range** only if the product truly excludes ages.
- Interests: few and specific, or none; Facebook's own delivery is often better
  than a stack of guessed interests.
- **Retargeting** beats strangers: people who engaged with the Page or watched
  its videos, when the user has enough of them.
- Never target or exclude by sensitive traits (health, religion, ethnicity,
  etc.). Meta restricts this, and housing, jobs, credit and politics have
  special rules. Flag it if the post touches those.

## Step 4: budget sanity check

- Start small and fixed: a few days, a daily amount the user can lose without
  stress. They name the number, not you.
- Decide **before** spending what result counts as "worked" (e.g. cost per
  message under {{their number}}).
- Stop or change after 3-4 days if it's not hitting that.

## Step 5: the copy

If the boost is an ad with new text, write it and lint it:

```bash
python3 ../fb-post/post.py ad.txt --mobile 125
```

- **Primary text**: the first ~125 characters are what show before "See
  more" in most ad placements. The offer and the "for whom" go there.
- **Headline**: ~40 characters. The benefit, not the brand name.
- One action, matched to the goal.
- No bait, no fake urgency, no before/after claims that break Meta's ad
  policies (health, weight loss, finance claims need extra care).

Run it through `/fb-human`.

## Output

```
BOOST PLAN
post:       "If you live in Patan..." Reel - 6.2x median, 9 messages organic
goal:       Messages
audience:   10 km around Patan, 22-55, no interests
budget:     {{daily amount}} x 4 days, set by you
success:    cost per message under {{your number}}
copy:       primary 118/125 chars · headline 31/40 · linter READY
```

The user creates and pays for the boost.
