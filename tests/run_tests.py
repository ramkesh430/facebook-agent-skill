#!/usr/bin/env python3
"""run_tests.py - end-to-end checks for every tool in the pack.

Runs each script on the files in examples/ and asserts on what it prints.
Standard library only, no pytest needed:

    python3 tests/run_tests.py

Exit code 0 means every check passed.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skills")
EX = os.path.join(ROOT, "examples")
PY = sys.executable

passed, failed = 0, []


def run(*args, stdin=None):
    r = subprocess.run([PY, *args], input=stdin, capture_output=True, text=True,
                       encoding="utf-8", cwd=ROOT)
    return r.returncode, r.stdout, r.stderr


def check(name, cond, detail=""):
    global passed
    if cond:
        passed += 1
        print(f"PASS  {name}")
    else:
        failed.append(name)
        print(f"FAIL  {name}  {detail}")


def s(*parts):
    return os.path.join(SK, *parts)


def e(name):
    return os.path.join(EX, name)


# ---------- structure ----------
skills = sorted(d for d in os.listdir(SK) if os.path.isdir(os.path.join(SK, d)))
check("16 skills present", len(skills) == 16, str(skills))
for d in skills:
    p = os.path.join(SK, d, "SKILL.md")
    ok = os.path.exists(p)
    txt = open(p, encoding="utf-8").read() if ok else ""
    m = re.match(r"---\nname: (\S+)\n", txt)
    check(f"{d}/SKILL.md frontmatter", ok and m and m.group(1) == d and "description:" in txt.split("---")[1])
for f in ["fb-reel/hooks.json", "fb-human/slop.json", "fb-page/rubric.json"]:
    try:
        json.load(open(s(f), encoding="utf-8"))
        check(f"{f} is valid JSON", True)
    except ValueError as ex:
        check(f"{f} is valid JSON", False, str(ex))
for f in [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"]:
    try:
        json.load(open(os.path.join(ROOT, f), encoding="utf-8"))
        check(f"{f} is valid JSON", True)
    except ValueError as ex:
        check(f"{f} is valid JSON", False, str(ex))
rub = json.load(open(s("fb-page/rubric.json"), encoding="utf-8"))
check("rubric totals 100", sum(p["points"] for p in rub["parts"]) == 100)
hooks = json.load(open(s("fb-reel/hooks.json"), encoding="utf-8"))
try:
    for x in hooks["formulas"]:
        re.compile(x["match"])
    for x in hooks["dealbreakers"]:
        re.compile(x["regex"])
    check("hooks.json regexes compile", True)
except re.error as ex:
    check("hooks.json regexes compile", False, str(ex))

# ---------- hookscore ----------
rc, out, _ = run(s("fb-reel/hookscore.py"), e("hooks.txt"), "--json")
res = json.loads(out) if rc == 0 else []
check("hookscore runs", rc == 0 and len(res) == 6)
by = {r["hook"]: r for r in res}
check("hookscore: greeting is WEAK",
      by.get("Hey guys, today I wanted to talk about content strategy", {}).get("band") == "WEAK")
check("hookscore: cost confession is STRONG",
      by.get("I lost $18,000 because of one missing contract.", {}).get("band") == "STRONG")
check("hookscore: bait gets a dealbreaker",
      bool(by.get("Like if you agree and share this with your friends", {}).get("dealbreakers")))
check("hookscore: Local Angle classified",
      (by.get("If you live in Pokhara, this is the only tailor open on Saturdays.", {}).get("formula") or {}).get("name") == "Local Angle")
rc, out, _ = run(s("fb-reel/hookscore.py"), "--hook", "Namaste sathi haru, aaja cake ko kura garchu")
check("hookscore: Nepali greeting is WEAK", rc == 0 and "WEAK" in out)

# ---------- beats ----------
rc, out, _ = run(s("fb-reel/beats.py"), e("script.txt"), "--target", "30")
check("beats runs", rc == 0 and "BEAT SHEET" in out)
check("beats: flags long beat", "runs past 4s" in out)
check("beats: detects loop", "Loops:" in out)

# ---------- post linter ----------
rc, out, _ = run(s("fb-post/post.py"), e("post-bad.txt"), "--keywords", "birthday cakes,kathmandu")
check("post.py runs", rc == 0 and "WHAT THE MOBILE FEED SHOWS" in out)
check("post.py: bad post not READY", "FIX" in out and "ENGAGEMENT BAIT" in out)
check("post.py: hashtag wall fails", re.search(r"FAIL\s+HASHTAGS", out) is not None)
check("post.py: link warned", re.search(r"WARN\s+LINKS", out) is not None)
rc, out, _ = run(s("fb-post/post.py"), e("post-good.txt"))
check("post.py: good post READY", rc == 0 and "VERDICT READY" in out)
rc, out, _ = run(s("fb-post/post.py"), e("post-nepali.txt"))
check("post.py: Nepali bait caught", "react-bait (ne)" in out and "tag-bait (ne)" in out and "share-bait (ne)" in out)
rc, out, _ = run(s("fb-post/post.py"), stdin="Fresh momo in Patan today. 40 plates, done by 2pm. Message us to reserve.\n")
check("post.py: reads stdin", rc == 0 and "VERDICT READY" in out)

# ---------- humanizer ----------
with tempfile.TemporaryDirectory() as tmp:
    dirty = os.path.join(tmp, "dirty.txt")
    clean = os.path.join(tmp, "clean.txt")
    open(dirty, "w", encoding="utf-8").write(
        "We leverage synergy​ to deliver “seamless” cakes — moreover, it’s fresh.\n")
    rc, _, err = run(s("fb-human/humanize.py"), dirty, "-o", clean)
    c = open(clean, encoding="utf-8").read() if rc == 0 else ""
    check("humanize runs", rc == 0 and "HUMANIZER REPORT" in err)
    check("humanize: invisible chars removed", "​" not in c)
    check("humanize: em dash and curly quotes removed", not any(ch in c for ch in "—“”’"))
    check("humanize: lexicon applied", "leverage" not in c.lower() and "synergy" not in c.lower() and "moreover" not in c.lower())

    rc, out, _ = run(s("fb-human/detect.py"), e("post-bad.txt"), e("post-good.txt"))
    check("detect runs (two files)", rc == 0 and "DELTA" in out)
    rc, out, _ = run(s("fb-human/detect.py"), e("post-good.txt"), "--json")
    d = json.loads(out) if rc == 0 else {}
    check("detect: good post PASS", list(d.values())[0]["verdict"] == "PASS" if d else False)
    rc, out, _ = run(s("fb-human/detect.py"), e("post-bad.txt"), "--json")
    d = json.loads(out) if rc == 0 else {}
    check("detect: bad post FLAGGED", list(d.values())[0]["verdict"] == "FLAGGED" if d else False)

    # ---------- swipe ----------
    md = os.path.join(tmp, "swipe.md")
    rc, out, _ = run(s("fb-viral/swipe.py"), e("captured.tsv"), "--out", md)
    check("swipe runs", rc == 0 and "SWIPE FILE" in out and os.path.exists(md))
    first = [l for l in out.splitlines() if re.match(r"\s*[\d.]+x", l)]
    check("swipe: ranked by multiple, not raw views", bool(first) and " C " in first[0])

print("-" * 60)
print(f"{passed} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
