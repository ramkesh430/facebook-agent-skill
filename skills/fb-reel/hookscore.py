#!/usr/bin/env python3
"""hookscore.py - score Facebook Reel / video hooks before you shoot them.

Five properties, each 0-100:
  FRONTLOAD    does the first few words carry the claim, or is it warm-up?
  SPECIFICITY  numbers, money, names, places - spoken numbers count too
  STAKES       is something lost, gained, risked, or wrong?
  ADDRESS      does it talk to one person ("you") or confess ("I")?
  BREVITY      sayable in about three seconds?

Dealbreakers (greeting, preamble, "stop scrolling", engagement bait) cap the
score, because no amount of specificity rescues them.

Usage:
  python3 hookscore.py hooks.txt          one hook per line, ranked
  python3 hookscore.py --hook "one line"  score a single hook
  python3 hookscore.py hooks.txt --json   machine-readable

Standard library only. Nothing leaves your machine.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

NUMBER_WORDS = (
    "zero one two three four five six seven eight nine ten eleven twelve "
    "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty "
    "forty fifty sixty seventy eighty ninety hundred thousand million billion "
    "lakh lakhs crore crores half double triple first second third"
).split()
UNITS = (
    "dollars rupees rs euros pounds percent minutes minute hours hour days day "
    "weeks week months month years year seconds second kg km likes shares "
    "followers views orders customers clients sales people members"
).split()
STAKE_WORDS = (
    "lost lose losing loss wasted waste cost costs costing broke debt fired quit "
    "failed fail failing mistake mistakes wrong worst never stop dying dead killed "
    "killing banned blocked scam saved save earned made doubled tripled sold grew "
    "secret regret warning risk hate cheapest expensive free fine sued refund "
    "deleted crashed tried tested worth"
).split()
WEAK_OPENERS = (
    "so", "um", "uh", "okay", "ok", "well", "basically", "today", "guys",
    "everyone", "friends", "alright", "right", "now", "just",
)


def load_hooks():
    path = os.path.join(HERE, "hooks.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"formulas": [], "dealbreakers": []}


def words_of(text):
    return re.findall(r"[A-Za-z0-9$%'.,]+", text)


def proper_nouns(text):
    """Capitalised words that are not the first word of a line or sentence."""
    n = 0
    for chunk in re.split(r"(?<=[.!?])\s+|\n+", text):
        toks = re.findall(r"[A-Za-z][A-Za-z']*", chunk)
        n += sum(1 for t in toks[1:] if re.match(r"[A-Z][a-z]{2,}$", t) and t not in ("I'm", "I've", "I'll"))
    return n


def concrete_markers(text):
    """Count concrete things: digits, money, spoken numbers, proper nouns."""
    low = text.lower()
    n = 0
    n += len(re.findall(r"\d[\d,.]*", text))
    toks = re.findall(r"[a-z]+", low)
    n += sum(1 for t in toks if t in NUMBER_WORDS)
    n += sum(1 for t in toks if t in UNITS) // 2
    # proper nouns not at sentence start
    n += proper_nouns(text)
    return n


def score_hook(hook, data):
    text = hook.strip()
    low = text.lower()
    toks = re.findall(r"[a-z0-9']+", low)
    nw = max(len(toks), 1)

    # FRONTLOAD: penalise warm-up words in the first three tokens
    first = toks[:3]
    weak = sum(1 for t in first if t in WEAK_OPENERS)
    frontload = 100 - 35 * weak
    if toks and toks[0] in ("i", "my", "you", "your", "this", "nobody", "the", "if", "stop", "steal"):
        frontload = min(100, frontload + 5)
    if re.match(r"(?i)^\s*(hey|hi|hello|namaste|good morning)\b", text):
        frontload = 0

    # SPECIFICITY
    cm = concrete_markers(text)
    specificity = min(100, 35 + 25 * cm) if cm else 25

    # STAKES
    st = sum(1 for t in toks if t.strip("'") in STAKE_WORDS)
    if re.search(r"[$₹]|\brs\.?\s?\d|\brupees\b|\bdollars\b", low):
        st += 1
    stakes = min(100, 40 + 30 * st) if st else 40

    # ADDRESS
    you = len(re.findall(r"\byou(r|'re|'ve|'ll)?\b", low))
    me = len(re.findall(r"\b(i|i'm|i've|my|we|our)\b", low))
    address = 70 if (you or me) else 45
    if you and me:
        address = 85
    elif you >= 1:
        address = 80

    # BREVITY: ideal 6-14 words (about 2-4 seconds spoken)
    if 6 <= nw <= 14:
        brevity = 100
    elif nw < 6:
        brevity = 70 + 5 * nw
    else:
        brevity = max(0, 100 - 8 * (nw - 14))

    props = {
        "FRONTLOAD": max(0, min(100, frontload)),
        "SPECIFICITY": specificity,
        "STAKES": stakes,
        "ADDRESS": address,
        "BREVITY": brevity,
    }
    weights = {"FRONTLOAD": 0.25, "SPECIFICITY": 0.30, "STAKES": 0.20,
               "ADDRESS": 0.10, "BREVITY": 0.15}
    total = sum(props[k] * w for k, w in weights.items())

    breakers = []
    for d in data.get("dealbreakers", []):
        try:
            if re.search(d["regex"], text):
                breakers.append(d["why"])
        except re.error:
            continue
    if breakers:
        total = min(total, 55) - 12 * (len(breakers) - 1)
        if props["FRONTLOAD"] == 0:
            total = min(total, 15)
    total = round(max(0.0, min(100.0, total)), 1)

    formula = classify(text, data)
    band = "STRONG" if total >= 70 else "OK" if total >= 45 else "WEAK"
    weakest = min(props, key=lambda k: props[k])
    return {
        "hook": text, "score": total, "band": band, "properties": props,
        "weakest": weakest, "dealbreakers": breakers, "formula": formula,
    }


def classify(text, data):
    for f in data.get("formulas", []):
        try:
            if re.search(f["match"], text):
                return {"id": f["id"], "name": f["name"]}
        except re.error:
            continue
    return None


def wrap(s, width=60):
    return s if len(s) <= width else s[: width - 3] + "..."


def main():
    ap = argparse.ArgumentParser(description="Score Facebook video hooks.")
    ap.add_argument("file", nargs="?", help="text file, one hook per line")
    ap.add_argument("--hook", help="score a single hook")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.hook:
        hooks = [a.hook]
    elif a.file:
        with open(a.file, encoding="utf-8") as f:
            hooks = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    else:
        hooks = [l.strip() for l in sys.stdin if l.strip()]
    if not hooks:
        sys.exit("no hooks given")

    data = load_hooks()
    results = sorted((score_hook(h, data) for h in hooks),
                     key=lambda r: r["score"], reverse=True)
    if a.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    print("HOOK RANKING")
    print("=" * 78)
    for i, r in enumerate(results):
        mark = "->" if i == 0 else "  "
        print(f"{mark} {r['score']:5.1f}  {r['band']:<6}  {wrap(r['hook'])}")
        f = r["formula"]
        tag = f"#{f['id']} {f['name']}" if f else "unclassified"
        print(f"{'':10}formula: {tag}   weakest: {r['weakest']} ({r['properties'][r['weakest']]})")
        for d in r["dealbreakers"]:
            print(f"{'':10}dealbreaker: {d}")
    print("-" * 78)
    top = results[0]
    if top["score"] < 50:
        print("Top hook is under 50. You do not have the hook yet; editing won't fix it.")
    else:
        print(f"Shoot the top one, or fix its weakest property ({top['weakest']}) first.")


if __name__ == "__main__":
    main()
