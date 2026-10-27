#!/usr/bin/env python3
"""generate.py - draft next week's Facebook posts into queue/, for you to approve.

Runs weekly in GitHub Actions (automation/workflows/generate.yml), using any
OpenAI-compatible chat API. The default is Google Gemini's free tier (no card
needed; key from aistudio.google.com). Groq's free tier works too. The
workflow opens a pull request. Merging it is the approval; nothing is
published from a draft that hasn't been merged.

Inputs (all in the repo):
  brand/voice.md        required. Who you are, how you sound, what's off limits.
  brand/ideas.md        recommended. Real stories, numbers, offers, events
                        this week. The model may only use facts from here and
                        from voice.md; anything else comes back as {{...}}.
  brand/swipe.md        optional. Output of /fb-viral.
  published/log.tsv     written by publish.py; used to avoid repeats.
  automation/config.json  timezone, weekly slots, model.

Every draft is cleaned by the pack's humanizer and linted by post.py. A draft
that fails the linter gets one repair attempt, then is dropped.

Environment:
  LLM_API_KEY    required. A Gemini (or Groq) API key, stored as a GitHub secret.
  LLM_BASE_URL   default https://generativelanguage.googleapis.com/v1beta/openai
                 Groq: https://api.groq.com/openai/v1
  MODEL          overrides config.json. "auto" (default) picks the best
                 available model from the provider's /models list.

Usage:
  python3 automation/generate.py --summary pr_body.md
  python3 automation/generate.py --dry-run          print drafts, write nothing

Standard library only.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "fb-human"))
from humanize import humanize  # noqa: E402

LINTER = os.path.join(ROOT, "skills", "fb-post", "post.py")
BASE_URL = os.environ.get("LLM_BASE_URL", "").rstrip("/") or "https://generativelanguage.googleapis.com/v1beta/openai"
# preference order for "auto"; the first one the provider lists is used
PREFERRED = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3-flash", "gemini-2.5-flash",
             "openai/gpt-oss-120b", "llama-3.3-70b-versatile", "openai/gpt-oss-20b"]
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
MAX_INPUT_CHARS = 14000   # keeps each request well inside free-tier token limits

RULES = """You write Facebook Page posts for a small business or creator, in their voice.

Hard rules:
- Use ONLY facts, numbers, names, prices, dates and stories that appear in VOICE or IDEAS.
  If a post needs a fact you don't have, write {{describe what is needed}} instead. Never invent
  customers, results, reviews, prices, discounts or deadlines.
- First line: the hook. Under 150 characters, concrete (a number, a name or a place), no greeting,
  no "We are pleased", no hashtag, no emoji first.
- No engagement bait in any language: no "like if", "share if", "tag a friend", "type YES",
  "comment AMEN", "like garnus", "share garnus", "sathi lai tag garnus", vote-with-reactions.
  A real question about the post itself is fine.
- Exactly one ask per post (message us, book, order, come in, answer a real question). Or none for
  a story post.
- 0-2 hashtags. No emoji bullet lists. No em dashes. Short paragraphs with blank lines between.
- Plain words. Never: delve, leverage, seamless, unlock, elevate, journey, game-changer, "it's not
  just X, it's Y", "in today's fast-paced world".
- No links in the post text. If a link matters, put it in first_comment (at most one link post a week).
- Every post must be different from the others and from RECENT POSTS. Mix: story, useful tip,
  behind the scenes, offer/event (only if IDEAS has one), opinion, customer question answered.

