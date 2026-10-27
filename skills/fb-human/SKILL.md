---
name: fb-human
description: >-
  The humanizer. Strip the AI fingerprint from any Facebook draft - invisible
  characters, em dashes, curly quotes, stock words, Facebook engagement-bait
  phrases - then score what is left on a five-check panel. Use before anything
  in this pack is shown to the user, and whenever they say "make this sound
  human", "this sounds like AI", "de-slop this", or paste a draft to clean.
---

# fb-human

Every other skill in this pack runs its draft through here before the user
sees it. Two tools, both real:

```bash
python3 humanize.py draft.txt --report       # clean it, list every change
python3 humanize.py draft.txt -o clean.txt   # write the clean version
python3 detect.py draft.txt                  # five-check score
python3 detect.py draft.txt clean.txt        # prove the delta
```

## What humanize.py fixes automatically

1. **Invisible characters.** Zero-width spaces and joiners, word joiners, BOMs,
   soft hyphens, bidi controls, Unicode tag characters, odd-width spaces.
2. **Typography.** Em dash -> comma, en dash -> hyphen, curly -> straight
   quotes, ellipsis -> three dots, bullets -> hyphens.
3. **The lexicon** in `slop.json`: about 190 stock words and phrases with
   plain replacements, longest match first, case preserved. The Facebook block
   catches what's specific here: "like and share", "tag a friend who needs
   this", "type amen", "1 like = 1 prayer", "copy and paste this", "we are
   pleased to inform", "our valued customers", "check out our page".

`slop.json` is meant to be edited. Add the words the user hates.

## What gets flagged, not fixed

Rewriting a sentence's shape needs judgement, so these come back to you:
"It's not just X, it's Y", "not only... but also", staged one-line reveals,
rule-of-three triads, fire/rocket/sparkle emoji, hashtag walls, Facebook
engagement bait, "stop scrolling", video preambles, emoji bullet lists, three
shouted words in a row, and press-release openers ("We are pleased to announce").

Rewrite every flag by hand in the user's voice, then re-run `detect.py`.

## The five checks

| check | what it measures |
|---|---|
| BURSTINESS | variation in sentence length; people vary, models don't |
| SPECIFICITY | numbers, names and places per 100 words |
| SLOP DENSITY | stock terms per 100 words |
| FINGERPRINT | invisible characters, em dashes, curly quotes |
| VOICE | structural tells; under 50 caps the total at 60 |

65+ is PASS. Show the user the score with the draft.

## Honest limits

These are local heuristics modelled on the signals public detectors look at.
They are not GPTZero, Originality, Copyleaks or Turnitin, they don't call them,
and they can't promise those verdicts. Nobody can honestly sell
"undetectable". The invisible-character pass removes a real, checkable
fingerprint; it is not a claim about defeating cryptographic watermarking.

The real goal isn't passing a detector. It's that the user's customers read the
post and hear the user.
