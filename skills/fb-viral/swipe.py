#!/usr/bin/env python3
"""swipe.py - rank captured Facebook posts by how far each beat its own account.

Raw views are not evidence. A 2M-follower Page doing 400k views had a quiet
Tuesday. A 4k-follower Page doing 400k found something. This ranks on the
multiple over each account's own baseline:

  baseline = the account's median metric, when you captured 3+ of its posts
           = else followers x 0.10 (stated in the output as a fallback)

Input: a TSV (tab-separated) with a header row. Columns, any order:
  account   required   Page or profile name
  metric    required   views, or shares, or reactions - be consistent
  hook      required   the first line / first spoken sentence
  followers optional   used only for the fallback baseline
  format    optional   reel, photo, text, link, group, live
  url       optional

Usage:
  python3 swipe.py captured.tsv
  python3 swipe.py captured.tsv --out ~/.claude/facebook/swipe.md

Standard library only. It reads a file you made by hand. It does not scrape.
"""
import argparse
import csv
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REEL = os.path.join(os.path.dirname(HERE), "fb-reel")
sys.path.insert(0, REEL)
try:
    from hookscore import load_hooks, score_hook  # noqa: E402
    HOOKS = load_hooks()
except Exception:  # fb-reel not installed next to this skill
    HOOKS = None


def num(x):
    x = (x or "").strip().lower().replace(",", "")
    mult = 1
    if x.endswith("k"):
        mult, x = 1_000, x[:-1]
    elif x.endswith("m"):
        mult, x = 1_000_000, x[:-1]
    try:
        return float(x) * mult
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser(description="Outlier-rank captured posts.")
    ap.add_argument("file")
    ap.add_argument("--out", help="write the swipe file as markdown")
    a = ap.parse_args()

    with open(a.file, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    rows = [{k.strip().lower(): (v or "").strip() for k, v in r.items() if k} for r in rows]
    rows = [r for r in rows if r.get("account") and num(r.get("metric")) is not None and r.get("hook")]
    if not rows:
        sys.exit("no usable rows: need account, metric and hook columns")

    by_acct = {}
    for r in rows:
        by_acct.setdefault(r["account"], []).append(num(r["metric"]))

    out = []
    fallback_used = False
    for r in rows:
        m = num(r["metric"])
        vals = by_acct[r["account"]]
        if len(vals) >= 3:
            base, how = statistics.median(vals), "median"
        elif num(r.get("followers")):
            base, how = num(r["followers"]) * 0.10, "followers"
            fallback_used = True
        else:
            base, how = statistics.median(vals), "median(n<3)"
            fallback_used = True
        mult = m / base if base else 0
        sc = score_hook(r["hook"], HOOKS) if HOOKS else None
        out.append({**r, "metric_n": m, "multiple": mult, "baseline": how,
                    "score": sc["score"] if sc else None,
                    "formula": (f"#{sc['formula']['id']} {sc['formula']['name']}"
                                if sc and sc["formula"] else "- unclassified")})
    out.sort(key=lambda r: r["multiple"], reverse=True)

    lines = []
    lines.append(f"SWIPE FILE · {len(out)} posts · {len(by_acct)} accounts · baseline: account median"
                 + (" (followers x 0.10 where fewer than 3 posts)" if fallback_used else ""))
    lines.append("=" * 78)
    for r in out:
        s = f"hook {r['score']:.0f}" if r["score"] is not None else "hook -"
        fmt = r.get("format") or "-"
        lines.append(f"{r['multiple']:6.1f}x  {s:<8} {r['formula'][:24]:<24} {fmt:<6} {r['account'][:16]:<16} {int(r['metric_n']):>10,}")
        lines.append(f"         \"{r['hook'][:68]}\"")
    lines.append("-" * 78)

    k = max(1, len(out) // 3)
    top, bot = out[:k], out[-k:]
    if len(out) >= 3:
        def avg(rs, key):
            v = [x[key] for x in rs if x[key] is not None]
            return sum(v) / len(v) if v else 0

        def share(rs, pred):
            return 100 * sum(1 for x in rs if pred(x)) / len(rs)

        has_num = lambda x: any(c.isdigit() for c in x["hook"])
        words = lambda rs: sum(len(x["hook"].split()) for x in rs) / len(rs)
        lines.append("TOP THIRD vs BOTTOM THIRD")
        if HOOKS:
            lines.append(f"  hook score        {avg(top, 'score'):5.1f}  vs {avg(bot, 'score'):5.1f}")
        lines.append(f"  hooks with digits {share(top, has_num):5.0f}% vs {share(bot, has_num):5.0f}%")
        lines.append(f"  words in hook     {words(top):5.1f}  vs {words(bot):5.1f}")
        fm_top = {}
        for x in top:
            fm_top[x.get("format") or "-"] = fm_top.get(x.get("format") or "-", 0) + 1
        lines.append("  formats on top    " + ", ".join(f"{k} x{v}" for k, v in sorted(fm_top.items(), key=lambda kv: -kv[1])))
        forms = {}
        for x in top:
            if not x["formula"].startswith("-"):
                forms[x["formula"]] = forms.get(x["formula"], 0) + 1
        if forms:
            lines.append("  formulas on top   " + ", ".join(f"{k} x{v}" for k, v in sorted(forms.items(), key=lambda kv: -kv[1])))
    text = "\n".join(lines)
    print(text)

    if a.out:
        path = os.path.expanduser(a.out)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Swipe file\n\n```\n" + text + "\n```\n")
        print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