Return JSON only:
{"posts": [{"slot": 1, "type": "text", "text": "...", "first_comment": "", "uses": "which fact from IDEAS/VOICE this is built on"}]}
type is "text". Use "link" only with a real URL from IDEAS, put it in "link".
"""


def read(rel, limit=None):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return ""
    s = open(p, encoding="utf-8").read().strip()
    return s[:limit] if limit else s


def tzinfo(offset):
    m = re.match(r"([+-])(\d{2}):(\d{2})$", offset)
    if not m:
        raise SystemExit(f"bad timezone in config.json: {offset!r} (use like +05:45)")
    sign = 1 if m.group(1) == "+" else -1
    return dt.timezone(sign * dt.timedelta(hours=int(m.group(2)), minutes=int(m.group(3))))


def next_slots(cfg, now):
    tz = tzinfo(cfg["timezone"])
    local = now.astimezone(tz)
    start = local + dt.timedelta(hours=12)   # never schedule inside the review window
    out = []
    for s in cfg["slots"]:
        d = DAYS.index(s["day"].lower()[:3])
        hh, mm = (int(x) for x in s["time"].split(":"))
        days_ahead = (d - start.weekday()) % 7
        t = (start + dt.timedelta(days=days_ahead)).replace(hour=hh, minute=mm, second=0, microsecond=0)
        if t <= start:
            t += dt.timedelta(days=7)
        out.append(t)
    return sorted(out)


def recent_posts(n=20):
    p = os.path.join(ROOT, "published", "log.tsv")
    if not os.path.exists(p):
        return []
    lines = open(p, encoding="utf-8").read().splitlines()[-n:]
    return [l.split("\t")[-1] for l in lines if "\t" in l]


def request(method, path, token, body=None):
    url = f"{BASE_URL}/{path.lstrip('/')}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw = r.read().decode("utf-8", "replace")
            status = r.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        status = e.code
    except urllib.error.URLError as e:
        raise SystemExit(f"cannot reach {BASE_URL}: {e.reason}")
    try:
        parsed = json.loads(raw) if raw.strip() else None
    except ValueError:
        parsed = None
    return status, parsed, raw[:300].replace(token, "***") if token else raw[:300]


def pick_models(wanted, token):
    """Ordered list of models to try: the wanted one, or the provider's best few."""
    if wanted and wanted != "auto":
        return [wanted]
    status, data, raw = request("GET", "models", token)
    if status != 200 or not isinstance(data, dict):
        raise SystemExit(f"could not list models ({status}): {raw}  -> check LLM_API_KEY and LLM_BASE_URL")
    ids = [m.get("id", "").replace("models/", "") for m in data.get("data", [])]
    out = [p for p in PREFERRED if p in ids]
    flash = sorted((i for i in ids if "flash" in i and "lite" not in i and "image" not in i
                    and "tts" not in i and "audio" not in i and i not in out), reverse=True)
    out += flash
    out += [i for i in ids if "flash-lite" in i and i not in out]   # last resort, still free
    if not out and ids:
        out = ids[:1]
    if not out:
        raise SystemExit("the provider listed no models")
    return out[:4]


RETRYABLE = (429, 500, 502, 503, 504)
RETRY_DELAY = float(os.environ.get("RETRY_DELAY", "20"))


def chat(messages, models, token):
    """Try each model, retrying busy/overloaded responses. Returns (json, model_used)."""
    last = ""
    for model in models:
        body = {"model": model, "messages": messages, "temperature": 0.7,
                "response_format": {"type": "json_object"}}
        for attempt in range(3):
            status, data, raw = request("POST", "chat/completions", token, body)
            if status == 400 and "response_format" in raw and "response_format" in body:
                body.pop("response_format")
                status, data, raw = request("POST", "chat/completions", token, body)
            if status in (401, 403):
                raise SystemExit(f"API key rejected ({status}): {raw}  -> regenerate LLM_API_KEY")
            if status in RETRYABLE:
                last = f"{model}: {status} {raw[:120]}"
                print(f"  {model} busy ({status}), attempt {attempt + 1}/3", file=sys.stderr)
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            if status != 200 or not isinstance(data, dict) or not data.get("choices"):
                last = f"{model}: {status} {raw[:200]}"
                break   # not retryable for this model; try the next one
            content = data["choices"][0]["message"].get("content") or ""
            content = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.M)
            m = re.search(r"\{.*\}", content, re.S)
            if not m:
                last = f"{model}: did not return JSON: {content[:120]}"
                break
            try:
                return json.loads(m.group(0)), model
            except ValueError:
                last = f"{model}: returned broken JSON"
                break
        print(f"  giving up on {model}, trying the next model", file=sys.stderr)
    raise SystemExit(f"every model failed; last error: {last}. The next weekly run (or a manual re-run) will try again.")


def lint(text):
    r = subprocess.run([sys.executable, LINTER], input=text, capture_output=True, text=True, encoding="utf-8")
    fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
    return not fails, "\n".join(fails)


def slug(text):
    words = re.findall(r"[a-z0-9]+", text.lower())[:6]
    return "-".join(words) or "post"


