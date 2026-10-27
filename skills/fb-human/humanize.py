#!/usr/bin/env python3
"""humanize.py - strip the AI fingerprint out of a Facebook draft.

Three cleaning passes, then a list of what still needs a human rewrite:

  1. INVISIBLE   zero-width characters, joiners, BOMs, bidi controls, Unicode
                 tag characters, odd spaces. Your keyboard does not type these.
  2. TYPOGRAPHY  em dash -> comma, en dash -> hyphen, curly -> straight quotes,
                 ellipsis -> three dots, bullets -> hyphens
  3. LEXICON     stock words and phrases from slop.json, case-preserving

Structures (it's-not-X-it's-Y, triads, engagement bait, emoji bullets...) are
FLAGGED, not rewritten. Changing a sentence's shape needs judgement.

Usage:
  python3 humanize.py draft.txt                 cleaned text to stdout
  python3 humanize.py draft.txt --report        show every change on stderr
  python3 humanize.py draft.txt -o clean.txt    write to a file
  python3 humanize.py draft.txt --inplace       overwrite the draft

Standard library only.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_slop():
    with open(os.path.join(HERE, "slop.json"), encoding="utf-8") as f:
        return json.load(f)


def cp_range(spec):
    parts = [p.strip().replace("U+", "") for p in spec.split("-")]
    lo = int(parts[0], 16)
    hi = int(parts[-1], 16)
    return lo, hi


def pass_invisible(text, slop, log):
    out = []
    ranges = [(cp_range(i["cp"]), i["action"], i["name"]) for i in slop["invisible"]]
    counts = {}
    for ch in text:
        o = ord(ch)
        hit = None
        for (lo, hi), action, name in ranges:
            if lo <= o <= hi:
                hit = (action, name)
                break
        if hit:
            counts[hit[1]] = counts.get(hit[1], 0) + 1
            if hit[0] == "space":
                out.append(" ")
        else:
            out.append(ch)
    for name, n in counts.items():
        log.append(("INVISIBLE", f"{n} x {name}"))
    return "".join(out)


def pass_typography(text, slop, log):
    for t in slop["typographic"]:
        n = text.count(t["from"])
        if not n:
            continue
        if t["name"] == "EM DASH":
            # spaced or unspaced em dash both become a comma
            text = re.sub(r"\s*—\s*", ", ", text)
        else:
            text = text.replace(t["from"], t["to"])
        log.append(("TYPOGRAPHY", f"{n} x {t['name']} -> {t['to']!r}"))
    # tidy what the swaps leave behind
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r",\s*([.!?])", r"\1", text)
    text = re.sub(r"(?m)^\s*,\s*", "", text)
    return text


def match_case(src, repl):
    if not repl:
        return repl
    if src.isupper() and len(src) > 1:
        return repl.upper()
    if src[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def pass_lexicon(text, slop, log):
    entries = slop["phrases"] + slop["words"]
    # longest first so "delve into" wins over "delve"
    entries = sorted(entries, key=lambda e: len(e["find"]), reverse=True)
    for e in entries:
        find = e["find"]
        rx = re.compile(r"(?<![\w'])" + re.escape(find).replace("\\ ", r"\s+")
                        + r"(?![\w'])", re.IGNORECASE)
        hits = rx.findall(text)
        if not hits:
            continue

        def sub(m):
            return match_case(m.group(0), e["replace"])

        text = rx.sub(sub, text)
        shown = e["replace"] if e["replace"] else "(deleted)"
        log.append(("LEXICON", f"{len(hits)} x \"{find}\" -> {shown}"))
    return tidy(text)


def tidy(text):
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" +([,.!?;:])", r"\1", text)
    text = re.sub(r"(?m)^[ \t]*[,;:][ \t]*", "", text)
    text = re.sub(r"([.!?])\s*[,;]", r"\1", text)
    text = re.sub(r"(?m)[ \t]+$", "", text)
    # deletions can strand a conjunction or leave punctuation at a line start
    text = re.sub(r"(?i)\s+\b(and|or|but|so|to)\s*([.!?])", r"\2", text)
    text = re.sub(r"(?m)^[ \t]*[!?.,;:]+[ \t]*", "", text)
    text = re.sub(r"([!?.])\s*\1+", r"\1", text)
    # capitalise sentence starts the deletions may have exposed
    text = re.sub(r"(^|[.!?]\s+|\n)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def flag_structures(text, slop):
    flags = []
    for s in slop["structures"]:
        try:
            for m in re.finditer(s["regex"], text):
                flags.append((s["name"], m.group(0).strip()[:60], s["fix"]))
        except re.error:
            continue
    return flags


def humanize(text, slop=None):
    slop = slop or load_slop()
    log = []
    text = pass_invisible(text, slop, log)
    text = pass_typography(text, slop, log)
    text = pass_lexicon(text, slop, log)
    return text, log, flag_structures(text, slop)


def main():
    ap = argparse.ArgumentParser(description="Strip the AI fingerprint from a draft.")
    ap.add_argument("file", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--inplace", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    src = open(a.file, encoding="utf-8").read() if a.file else sys.stdin.read()
    clean, log, flags = humanize(src)

    if a.inplace and a.file:
        open(a.file, "w", encoding="utf-8").write(clean)
    elif a.out:
        open(a.out, "w", encoding="utf-8").write(clean)
    else:
        sys.stdout.write(clean)

    if a.report or a.out or a.inplace:
        err = sys.stderr
        print("\nHUMANIZER REPORT", file=err)
        print("=" * 64, file=err)
        if not log:
            print("nothing to strip", file=err)
        for kind, msg in log:
            print(f"{kind:<11} {msg}", file=err)
        print("-" * 64, file=err)
        if flags:
            print(f"{len(flags)} structure(s) need a human rewrite:", file=err)
            for name, snip, fix in flags:
                print(f"  - {name}: \"{snip}\"", file=err)
                print(f"      fix: {fix}", file=err)
        else:
            print("no structural tells flagged", file=err)
        print(f"\n{len(log)} change group(s) · {len(flags)} flag(s). Run detect.py to score it.", file=err)


if __name__ == "__main__":
    main()
