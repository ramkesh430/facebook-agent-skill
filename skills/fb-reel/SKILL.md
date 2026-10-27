---
name: fb-reel
description: >-
  Write a Facebook Reel or video from a raw idea - hook options off 24 formulas,
  the spoken script, the on-screen text, and a timed beat sheet - in the user's
  own voice and scored before they shoot it. Use whenever the user wants a
  Facebook Reel, a Facebook video script, a hook, a voiceover, "make a reel
  about X", or is about to record and does not have the first line yet.
---

# fb-reel

Turns one raw idea into a Facebook Reel that somebody finishes.

Since June 2025 every new video uploaded to Facebook is a Reel, and the old
length and format limits are gone. That does not mean long is good. It means
the first three seconds decide everything for every video you post.

Two tools live in this folder and both actually run. Use them.

```bash
python3 hookscore.py hooks.txt              # rank your hook options
python3 hookscore.py --hook "one line"      # score a single one
python3 beats.py script.txt --target 30     # timed beat sheet before you shoot
python3 beats.py script.txt --wpm 150       # at your own pace
```

## Before you write

1. Read `~/.claude/facebook/voice.md` if it exists. If it doesn't, ask for
   **three of their own videos or posts**, infer the voice, and write the file
   from `templates/voice.md`. A script in the wrong voice is unusable, because
   they have to say it out loud.
2. Read `hooks.json`. 24 formulas, each with a template, a filled example, the
   on-screen version, what it's for, and how it gets ruined. Two are there for
   Facebook specifically: **Local Angle** and **Family Truth**. Facebook's
   audience is older, more local and more family-connected than Instagram's or
   TikTok's, and hooks that name a place or a parent travel further here.
3. If the idea is thin, don't pad it. Ask one batched question: what happened,
   to whom, and what did it cost or return. A Reel needs one specific true thing.
4. If `~/.claude/facebook/swipe.md` exists (written by `/fb-viral`), read it.
   It is the user's own evidence about what's working in their niche. It beats
   the defaults here.

## The shape

```
0:00 - 0:03   HOOK        the claim. Spoken line and on-screen line, written
                          separately. Motion in frame one, not a static face.
0:03 - 0:08   THE STAKE   why this matters to the person watching. One line.
0:08 - ...    THE BODY    one idea per beat; the frame changes every beat.
LAST 3s       THE PAYOFF  deliver what the hook promised, then the single ask.
LAST LINE     THE LOOP    echo one word from the hook so the replay lands clean.
```

Length: Meta's own guidance is 10-30 seconds for reach and 30 seconds to 3
minutes or longer for deeper engagement. Match length to the goal. A tutorial
can run 90 seconds if every beat earns the next; an opinion should be 20.

## The loop

1. **Pick three hooks**, from three different formulas. Write the spoken line
   and the on-screen line for each.
2. **Score them** with `hookscore.py`. Show the ranking. If the top is under 50
   you don't have the hook yet; editing won't fix it.
3. **Write the script** on the winner. Plain spoken language, contractions,
   short lines, nothing they'd have to rehearse. One beat per line.
4. **Time it** with `beats.py --target {length}`. Fix every flag: a hook over
   ~3 seconds, a beat over 4, three beats with nothing concrete, no loop.
5. **Humanize it** with `/fb-human`. A written-sounding line is obvious the
   moment someone says it out loud.
6. **Print the block**: the script in a fenced block, the on-screen text as a
   separate timed list, then:

```
REEL READY
hook:       #22 Local Angle, scored 82 STRONG
length:     27.9s across 8 beats at 165 wpm
on-screen:  6 cards
humanizer:  3 artefacts stripped, human score 84 PASS
caption:    run /fb-post --reel next

Reply "yes" to log it, or tell me what to change.
```

7. **Never publish.** On "yes", append to `~/.claude/facebook/log.md` with the
   date, format, hook formula and first line, so `/fb-audit` has a history.

## On-screen text is a separate script

- **Six words or fewer per card.** Read at arm's length by someone not listening yet.
- **Hook card up at frame 1.**
- **Safe zone on 1080x1920:** keep text out of the top ~250px and the bottom
  ~400px, and clear of the right-hand action rail. Caption, name and buttons
  sit on top of everything outside that box.
- **Burn in captions.** Most Facebook video starts muted.
- **Write for the 45+ viewer too:** larger text, higher contrast, slower cuts
  than you'd use on TikTok.

## Rules

- **One idea per Reel.** Two ideas = two Reels. Say so.
- **Numbers over adjectives.** If there's no number, ask; don't write around it.
- **Cut the intro.** No greeting, no "in this video", no logo sting.
- **One ask at the end.** Comment a word, send a message, or follow. One.
- **Original only.** Since July 2025 Meta cuts reach and monetization for
  accounts that repost others' videos without meaningful additions. Never
  script a reupload of someone else's clip. Reaction and commentary are fine
  when the commentary is the content.
- **No engagement bait.** "Like if", "share if", "tag a friend", "type YES"
  are demoted by Meta's distribution guidelines. `hookscore.py` treats them as
  dealbreakers.
- **Never fabricate.** No invented metrics, clients or outcomes. Unknown number
  -> `{{your number}}` and a flag.
