#!/usr/bin/env python3
"""detect.py - score a draft on five local checks before anyone else sees it.

  BURSTINESS    do sentence lengths vary the way people's do?
  SPECIFICITY   concrete markers (numbers, names, places) per 100 words
  SLOP DENSITY  stock words and phrases from slop.json per 100 words
  FINGERPRINT   invisible characters, em dashes, curly quotes
  VOICE         structural tells (triads, it's-not-X-it's-Y, bait, ...)

These are local heuristics modelled on what public detectors look at. They
are NOT GPTZero, Originality, Copyleaks or any other service, they don't call
them, and they can't promise those verdicts.

Usage:
  python3 detect.py draft.txt                 score one draft
  python3 detect.py before.txt after.txt      score both and show the delta
  python3 detect.py draft.txt --json

Standard library only.
"""
import argparse
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from humanize import load_slop, cp_range  # noqa: E402

NUMBER_WORDS = set((
    "one two three four five six seven eight nine ten eleven twelve twenty "
    "thirty forty fifty hundred thousand million lakh crore half double"
).split())
WEIGHTS = {"BURSTINESS": 0.2, "SPECIFICITY": 0.2, "SLOP DENSITY": 0.25,
           "FINGERPRINT": 0.15, "VOICE": 0.2}


def proper_nouns(text):
    """Capitalised words that are not the first word of a line or sentence."""
    n = 0
    for chunk in re.split(r"(?<=[.!?])\s+|\n+", text):
        toks = re.findall(r"[A-Za-z][A-Za-z']*", chunk)
        n += sum(1 for t in toks[1:] if re.match(r"[A-Z][a-z]{2,}$", t) and t not in ("I'm", "I've", "I'll"))
    return n


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p for p in parts if len(re.findall(r"\w+", p)) >= 2]


def score(text, slop):
    words = re.findall(r"[A-Za-z0-9']+", text)
    nw = max(len(words), 1)
    per100 = 100.0 / nw
    detail = {}

    # BURSTINESS: coefficient of variation of sentence length
    lens = [len(re.findall(r"\w+", s)) for s in sentences(text)]
    if len(lens) >= 3:
        mean = sum(lens) / len(lens)
        sd = math.sqrt(sum((l - mean) ** 2 for l in lens) / len(lens))
        cv = sd / mean if mean else 0
        burst = max(0.0, min(100.0, cv * 140))
        detail["BURSTINESS"] = f"sentence length cv {cv:.2f} over {len(lens)} sentences"
    else:
        burst = 60.0
        detail["BURSTINESS"] = "too few sentences to judge"

    # SPECIFICITY
    conc = len(re.findall(r"\d[\d,.]*", text))
    conc += sum(1 for w in words if w.lower() in NUMBER_WORDS)
    conc += proper_nouns(text)
    rate = conc * per100
    spec = max(0.0, min(100.0, rate * 16))
    detail["SPECIFICITY"] = f"{rate:.1f} concrete markers per 100 words"

    # SLOP DENSITY
    low = text.lower()
    hits = 0
    for e in slop["words"] + slop["phrases"]:
        rx = r"(?<![\w'])" + re.escape(e["find"]).replace("\\ ", r"\s+") + r"(?![\w'])"
        hits += len(re.findall(rx, low))
    srate = hits * per100
    slop_s = max(0.0, 100.0 - srate * 25)
    detail["SLOP DENSITY"] = f"{hits} stock terms, {srate:.1f} per 100 words"

    # FINGERPRINT
    inv = 0
    for i in slop["invisible"]:
        lo, hi = cp_range(i["cp"])
        inv += sum(1 for ch in text if lo <= ord(ch) <= hi)
    em = text.count("—")
    curly = sum(text.count(c) for c in "‘’“”")
    fp = max(0.0, 100.0 - inv * 15 - em * 12 - min(curly, 10) * 2)
    bits = []
    if inv:
        bits.append(f"{inv} invisible char(s)")
    if em:
        bits.append(f"{em} em dash(es)")
    if curly:
        bits.append(f"{curly} curly quote(s)")
    detail["FINGERPRINT"] = ", ".join(bits) or "clean"

    # VOICE
    tells = 0
    for s in slop["structures"]:
        try:
            tells += len(re.findall(s["regex"], text))
        except re.error:
            pass
    voice = max(0.0, 100.0 - tells * 12)
    detail["VOICE"] = f"{tells} structural tell(s)"

    checks = {"BURSTINESS": burst, "SPECIFICITY": spec, "SLOP DENSITY": slop_s,
              "FINGERPRINT": fp, "VOICE": voice}
    total = sum(checks[k] * w for k, w in WEIGHTS.items())
    # one terrible check drags the whole thing: no averaging away a disaster
    worst = min(checks.values())
    if worst < 20:
        total = min(total, 55)
    if checks["SLOP DENSITY"] == 0:
        total = min(total, 40)
    # structural tells are what a reader notices first; they can't be averaged away
    if checks["VOICE"] < 50:
        total = min(total, 60)
    return {"checks": checks, "detail": detail, "human": round(total, 1),
            "verdict": "PASS" if total >= 65 else "FLAGGED"}


def bar(v, width=24):
    n = int(round(v / 100 * width))
    return "#" * n + "." * (width - n)


def show(name, r):
    print(f"{name}")
    for k in WEIGHTS:
        print(f"{k:<13}{bar(r['checks'][k])} {r['checks'][k]:5.1f}  {r['detail'][k]}")
    print("-" * 70)
    print(f"{'HUMAN SCORE':<13}{bar(r['human'])} {r['human']:5.1f}  {r['verdict']}")


def main():
    ap = argparse.ArgumentParser(description="Five-check human score.")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    slop = load_slop()
    if not a.files:
        res = [("stdin", score(sys.stdin.read(), slop))]
    else:
        res = [(f, score(open(f, encoding="utf-8").read(), slop)) for f in a.files[:2]]
    if a.json:
        print(json.dumps({n: r for n, r in res}, indent=2))
        return
    for i, (n, r) in enumerate(res):
        if i:
            print()
        show(n, r)
    if len(res) == 2:
        d = res[1][1]["human"] - res[0][1]["human"]
        print(f"\nDELTA {d:+.1f}  ({res[0][1]['verdict']} -> {res[1][1]['verdict']})")


if __name__ == "__main__":
    main()
