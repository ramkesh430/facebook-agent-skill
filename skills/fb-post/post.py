#!/usr/bin/env python3
"""post.py - lint a Facebook post before it goes out.

Prints what the feed shows before "... See more" (mobile and desktop), then
runs the checks that decide whether a Facebook post gets read, shared, or
quietly demoted:

  LENGTH         total characters (Facebook allows 63,206; almost nothing should)
  FIRST LINE     does the first line fit the mobile window, or get cut mid-thought?
  HOOK CONCRETE  numbers, names or places inside the visible window
  ENGAGEMENT BAIT  react-bait, share-bait, tag-bait, comment-bait, vote-bait.
                 Meta's content distribution guidelines demote these.
  LINKS          a URL in the body. Link posts reach fewer people, and some
                 Pages are in a test that limits link posts per month.
  HASHTAGS       0-3 is right on Facebook. They label, they don't distribute.
  ONE ASK        exactly one call to action
  EMOJI          density
  SEARCH TERMS   the phrases you want to be found for, present as words

Usage:
  python3 post.py post.txt
  python3 post.py post.txt --keywords "home bakery,birthday cakes"
  python3 post.py post.txt --mobile 140 --desktop 477

Window sizes are approximate and change with device and font. Defaults:
mobile 150 characters / 3 lines, desktop 477 characters. Standard library only.
"""
import argparse
import re
import sys
import textwrap

MAX_LEN = 63206

BAIT = [
    ("react-bait", r"(?i)\b(like|react|love|haha|wow)\s+(this|if|for)\b.{0,40}\b(if|for|=)\b|\b(like|react) (with|using) (a )?(heart|love|haha|wow|sad|angry)\b|\b1 like\s*=\s*"),
    ("vote-bait", r"(?i)\b(vote|choose|pick)\b.{0,40}\b(react|like|love|haha|wow|comment (a|b|1|2))\b|\breact with\b"),
    ("share-bait", r"(?i)\bshare (this|if|it|before|with (all )?your friends)\b|\bshare (to|so) (your|everyone)\b|\bbefore (it'?s|they) (deleted|removed|take it down)\b"),
    ("tag-bait", r"(?i)\btag (a friend|someone|your|3|three|5|five|a person|the friend)\b"),
    ("comment-bait", r"(?i)\b(type|comment|say)\s+[\"']?(yes|amen|done|1|ok|i'?m in|me)\b[\"']?(\s+if|\s+to|\s+for|\s*!|\s*$)"),
    # Nepali, romanized and Devanagari. Same five Meta bait types, in the
    # words people actually type in Nepal.
    ("react-bait (ne)", r"(?i)\b(like|love|react)\s+(garnus|garnuhos|garnu ?hola|gara|garau|gardinus|gardinuhos)\b|\b(bhane|vane|bhaye|vaye)\s+(like|love|react)\b|(लाइक|लभ)\s*(गर्नुहोस्|गर्नुस्|गर्नु होला|गर|गरिदिनुहोस्)|भने\s*(लाइक|लभ)"),
    ("share-bait (ne)", r"(?i)\bshare\s+(garnus|garnuhos|garnu ?hola|gara|garau|gardinus|gardinuhos)\b|\b(bhane|vane)\s+share\b|शेयर\s*(गर्नुहोस्|गर्नुस्|गर्नु होला|गर|गरिदिनुहोस्)|भने\s*शेयर"),
    ("tag-bait (ne)", r"(?i)\b(sathi|saathi|friend)\w*\s+(lai\s+)?tag\b|\btag\s+(garnus|garnuhos|garnu ?hola|gara|garau|gardinus)\b|ट्याग\s*(गर्नुहोस्|गर्नुस्|गर)"),
    ("comment-bait (ne)", r"(?i)[\"']?\b(ho|yes|jay\s+\w+|om|amen|done)\b[\"']?\s+(lekhnus|lekhnuhos|lekha|lekhnu ?hola)\b|(लेख्नुहोस्|लेख्नुस्)\s*$|['\"](हो|जय\s*\S+)['\"]\s*(लेख्नुहोस्|लेख्नुस्)"),
    ("copy-paste hoax", r"(?i)\b(copy and paste|copy & paste|don'?t share,? copy|facebook (is|will) (deleting|charging|start charging)|i do not give facebook permission)\b"),
]

ASKS = [
    r"(?i)\bcomment\b",
    r"(?i)\b(message|dm|inbox|text|whatsapp|call) (us|me)\b",
    r"(?i)\bsend (us|me) a message\b",
    r"(?i)\b(join|book|order|buy|shop|sign up|register|reserve|visit|download|subscribe)\b",
    r"(?i)\bshare (your|what)\b",
    r"(?i)\bsave (this|it)\b",
    r"(?i)\b(click|tap) (the )?(link|button)\b",
    r"(?i)\bfollow (us|me|the page)\b",
    r"(?i)\b(message|inbox|call|phone|order|book|join|sampark|samparka)\s+(garnus|garnuhos|garnu ?hola|gara|gardinus)\b",
    r"(म्यासेज|इनबक्स|कल|अर्डर|बुक|सम्पर्क)\s*(गर्नुहोस्|गर्नुस्|गर्नु होला)",
]

URL_RE = r"(?i)\b(https?://\S+|www\.\S+|\b[a-z0-9-]+\.(com|net|org|io|co|np|in|shop|store|me|ly|link)(/\S*)?)\b"
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⬀-⯿\U0001F1E6-\U0001F1FF]")


