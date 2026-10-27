#!/usr/bin/env python3
"""beats.py - turn a Reel script into a timed beat sheet before you shoot it.

One non-empty line of the script = one beat. Each beat is timed at your
speaking pace, stacked into timecodes, and checked for the things that kill a
Facebook Reel in the edit:

  - a hook that runs past about 3 seconds (flagged over 3.5s)
  - any beat over 4 seconds (a static frame is where people leave)
  - three beats in a row with nothing concrete in them
  - no loop: the last beat never echoes a word from the hook
  - too far over or under your target length

Usage:
  python3 beats.py script.txt
  python3 beats.py script.txt --target 30 --wpm 160

Standard library only.
"""
import argparse
import re
import sys

STOP = set((
    "the a an and or but so to of in on at for with is are was were be been it "
    "this that these those i you we they he she my your our their me us them "
    "not no do does did have has had just very really can will would could "
    "should here there what when how why who then than from up out about now"
).split())
NUMBER_WORDS = set((
    "one two three four five six seven eight nine ten eleven twelve fifteen "
    "twenty thirty forty fifty hundred thousand million lakh crore half double"
).split())


def syllables(word):
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 1
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee")):
        n -= 1
    return max(1, n)


def spoken_words(line):
    toks = re.findall(r"[A-Za-z']+|\d[\d,.]*|[$%]", line)
    n = 0.0
    for t in toks:
        if re.match(r"\d", t):
            # digits are said as words: "18,000" is "eighteen thousand"
            digits = len(re.sub(r"\D", "", t))
            n += 1 + max(0, digits - 3) * 0.5
        elif t in "$%":
            n += 0.5
        else:
            # long words take longer to say
            n += 1 + max(0, syllables(t) - 2) * 0.15
    return n


def is_concrete(line):
    if re.search(r"\d", line):
        return True
    low = re.findall(r"[a-z]+", line.lower())
    if any(t in NUMBER_WORDS for t in low):
        return True
    toks = re.findall(r"[A-Za-z][A-Za-z']*", line)
    return any(re.match(r"[A-Z][a-z]{2,}$", t) for t in toks[1:])


def content_words(line):
    return {t for t in re.findall(r"[a-z0-9$]+", line.lower().replace(",", ""))
            if t not in STOP and len(t) > 2}


def tc(sec):
    m = int(sec // 60)
    return f"{m}:{sec - 60 * m:04.1f}"


def main():
    ap = argparse.ArgumentParser(description="Timed beat sheet for a Reel script.")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--target", type=float, default=30.0, help="target seconds")
    ap.add_argument("--wpm", type=float, default=165.0, help="your speaking pace")
    ap.add_argument("--pause", type=float, default=0.15, help="gap between beats")
    a = ap.parse_args()

    src = open(a.file, encoding="utf-8").read() if a.file else sys.stdin.read()
    beats = [l.strip() for l in src.splitlines() if l.strip() and not l.startswith("#")]
    if not beats:
        sys.exit("empty script")

    total_words = sum(len(re.findall(r"\S+", b)) for b in beats)
    rows, t = [], 0.0
    for i, b in enumerate(beats):
        d = spoken_words(b) / a.wpm * 60 + a.pause
        rows.append((t, d, b))
        t += d
    total = t

    print(f"BEAT SHEET · {total_words} words · ~{total:.1f}s at {a.wpm:.0f} wpm · target {a.target:.1f}s")
    print("=" * 74)
    flags = []
    run = 0
    for i, (start, d, b) in enumerate(rows):
        if i == 0:
            label = "HOOK"
        elif i == len(rows) - 1:
            label = "CTA"
        elif d > 4:
            label = "MID"
        else:
            label = ""
        text = b if len(b) <= 48 else b[:45] + "..."
        print(f"{tc(start):>7} {d:5.1f}s {label:<5} {text}")
        if i == 0 and d > 3.5:
            print(f"{'':15}^ hook runs {d:.1f}s")
            flags.append(f"The hook runs {d:.1f}s. Cut it to about 3s; the scroll decision is made by then.")
        elif d > 4:
            print(f"{'':15}^ {d:.1f}s on one beat")
            flags.append(f"Beat {i + 1} runs past 4s. Split the line or change what is on screen inside it.")
        run = 0 if is_concrete(b) else run + 1
        if run == 3:
            flags.append(f"Beats {i - 1}-{i + 1} have nothing concrete (no number, name or place). That's where viewers drift.")
    print("-" * 74)

    hook_w = content_words(beats[0])
    last_w = content_words(beats[-1])
    echo = hook_w & last_w
    if len(beats) > 1 and echo:
        flags.append(f"Loops: the last beat repeats \"{sorted(echo)[0]}\" from the hook. Replays are free reach.")
    elif len(beats) > 1:
        flags.append("No loop. Echo one word from the hook in the last line so the replay lands clean.")

    diff = total - a.target
    wps = a.wpm / 60
    if diff > 2:
        flags.append(f"{diff:.1f}s over target. Cut about {int(diff * wps)} words.")
    elif diff < -2:
        flags.append(f"{-diff:.1f}s under target. Either add about {int(-diff * wps)} words or ship it short. Short is usually right.")
    else:
        flags.append("Length is on target.")

    for f in flags:
        print(f"- {f}")


if __name__ == "__main__":
    main()
