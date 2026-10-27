---
name: fb-dm
description: >-
  Write Facebook Messenger messages - the keyword delivery, the first reply to
  a new enquiry, instant replies and FAQs, the collab pitch, and at most two
  follow-ups - inside Meta's messaging rules. Use when the user asks for
  Messenger replies, "what do I message them", DM scripts, a partnership
  pitch, or auto-reply / FAQ setup for their Page.
---

# fb-dm

Messages are where Facebook turns into revenue for most small businesses. The
rule: they moved first, you answer like a person.

## The lines this skill won't cross

- **No cold mass messaging.** Pages can only message people who messaged them
  first. Meta's standard messaging window is 24 hours after the person's last
  message; outside it, only specific approved message types apply. Don't write
  workarounds.
- **Automation only through Meta's own tools** (Business Suite instant replies,
  FAQs, comment-to-message, away messages) or approved partners. No browser
  bots, no third-party "DM blasters". They break the Terms and get Pages
  restricted.
- Personal profiles: no unsolicited sales messages to friends or strangers.

## The messages

**1. Keyword delivery** (they commented or replied with the keyword)

```
Hi {name}, here's the {thing} you asked for: {thing or link}
{one line on how to use it}
{one question that's easy to answer, about their situation}
```

**2. First reply to a new enquiry** - answer the question in the first line.
Price questions get a price (or a range and what changes it). Then one
question that moves toward the next step.

**3. Instant reply + FAQs (Page setup)** - an instant reply that sets the
response time honestly, and 3-5 FAQ answers (price, location/delivery, hours,
how to book). Written in the user's voice, each under 300 characters.

**4. Collab / partnership pitch** - only to accounts with a reason: shared
audience, local overlap. Three short paragraphs: why them (specific), the idea
(specific), the easy next step. No attachments in the first message.

**5. Follow-ups: two, max.**
- Follow-up 1 after 2-3 days (and only inside allowed messaging rules): add one
  new useful thing, not "just checking in".
- Follow-up 2 a week later: a clean close ("I'll leave it here, the offer's
  open whenever").
Then stop.

## Rules

- Short. Messenger is a chat, not an email. Under 500 characters usually.
- Use their name and what they actually said.
- Never invent prices, stock, discounts or deadlines. Unknown -> `{{price}}`.
- Run everything through `/fb-human`. The user sends it.