def main():
    ap = argparse.ArgumentParser(description="Draft next week's posts into queue/.")
    ap.add_argument("--summary", help="write a markdown summary (used as the PR body)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--now", help="pretend it is this time (ISO 8601), for testing")
    a = ap.parse_args()

    cfg = json.loads(read("automation/config.json") or "{}")
    token = os.environ.get("LLM_API_KEY", "")
    if not token:
        raise SystemExit("LLM_API_KEY is not set. Add a free Gemini key as the repo secret LLM_API_KEY (see automation/SETUP.md).")

    voice = read("brand/voice.md", 6000)
    filled = re.findall(r":\*\*[ \t]*[^\s(]", voice)   # "**Name:** RAM", not "**Name:**" or "(hint)"
    if not voice or ("**" in voice and len(filled) < 3):
        raise SystemExit("brand/voice.md is missing or still blank. Fill it in first; drafts without it are generic.")
    ideas = read("brand/ideas.md", 5000)
    swipe = read("brand/swipe.md", 2000)
    recent = recent_posts()

    now = dt.datetime.fromisoformat(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    slots = next_slots(cfg, now)

    user = f"VOICE:\n{voice}\n\nIDEAS:\n{ideas or '(none given - lean on VOICE, use {{...}} for any missing fact)'}\n\n"
    if swipe:
        user += f"WHAT WORKS IN THIS NICHE:\n{swipe}\n\n"
    if recent:
        user += "RECENT POSTS (do not repeat):\n" + "\n".join(f"- {r}" for r in recent) + "\n\n"
    user += (f"LANGUAGE: {cfg.get('language', 'plain English')}\n"
             f"Write {len(slots)} posts, one per slot, slots numbered 1-{len(slots)}.")
    user = user[:MAX_INPUT_CHARS]
    messages = [{"role": "system", "content": RULES}, {"role": "user", "content": user}]

    models = pick_models(os.environ.get("MODEL") or cfg.get("model", "auto"), token)
    out, model = chat(messages, models, token)
    models = [model] + [m for m in models if m != model]
    posts = out.get("posts", [])[: len(slots)]
    kept, dropped, link_posts = [], [], 0
    for i, p in enumerate(posts):
        text = (p.get("text") or "").strip()
        if not text:
            continue
        text, _, _ = humanize(text)
        text = text.strip()
        ok, report = lint(text)
        if not ok:
            fix, _ = chat(messages + [
                {"role": "assistant", "content": json.dumps({"posts": [p]})},
                {"role": "user", "content": "The linter failed this post:\n" + report +
                 "\nRewrite it to fix every FAIL. Same JSON shape, one post."}], models, token)
            fixed = (fix.get("posts") or [{}])[0].get("text", "")
            text, _, _ = humanize(fixed)
            text = text.strip()
            ok, report = lint(text)
        if not ok:
            dropped.append((i + 1, report))
            continue
        kind = p.get("type", "text")
        link = (p.get("link") or "").strip()
        if kind == "link" and (not link.startswith("http") or link_posts >= cfg.get("max_link_posts_per_week", 1)):
            kind, link = "text", ""
        link_posts += kind == "link"
        fc = (p.get("first_comment") or "").strip() or cfg.get("first_comment_link", "")
        kept.append({"when": slots[len(kept)], "type": kind, "link": link, "text": text,
                     "first_comment": fc, "uses": p.get("uses", "")})

    lines = [f"## Drafts for the week of {slots[0].date()}", "",
             f"Model: `{model}` via {BASE_URL.split('/')[2]}. Merge this PR to approve; publish.py posts each one at its time.",
             "Edit any file in this PR before merging. Close the PR to skip the week.", ""]
    os.makedirs(os.path.join(ROOT, "queue"), exist_ok=True)
    for k in kept:
        stamp = k["when"].strftime("%Y-%m-%d-%H%M")
        name = f"{stamp}-{slug(k['text'])}.md"
        fm = [f"publish_at: {k['when'].isoformat()}", f"type: {k['type']}"]
        if k["link"]:
            fm.append(f"link: {k['link']}")
        if k["first_comment"]:
            fm.append(f"first_comment: {k['first_comment']}")
        content = "---\n" + "\n".join(fm) + "\n---\n" + k["text"] + "\n"
        flag = " **needs your input: fill the {{...}} before merging**" if "{{" in content else ""
        lines.append(f"- `{name}` {k['when'].strftime('%a %d %b %H:%M')}{flag}  \n  > {k['text'].splitlines()[0][:140]}  \n  built on: {k['uses'][:120]}")
        if a.dry_run:
            print(content)
        else:
            with open(os.path.join(ROOT, "queue", name), "w", encoding="utf-8") as f:
                f.write(content)
    for slot, rep in dropped:
        lines.append(f"- slot {slot} dropped after a failed repair: {rep[:200]}")
    summary = "\n".join(lines) + "\n"
    print(summary)
    if a.summary:
        with open(a.summary, "w", encoding="utf-8") as f:
            f.write(summary)
    if not kept:
        raise SystemExit("no drafts survived the linter")


if __name__ == "__main__":
    main()
