---
name: fb-repurpose
description: >-
  Turn one long piece - a YouTube video, podcast, blog post, newsletter,
  workshop or Live - into a week of original Facebook Reels, photo posts, text
  posts and Group posts that each stand alone. Use when the user says
  "repurpose this for Facebook", "turn my video into posts", "cut this
  podcast into reels", or pastes a transcript.
---

# fb-repurpose

One long thing becomes 5-10 Facebook pieces, each complete on its own.

## The process

1. **Get the source.** Transcript, article text, or notes. If it's a video
   file, work from the transcript and timestamps.
2. **Mine it.** List every moment that has one specific true thing in it: a
   number, a story, a mistake, a strong opinion, a how-to step, a quote.
   Ignore the intro and the summary.
3. **Rank** the moments by how well they stand alone. A clip that needs the
   previous ten minutes to make sense is not a Reel.
4. **Assign a format** to each:

| moment | Facebook format |
|---|---|
| a story with an arc, under 60s | Reel (cut from the source, with a new 3s hook) |
| a strong opinion | text post, Job B (`/fb-post`) |
| a step-by-step | multi-photo post or Reel |
| a number or result | Reel hook or the first line of a text post |
| a question the audience asked | Group post (`/fb-group`) |
| a behind-the-scenes moment | Story (`/fb-story`) |

5. **Write each piece** with its skill. Every Reel gets its own hook scored by
   `../fb-reel/hookscore.py`. A clip from a long video almost never starts on
   a hook, so re-cut or re-record the first line.

## Rules

- **Each piece stands alone.** No "part 3", no "watch the full video to understand".
- **It must be the user's own content.** Repurposing their own work is fine.
  Reposting someone else's video, or a compilation of others' clips, is exactly
  what Meta's 2025 originality rules demote. Refuse that version and offer
  commentary instead.
- **Rewrite, don't copy-paste.** A blog paragraph is not a Facebook post.
- Run everything through `/fb-human`.

## Output

A table: piece, format, the hook/first line, source timestamp, skill to run
next. Then the first two pieces fully written.
