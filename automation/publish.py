#!/usr/bin/env python3
"""publish.py - publish approved, due posts from queue/ to a Facebook Page.

Runs on a schedule in GitHub Actions (see automation/workflows/publish.yml).
Everything in queue/ on the main branch counts as approved: posts only get
there by merging the weekly draft pull request.

A queue file looks like this:

    ---
    publish_at: 2026-11-02T18:30:00+05:45
    type: text
    link: https://example.com
    image: brand/images/cake.jpg
    first_comment: Menu and prices: https://example.com/menu
    ---
    The post text goes here.

  type is text, link or photo. link is only for type: link. image is only for
  type: photo, as a path in this repo or an https URL.

For each due post it:
  1. refuses it if it still has a {{placeholder}} in it
  2. lints it with skills/fb-post/post.py and refuses it on any FAIL
  3. refuses an exact duplicate of something already published
  4. publishes it through the Graph API, then adds the first comment
  5. moves the file to published/YYYY-MM/ (or failed/ with the reason)

Environment:
  FB_PAGE_ID      the Page's numeric id            (GitHub secret)
  FB_PAGE_TOKEN   a Page access token              (GitHub secret, never printed)
  GRAPH_VERSION   default v26.0
  GRAPH_BASE      default https://graph.facebook.com (override for tests)
  MAX_PER_RUN     default 2
  DRY_RUN=1       lint and report, publish nothing, move nothing

Usage:
  python3 automation/publish.py            publish what is due
  python3 automation/publish.py --check    verify the token can see the Page
  python3 automation/publish.py --list     show the queue and when each is due

Standard library only.
"""
import argparse
import datetime as dt
import hashlib
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(ROOT, "queue")
DONE = os.path.join(ROOT, "published")
FAILED = os.path.join(ROOT, "failed")
LOG = os.path.join(DONE, "log.tsv")
LINTER = os.path.join(ROOT, "skills", "fb-post", "post.py")

VERSION = os.environ.get("GRAPH_VERSION", "v26.0")
BASE = os.environ.get("GRAPH_BASE", "https://graph.facebook.com").rstrip("/")
TOKEN = os.environ.get("FB_PAGE_TOKEN", "")
PAGE = os.environ.get("FB_PAGE_ID", "")


class GraphError(Exception):
    pass


def redact(s):
    s = str(s)
    if TOKEN:
        s = s.replace(TOKEN, "***")
    return re.sub(r"access_token=[^&\s\"']+", "access_token=***", s)


# ---------------------------------------------------------------- queue files
def parse(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S)
    if not m:
        raise ValueError("missing front matter (--- ... ---)")
    meta = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"bad front matter line: {line!r}")
        k, v = line.split(":", 1)
        meta[k.strip().lower()] = v.strip().strip("\"'")
    body = m.group(2).strip()
    if not body:
        raise ValueError("empty post body")
    if "publish_at" not in meta:
        raise ValueError("publish_at is required")
    meta["when"] = parse_time(meta["publish_at"])
    meta["type"] = meta.get("type", "text").lower()
    if meta["type"] not in ("text", "link", "photo"):
        raise ValueError(f"type must be text, link or photo, not {meta['type']!r}")
    if meta["type"] == "link" and not meta.get("link"):
        raise ValueError("type: link needs a link")
    if meta["type"] == "photo" and not meta.get("image"):
        raise ValueError("type: photo needs an image")
    return meta, body


def parse_time(s):
    s = s.strip().replace(" ", "T", 1)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    t = dt.datetime.fromisoformat(s)
    if t.tzinfo is None:
        raise ValueError("publish_at needs a timezone offset, e.g. +05:45")
    return t


def fingerprint(body):
    norm = re.sub(r"\s+", " ", body.strip().lower())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]


def published_fingerprints():
    seen = set()
    if os.path.exists(LOG):
        for line in open(LOG, encoding="utf-8"):
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3:
                seen.add(parts[2])
    return seen


def lint(body):
    """Run the pack's post linter. Returns (ok, report)."""
    if not os.path.exists(LINTER):
        return True, "linter not found, skipped"
    r = subprocess.run([sys.executable, LINTER], input=body, capture_output=True,
                       text=True, encoding="utf-8")
    fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
    return (not fails), ("\n".join(fails) or "READY")


# ---------------------------------------------------------------- graph api
def call(method, path, fields=None, files=None):
    url = f"{BASE}/{VERSION}/{path.lstrip('/')}"
    fields = dict(fields or {})
    fields["access_token"] = TOKEN
    if method == "GET":
        req = urllib.request.Request(url + "?" + urllib.parse.urlencode(fields))
    elif files:
        boundary = uuid.uuid4().hex
        body = b""
        for k, v in fields.items():
            body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n"
                     f"{v}\r\n").encode("utf-8")
        for k, (name, data) in files.items():
            ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
            body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; "
                     f"filename=\"{name}\"\r\nContent-Type: {ctype}\r\n\r\n").encode("utf-8")
            body += data + b"\r\n"
        body += f"--{boundary}--\r\n".encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    else:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(fields).encode("utf-8"),
                                     method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode("utf-8")).get("error", {})
            msg = f"{err.get('type', 'HTTPError')} {err.get('code', e.code)}: {err.get('message', '')}"
        except Exception:
            msg = f"HTTP {e.code}"
        raise GraphError(redact(msg))
    except urllib.error.URLError as e:
        raise GraphError(redact(f"network error: {e.reason}"))


