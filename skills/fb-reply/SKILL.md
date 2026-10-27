---
name: fb-reply
description: >-
  Handle the comments under the user's own Facebook post - sort them into
  keyword / lead / substance / question / support / complaint / noise, then
  write replies in that order. Use when the user pastes their comments, says
  "help me reply to these", "how do I answer this comment", or has a post
  taking off.
---

# fb-reply

The thread under a post is part of the post. Replies keep it alive and turn
commenters into conversations.

## Sort first

Ask for the comments (pasted or a screenshot). Sort every one:

| bucket | what it is | priority |
|---|---|---|
| KEYWORD | they typed the word the post asked for | 1 - send what was promised |
| LEAD | price question, "do you deliver to...", "how do I book" | 1 |
| COMPLAINT | a problem with the product or service | 1 - publicly, calmly |
| QUESTION | about the content | 2 |
| SUBSTANCE | adds a point or a story | 2 |
| SUPPORT | "love this", tags, emoji | 3 - short reply or a reaction |
| NOISE / SPAM | scams, links, bots, abuse | hide or delete; never argue |

## Write replies in that order

- **KEYWORD / LEAD**: short public reply ("Sent you a message, Sita!") then the
  private message via `/fb-dm`. On Pages, Meta's "comment to message"
  automations can do the keyword part through Business Suite. Never put prices
  that change daily in a public comment if they belong in a message.
- **COMPLAINT**: acknowledge, own what's yours, move details to Messenger,
  come back and say it's resolved. Never delete a fair complaint.
- **QUESTION**: answer it fully in the reply. Others will read it.
- **SUBSTANCE**: respond to their point specifically; a question back keeps the thread going.
- **SUPPORT**: a few words using their name, or just a reaction. Don't
  paste the same "Thank you so much! ❤️" 40 times.

## Rules

- Use their first name. Vary every reply; identical replies read as a bot.
- 1-2 sentences, in the user's voice. Run through `/fb-human`.
- Never invent a policy, discount or promise the user hasn't confirmed.
- The user posts the replies.

## Output

A table: commenter, bucket, reply. Then a one-line summary of leads to follow
up in Messenger.