def box(text, width, title, cut_label):
    flat = re.sub(r"\n+", " / ", text.strip())
    shown = flat[:width]
    lines = textwrap.wrap(shown, 54) or [""]
    out = [title, "+" + "-" * 56 + "+"]
    for l in lines:
        out.append("| " + l.ljust(54) + " |")
    if len(flat) > width:
        out.append("+" + "-" * (56 - len(cut_label) - 1) + " " + cut_label + "+")
    else:
        out.append("+" + "-" * 56 + "+")
    return "\n".join(out)


def proper_nouns(text):
    """Capitalised words that are not the first word of a line or sentence."""
    n = 0
    for chunk in re.split(r"(?<=[.!?])\s+|\n+", text):
        toks = re.findall(r"[A-Za-z][A-Za-z']*", chunk)
        n += sum(1 for t in toks[1:] if re.match(r"[A-Z][a-z]{2,}$", t) and t not in ("I'm", "I've", "I'll"))
    return n


def concrete(text):
    n = len(re.findall(r"\d[\d,.]*", text))
    n += proper_nouns(text)
    return n


def main():
    ap = argparse.ArgumentParser(description="Lint a Facebook post.")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--keywords", default="", help="comma-separated search terms")
    ap.add_argument("--mobile", type=int, default=150)
    ap.add_argument("--desktop", type=int, default=477)
    ap.add_argument("--reel", action="store_true", help="this is a Reel/video caption")
    a = ap.parse_args()

    text = open(a.file, encoding="utf-8").read() if a.file else sys.stdin.read()
    text = text.strip()
    if not text:
        sys.exit("empty post")

    print(box(text, a.mobile, "WHAT THE MOBILE FEED SHOWS", "... See more "))
    print()
    if len(text) > a.mobile:
        print(f"(desktop shows about {a.desktop} characters before the cut)")
        print()

    results = []

    def add(status, name, msg):
        results.append((status, name, msg))

    n = len(text)
    limit = 500 if a.reel else 1500
    if n > MAX_LEN:
        add("FAIL", "LENGTH", f"{n} / {MAX_LEN} characters, over the hard limit")
    elif n > limit:
        add("WARN", "LENGTH", f"{n} characters. Long is fine only if every paragraph earns the next one")
    else:
        add("PASS", "LENGTH", f"{n} characters")

    first = text.splitlines()[0].strip()
    if len(first) > a.mobile:
        add("WARN", "FIRST LINE", f"{len(first)} characters, so mobile cuts it at {a.mobile} mid-thought")
    elif re.match(r"(?i)^(hi|hello|hey|namaste|good (morning|evening)|dear)\b", first):
        add("FAIL", "FIRST LINE", "opens with a greeting. The first line is the whole pitch")
    elif first.startswith("#") or (first and EMOJI_RE.match(first)):
        add("WARN", "FIRST LINE", "opens with a hashtag or emoji. Open on the claim")
    else:
        add("PASS", "FIRST LINE", f"{len(first)} characters, fits the mobile window")

    c = concrete(text[: a.mobile])
    if c:
        add("PASS", "HOOK CONCRETE", f"{c} numbers or names in the visible window")
    else:
        add("WARN", "HOOK CONCRETE", "nothing concrete before the cut. Add a number, a name or a place")

    hits = []
    for name, rx in BAIT:
        m = re.search(rx, text)
        if m:
            hits.append(f"{name} (\"{m.group(0).strip()[:40]}\")")
    if hits:
        add("FAIL", "ENGAGEMENT BAIT", "; ".join(hits) + ". Meta demotes this")
    else:
        add("PASS", "ENGAGEMENT BAIT", "none found")

    urls = [m.group(0) for m in re.finditer(URL_RE, text)]
    if urls:
        add("WARN", "LINKS", f"{len(urls)} link(s) in the body. Consider the first comment instead, and check whether your Page has a monthly link limit")
    else:
        add("PASS", "LINKS", "no link in the body")

    tags = re.findall(r"(?<!\w)#\w+", text)
    if len(tags) <= 3:
        add("PASS", "HASHTAGS", f"{len(tags)} tag(s)" + (": " + " ".join(tags) if tags else ""))
    elif len(tags) <= 5:
        add("WARN", "HASHTAGS", f"{len(tags)} tags. On Facebook, 0-3 is plenty")
    else:
        add("FAIL", "HASHTAGS", f"{len(tags)} tags. A hashtag wall reads as spam on Facebook")

    asks = sum(1 for rx in ASKS if re.search(rx, text))
    if asks == 1:
        add("PASS", "ONE ASK", "one call to action")
    elif asks == 0:
        add("WARN", "ONE ASK", "no ask. Fine for a story post, otherwise add one")
    else:
        add("WARN", "ONE ASK", f"{asks} different asks. Two asks is the same as none")

    e = len(EMOJI_RE.findall(text))
    dens = e / max(n, 1) * 100
    if dens > 4:
        add("WARN", "EMOJI", f"{e} emoji, {dens:.1f} per 100 characters. Use them as punctuation")
    else:
        add("PASS", "EMOJI", f"{e} emoji")

    kws = [k.strip() for k in a.keywords.split(",") if k.strip()]
    if kws:
        low = text.lower()
        missing = [k for k in kws if k.lower() not in low]
        status = "PASS" if not missing else "WARN"
        msg = f"{len(kws) - len(missing)}/{len(kws)} present"
        if missing:
            msg += ". Missing: " + ", ".join(missing)
        add(status, "SEARCH TERMS", msg)

    for s, name, msg in results:
        print(f"{s:<5} {name:<16} {msg}")
    fails = sum(1 for r in results if r[0] == "FAIL")
    warns = sum(1 for r in results if r[0] == "WARN")
    print("-" * 60)
    print("VERDICT", "READY" if not fails else f"FIX {fails} FAIL(S)", f"· {warns} warning(s) to decide on")


if __name__ == "__main__":
    main()
