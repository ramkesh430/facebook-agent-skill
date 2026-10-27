---
name: fb-post
description: >-
  Write a Facebook post or Reel caption - the line that survives the "See more"
  cut on mobile, the body, the single ask, links handled properly, no
  engagement bait - and lint it before it goes out. Use when the user says
  "write a Facebook post", "caption this for Facebook", "post this on my Page",
  "announce X on Facebook", or has a video or photo ready and needs the text.
---

# fb-post

One tool lives here and it runs:

```bash
python3 post.py post.txt
python3 post.py post.txt --keywords "home bakery,birthday cakes"
python3 post.py caption.txt --reel           # shorter length budget for video captions
```

It prints the post the way a phone prints it: about the first 150 characters
in a box, everything else behind **See more**. Desktop shows about 477. Read
the box before you read anything else you wrote.

## First, decide which job this post has

**Job A: the media already hooked them.** A Reel or a strong photo carries the
hook. The text's job is context, the ask, and the words people search. Keep it
short; 40-150 characters often wins.

**Job B: the text is the content.** A text post, a story, an opinion, a Group
post. Line one is the hook and works like a Reel hook: concrete, short, cut at
a cliff rather than mid-clause. This is where Facebook still rewards longer
writing, if each paragraph earns the next.

Say which job you're writing.

## The shape

```
Line 1      fits the ~150-char mobile window. Job A: context + ask.
            Job B: the hook. Never a greeting, a hashtag or "We are pleased".
Body        short paragraphs, one blank line between each.
The ask     one. A question only you could ask, a message, a booking. One.
Hashtags    0-3, or none. They label; they do not distribute on Facebook.
```

## Links, honestly

- Link posts usually reach fewer people than native posts, because they send
  people off Facebook.
- Since December 2025 Meta has been **testing a limit of two link posts a
  month** for some Pages and professional-mode profiles without Meta Verified.
  Links in comments, affiliate links and links to Meta's own apps were exempt
  in that test. Check whether your Page is in it before you plan a link-heavy week.
- So by default: the post stands alone and is worth reading without clicking,
  and the link goes in the **first comment**. Write that comment separately
  and say so in the receipt.

## Engagement bait - the one that gets posts demoted

Meta's content distribution guidelines demote posts that trade engagement:
react-bait ("like if"), vote-bait ("react ❤️ for A, 😮 for B"), share-bait
("share before it's deleted"), tag-bait ("tag a friend"), and comment-bait
("type YES"). `post.py` fails all five. Asking a real question about the
specific thing in the post is not bait. Asking for a reaction as a trade is.

## Rules

- **Original.** Meta reduces reach for accounts that mostly repost others'
  content. Commentary on a share is the minimum; your own post is better.
- **One ask.** `post.py` counts them.
- **Emoji as punctuation**, not bullets. Emoji bullet lists read as a template.
- **Local words.** If the user serves a place, name it. Facebook search and
  Groups are heavily local.
- **Alt text** for photos: write it. Screen readers and Facebook both read it.

## The loop

1. Decide Job A or B and say which.
2. Draft it in the user's voice (`~/.claude/facebook/voice.md`).
3. Run `/fb-human` on it.
4. Run `post.py` with the user's search terms. Fix every FAIL. Decide every
   WARN out loud.
5. Print the copy-ready block (and the first comment if there's a link), then:

```
POST READY
job:        B - the text is the content
visible:    132 of ~150 characters before See more
ask:        one, "message us BOOK"
links:      none in body; first comment has the menu link
hashtags:   1
bait:       none
linter:     READY
```

Nothing is posted. The user pastes it.
