---
name: fb-live
description: >-
  Plan and script a Facebook Live - the announcement post, the run-of-show
  with timed segments, the opening 60 seconds, comment prompts, the offer,
  and the replay clips afterwards. Use when the user wants to go live on
  Facebook, host a Q&A, launch, sale, demo, workshop or event stream, or asks
  "what do I say on my live".
---

# fb-live

A Live is the one Facebook format where the audience talks back in real time.
Most Lives fail in the first minute (nobody's there yet) and the last five
(no clear ask). This skill plans both.

## Before

Read `~/.claude/facebook/voice.md`. Ask:

- **Why this Live?** Q&A, launch, sale, demo, tutorial, interview, event.
- **One outcome**: messages, orders, Group joins, sign-ups. One.
- **Length**: 20-45 minutes is the working range for most small Pages.
- **Where**: Page, profile, or a Group (Group Lives reach members who care most).
- **Guest?** Get their name, handle and one story they'll tell.

## The announcement

Write with `/fb-post`: what, when (date, time, timezone), why it's worth
turning up for (one specific thing they'll get), and the one action:
"Tap **Get reminder**" if the user schedules the Live in advance, or "Comment
your question now and I'll answer it live". Post it 1-3 days before, plus a
Story on the day (`/fb-story`).

## Run of show

```
0:00-1:00   OPEN       start talking immediately. Say what they'll get and
                       when. Don't wait for people; the replay audience is
                       bigger than the live one.
1:00-3:00   HOOK       the most interesting thing first: the result, the
                       reveal, the strongest answer.
3:00-...    SEGMENTS   5-8 minutes each, each with one prompt for comments.
                       Re-state the topic every segment for late joiners.
LAST 5 MIN  THE ASK    the one action, said twice, with how to do it.
LAST 30s    CLOSE      what's next and when.
```

For each segment: the talking points (bullets, not a script), one prop or
screen to show, and one comment prompt that's a real question ("What's your
biggest problem with X?"), never "type 1 if you can hear me".

## Comment handling

- Greet people **by name** when they comment; it's the reason to watch live.
- Prepare 5 answers to the questions you expect.
- A co-host or helper pins the key comment (the offer, the link) and hides spam.
- Price questions: answer publicly if the price is fixed; otherwise move to
  Messenger (`/fb-dm`).

## After

1. Edit the replay title and description (`/fb-post`, Job A).
2. Cut 3-5 clips of the best moments into Reels with new hooks
   (`/fb-repurpose`, `/fb-reel`).
3. Reply to every comment on the replay (`/fb-reply`).
4. Log it in `~/.claude/facebook/log.md` for `/fb-audit`.

## Rules

- No engagement bait ("share this live to win"), unless it's a real giveaway
  that follows Meta's promotion rules and local law; even then, sharing to
  enter is not allowed on Facebook. Say so.
- Never invent a discount, deadline or stock count. `{{your number}}`.
- The user goes live. This skill plans and writes.