def publish_one(meta, body):
    kind = meta["type"]
    if kind == "photo":
        img = meta["image"]
        if img.startswith("https://"):
            res = call("POST", f"{PAGE}/photos", {"url": img, "message": body})
        else:
            p = os.path.join(ROOT, img)
            if not os.path.isfile(p):
                raise GraphError(f"image not found in repo: {img}")
            with open(p, "rb") as f:
                res = call("POST", f"{PAGE}/photos", {"message": body},
                           files={"source": (os.path.basename(p), f.read())})
        post_id = res.get("post_id") or res.get("id")
    else:
        fields = {"message": body}
        if kind == "link":
            fields["link"] = meta["link"]
        res = call("POST", f"{PAGE}/feed", fields)
        post_id = res.get("id")
    if not post_id:
        raise GraphError(f"no post id in response: {redact(res)}")
    comment_id = None
    if meta.get("first_comment"):
        c = call("POST", f"{post_id}/comments", {"message": meta["first_comment"]})
        comment_id = c.get("id")
    return post_id, comment_id


# ---------------------------------------------------------------- moving files
def move(path, dest_dir, extra):
    os.makedirs(dest_dir, exist_ok=True)
    raw = open(path, encoding="utf-8").read()
    add = "".join(f"{k}: {v}\n" for k, v in extra.items())
    raw = re.sub(r"^---\s*\n", "---\n" + add, raw, count=1)
    dest = os.path.join(dest_dir, os.path.basename(path))
    with open(dest, "w", encoding="utf-8") as f:
        f.write(raw)
    os.remove(path)
    return dest


def queue_files():
    if not os.path.isdir(QUEUE):
        return []
    return sorted(os.path.join(QUEUE, f) for f in os.listdir(QUEUE)
                  if f.endswith(".md") and not f.startswith("_"))


# ---------------------------------------------------------------- commands
def cmd_list(now):
    files = queue_files()
    if not files:
        print("queue is empty")
    for p in files:
        try:
            meta, body = parse(p)
            due = "DUE" if meta["when"] <= now else f"in {meta['when'] - now}".split(".")[0]
            print(f"{due:<20} {meta['type']:<6} {os.path.basename(p):<34} {body.splitlines()[0][:50]}")
        except ValueError as e:
            print(f"{'INVALID':<20} {'':<6} {os.path.basename(p):<34} {e}")


def cmd_check():
    if not (TOKEN and PAGE):
        sys.exit("FB_PAGE_ID and FB_PAGE_TOKEN must both be set")
    try:
        me = call("GET", PAGE, {"fields": "id,name"})
    except GraphError as e:
        sys.exit(f"CHECK FAILED  {e}")
    print(f"CHECK OK  token can act as Page: {me.get('name')} ({me.get('id')}) on Graph API {VERSION}")


def cmd_publish(now, dry, max_per_run):
    files = queue_files()
    seen = published_fingerprints()
    due = []
    for p in files:
        try:
            meta, body = parse(p)
        except ValueError as e:
            print(f"SKIP  {os.path.basename(p)}: {e}")
            if not dry:
                move(p, FAILED, {"failed_reason": str(e)})
            continue
        if meta["when"] <= now:
            due.append((meta["when"], p, meta, body))
    due.sort()
    if not due:
        print("nothing due")
        return 0
    if not dry and not (TOKEN and PAGE):
        sys.exit("FB_PAGE_ID and FB_PAGE_TOKEN must be set to publish")

    published = errors = 0
    for when, p, meta, body in due:
        name = os.path.basename(p)
        if published >= max_per_run:
            print(f"WAIT  {name}: max {max_per_run} per run, next run picks it up")
            continue
        reason = None
        if "{{" in body or "{{" in meta.get("first_comment", ""):
            reason = "still has a {{placeholder}}; fill it in before it can go out"
        elif fingerprint(body) in seen:
            reason = "exact duplicate of a post already published"
        else:
            ok, report = lint(body)
            if not ok:
                reason = "linter FAIL: " + report.replace("\n", " | ")
        if reason:
            errors += 1
            print(f"REFUSE {name}: {reason}")
            if not dry:
                move(p, FAILED, {"failed_reason": reason})
            continue
        if dry:
            print(f"DRY   {name}: would publish {meta['type']} post")
            continue
        try:
            post_id, comment_id = publish_one(meta, body)
        except GraphError as e:
            errors += 1
            print(f"ERROR {name}: {e}")
            if "OAuthException" in str(e) or " 190" in str(e):
                print("      the token was rejected; regenerate it (see automation/SETUP.md)")
                return 1
            move(p, FAILED, {"failed_reason": str(e)})
            continue
        stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        month = now.strftime("%Y-%m")
        move(p, os.path.join(DONE, month),
             {"post_id": post_id, "published_at": stamp, **({"comment_id": comment_id} if comment_id else {})})
        os.makedirs(DONE, exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{stamp}\t{post_id}\t{fingerprint(body)}\t{meta['type']}\t{body.splitlines()[0][:80]}\n")
        seen.add(fingerprint(body))
        published += 1
        print(f"POSTED {name}: {post_id}" + (" + first comment" if comment_id else ""))
    print(f"done: {published} published, {errors} refused or failed")
    return 1 if errors and not published else 0


def main():
    ap = argparse.ArgumentParser(description="Publish due posts from queue/.")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--now", help="pretend it is this time (ISO 8601), for testing")
    a = ap.parse_args()
    now = parse_time(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    if a.check:
        return cmd_check()
    if a.list:
        return cmd_list(now)
    dry = os.environ.get("DRY_RUN", "") not in ("", "0", "false")
    sys.exit(cmd_publish(now, dry, int(os.environ.get("MAX_PER_RUN", "2"))))


if __name__ == "__main__":
    main()
