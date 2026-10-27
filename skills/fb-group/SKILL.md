---
name: fb-group
description: >-
  Run or post in Facebook Groups - start a Group, write its rules, welcome
  posts and weekly prompts, and write posts for other people's Groups that add
  value instead of reading as spam. Use when the user mentions Facebook Groups,
  community, "start a group", "post in a group", "group rules", "grow my
  group", or wants local word-of-mouth.
---

# fb-group

Groups are where Facebook still behaves like a community: people read, reply
and recommend. They are also where self-promotion gets people removed. Two
modes.

## Mode 1: the user's own Group

**Setup** (write all of it, the user creates it):

- **Name**: the member's identity or problem + place, not the brand.
  "Kathmandu Home Bakers" beats "SweetBakes Community".
- **Description**: who it's for, what happens here, what doesn't.
- **3 membership questions**: one qualifying, one about their goal, one for
  consent to rules.
- **5-8 rules**: short, specific, enforceable. Include the promo rule.
- **Welcome post**, pinned: how to introduce yourself, with the admin's own
  intro as the example.

**Weekly rhythm** (prompts the admin posts):

```
Mon  question about their week / goal
Wed  a useful post from the admin (tip, template, local info)
Fri  wins thread: members share one result
Sat  member spotlight or Q&A
```

Prompts must be answerable in one sentence. "What's one thing that..." beats
"Thoughts?". Admin replies to every early comment in the first hour.

## Mode 2: posting in someone else's Group

1. **Read the rules first.** Ask the user to paste them. If promo is banned,
   don't write promo in disguise.
2. Read the last 20 posts: what gets replies here?
3. Write a post that is **useful on its own**: an answer, a local tip, a
   specific question, a lesson with a number. No link unless the rules allow.
   The user's business appears only as context ("I run a bakery in Patan, so
   here's what we found...").
4. Never post the same text in multiple Groups. Facebook treats it as spam and
   members notice. Write a different version per Group, or skip it.

## Rules

- No engagement bait, no "comment INTERESTED", no fake questions to plant a
  recommendation.
- Never write posts pretending to be a customer, or sock-puppet replies.
- Run everything through `/fb-human` and lint with `../fb-post/post.py`.
- The user posts. This skill writes.
