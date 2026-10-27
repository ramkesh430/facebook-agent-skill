#!/usr/bin/env python3
"""test_automation.py - run publish.py and generate.py end to end against
local mock servers that imitate the Graph API and an OpenAI-compatible LLM API
(the shape Gemini and Groq both expose).

Nothing touches the real Facebook or any AI provider. The scripts run
unmodified; only GRAPH_BASE and LLM_BASE_URL point at localhost.

    python3 tests/test_automation.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
calls = []
passed, failed = 0, []

GOOD_POST = ("We sold 46 birthday cakes in Patan last week, our best week since March.\n\n"
             "The reason was boring: we started answering every message within an hour.\n\n"
             "Message us your date and we'll tell you what's still free.")
BAIT_POST = ("New cakes in Patan this week, 3 flavours.\n\nLike garnus ra sathi lai tag garnus!")
FIXED_POST = ("New cakes in Patan this week, 3 flavours: mango, coffee and black forest.\n\n"
              "Which one should we make a bigger size of?")


class Mock(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def reply(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path == "/llm/models":
            calls.append(("LIST", self.headers.get("Authorization", "")))
            if self.headers.get("Authorization") != "Bearer test-key":
                return self.reply(401, {"error": {"message": "API key not valid"}})
            return self.reply(200, {"object": "list", "data": [
                {"id": "models/gemini-2.5-flash-lite"}, {"id": "models/gemini-2.5-flash"},
                {"id": "models/embedding-001"}]})
        calls.append(("GET", u.path, q))
        if q.get("access_token", [""])[0] == "BAD":
            return self.reply(400, {"error": {"type": "OAuthException", "code": 190, "message": "Invalid token"}})
        self.reply(200, {"id": "123", "name": "Test Bakery"})

    def do_POST(self):
        u = urlparse(self.path)
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n)
        ctype = self.headers.get("Content-Type", "")
        if u.path == "/llm/chat/completions":
            body = json.loads(raw)
            calls.append(("MODELS", body["model"], body["messages"][-1]["content"][:60]))
            if "linter failed" in body["messages"][-1]["content"]:
                posts = [{"slot": 1, "type": "text", "text": FIXED_POST}]
            else:
                posts = [{"slot": 1, "type": "text", "text": GOOD_POST, "uses": "46 cakes"},
                         {"slot": 2, "type": "text", "text": BAIT_POST, "uses": "new flavours"},
                         {"slot": 3, "type": "text", "text": "Our {{new opening hours}} start next week in Patan.", "uses": "hours"}]
            # wrap in a code fence like Gemini sometimes does
            return self.reply(200, {"choices": [{"message": {"content": "```json\n" + json.dumps({"posts": posts}) + "\n```"}}]})
        if "multipart" in ctype:
            fields = {"_multipart": True, "has_source": b'name="source"' in raw,
                      "token": re.search(rb'name="access_token"\r\n\r\n([^\r]*)', raw).group(1).decode()}
        else:
            fields = {k: v[0] for k, v in parse_qs(raw.decode()).items()}
            fields["token"] = fields.pop("access_token", "")
        calls.append(("POST", u.path, fields))
        if fields["token"] == "BAD":
            return self.reply(400, {"error": {"type": "OAuthException", "code": 190, "message": "Invalid token"}})
        if u.path.endswith("/feed"):
            return self.reply(200, {"id": "123_900"})
        if u.path.endswith("/photos"):
            return self.reply(200, {"id": "555", "post_id": "123_901"})
        if u.path.endswith("/comments"):
            return self.reply(200, {"id": "c_1"})
        self.reply(404, {"error": {"message": "unknown"}})


def check(name, cond, detail=""):
    global passed
    if cond:
        passed += 1
        print(f"PASS  {name}")
    else:
        failed.append(name)
        print(f"FAIL  {name}  {detail}")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    srv = HTTPServer(("127.0.0.1", 0), Mock)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    tmp = tempfile.mkdtemp()
    repo = os.path.join(tmp, "repo")
    shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__", "queue", "published", "failed"))
    env = dict(os.environ, GRAPH_BASE=f"http://127.0.0.1:{port}", FB_PAGE_ID="123",
               FB_PAGE_TOKEN="GOODTOKEN", LLM_BASE_URL=f"http://127.0.0.1:{port}/llm",
               LLM_API_KEY="test-key")
    pub = os.path.join(repo, "automation", "publish.py")
    gen = os.path.join(repo, "automation", "generate.py")

    def run(script, *args, **extra):
        e = dict(env, **extra)
        return subprocess.run([PY, script, *args], capture_output=True, text=True, env=e, cwd=repo)

    try:
        # --- check
        r = run(pub, "--check")
        check("publish --check OK", r.returncode == 0 and "Test Bakery" in r.stdout, r.stdout + r.stderr)
        r = run(pub, "--check", FB_PAGE_TOKEN="BAD")
        check("publish --check rejects bad token", r.returncode != 0 and "190" in (r.stdout + r.stderr))
        check("token never printed", "GOODTOKEN" not in r.stdout + r.stderr)

        # --- queue: due text with first comment, due photo, future post, placeholder, bait, duplicate
        q = os.path.join(repo, "queue")
        write(os.path.join(q, "a-text.md"), "---\npublish_at: 2026-11-02T18:30:00+05:45\ntype: text\n"
              "first_comment: Menu: https://example.com/menu #cakes\n---\n" + GOOD_POST + "\n")
        write(os.path.join(repo, "brand", "images", "cake.jpg"), "fakejpegbytes")
        write(os.path.join(q, "b-photo.md"), "---\npublish_at: 2026-11-02T19:00:00+05:45\ntype: photo\n"
              "image: brand/images/cake.jpg\n---\nFresh mango cake in Patan today, 12 slices left.\n")
        write(os.path.join(q, "c-future.md"), "---\npublish_at: 2030-01-01T10:00:00+05:45\n---\nLater post in Kathmandu.\n")
        write(os.path.join(q, "d-placeholder.md"), "---\npublish_at: 2026-11-01T10:00:00+05:45\n---\nOpen until {{closing time}} in Patan.\n")
        write(os.path.join(q, "e-bait.md"), "---\npublish_at: 2026-11-01T11:00:00+05:45\n---\nNew cake! Like garnus ra share garnus.\n")
        write(os.path.join(q, "f-bad.md"), "no front matter at all\n")

        r = run(pub, "--list", "--now", "2026-11-03T00:00:00+05:45")
        check("publish --list shows due and future", "DUE" in r.stdout and "in " in r.stdout and "INVALID" in r.stdout)

        r = run(pub, "--now", "2026-11-03T00:00:00+05:45", DRY_RUN="1")
        check("dry run publishes nothing", not any(c[0] == "POST" for c in calls) and "DRY" in r.stdout, r.stdout)
        check("dry run moves nothing", os.path.exists(os.path.join(q, "a-text.md")))

        calls.clear()
        r = run(pub, "--now", "2026-11-03T00:00:00+05:45")
        out = r.stdout
        posts = [c for c in calls if c[0] == "POST"]
        feed = [c for c in posts if c[1].endswith("/123/feed")]
        photo = [c for c in posts if c[1].endswith("/123/photos")]
        comments = [c for c in posts if c[1].endswith("/comments")]
        check("text post published to /feed", len(feed) == 1 and feed[0][2]["message"].startswith("We sold 46"), str(posts))
        check("uses Graph API v26.0", feed and feed[0][1].startswith("/v26.0/"))
        check("first comment added (hashtag kept)", len(comments) == 1 and comments[0][1] == "/v26.0/123_900/comments"
              and comments[0][2]["message"].endswith("#cakes"))
        check("photo uploaded as multipart with source", len(photo) == 1 and photo[0][2].get("has_source"))
        check("placeholder refused", "d-placeholder.md: still has a {{placeholder}}" in out, out)
        check("Nepali bait refused by linter", "REFUSE e-bait.md: linter FAIL" in out, out)
        check("invalid file skipped", "SKIP  f-bad.md" in out)
        check("future post left in queue", os.path.exists(os.path.join(q, "c-future.md")))
        pubdir = os.path.join(repo, "published", "2026-11")
        moved = open(os.path.join(pubdir, "a-text.md")).read() if os.path.exists(os.path.join(pubdir, "a-text.md")) else ""
        check("published file moved with post_id", "post_id: 123_900" in moved and "comment_id: c_1" in moved)
        check("refused files moved to failed/", os.path.exists(os.path.join(repo, "failed", "e-bait.md")))
        check("log.tsv written", os.path.exists(os.path.join(repo, "published", "log.tsv")))

        # duplicate guard
        write(os.path.join(q, "g-dup.md"), "---\npublish_at: 2026-11-02T20:00:00+05:45\n---\n" + GOOD_POST + "\n")
        calls.clear()
        r = run(pub, "--now", "2026-11-03T00:00:00+05:45")
        check("duplicate refused", "REFUSE g-dup.md: exact duplicate" in r.stdout and not calls, r.stdout)

        # max per run
        for i in range(3):
            write(os.path.join(q, f"h{i}.md"), f"---\npublish_at: 2026-11-02T2{i}:00:00+05:45\n---\nPost number {i + 1} from Patan, {i + 10} cakes.\n")
        r = run(pub, "--now", "2026-11-03T00:00:00+05:45")
        check("max 2 per run", r.stdout.count("POSTED") == 2 and "WAIT" in r.stdout, r.stdout)

        # bad token stops the run without moving the file
        r = run(pub, "--now", "2026-11-03T00:00:00+05:45", FB_PAGE_TOKEN="BAD")
        check("bad token stops run, keeps post queued", r.returncode != 0 and os.path.exists(os.path.join(q, "h2.md")), r.stdout)

        # --- generate
        write(os.path.join(repo, "brand", "voice.md"),
              "- **Name:** Test Bakery\n- **Where I serve:** Patan\n- **What I sell:** cakes\n- **Proof:** 46 cakes last week\n")
        write(os.path.join(repo, "brand", "ideas.md"), "- 46 birthday cakes last week\n- new flavours: mango, coffee, black forest\n")
        before = set(os.listdir(q))
        calls.clear()
        r = run(gen, "--summary", os.path.join(tmp, "pr.md"), "--now", "2026-10-31T02:23:00+00:00")
        new = sorted(set(os.listdir(q)) - before)
        check("generate runs", r.returncode == 0, r.stdout + r.stderr)
        check("generate wrote 3 drafts", len(new) == 3, str(new))
        model_calls = [c for c in calls if c[0] == "MODELS"]
        check("bait draft got one repair call", len(model_calls) == 2, str(model_calls))
        texts = [open(os.path.join(q, f)).read() for f in new]
        check("no bait in any draft", not any("garnus" in t for t in texts))
        check("drafts scheduled in Nepal time", all("+05:45" in t for t in texts))
        check("drafts after the 12h review window", all(f >= "2026-11-01" for f in new), str(new))
        pr = open(os.path.join(tmp, "pr.md")).read()
        check("PR body flags {{placeholder}} draft", "needs your input" in pr)
        r2 = run(pub, "--list", "--now", "2026-10-31T09:00:00+05:45")
        check("drafts parse in publish.py", "INVALID" not in r2.stdout, r2.stdout)
        check("auto-picked gemini-2.5-flash from /models", model_calls and model_calls[0][1] == "gemini-2.5-flash", str(model_calls))
        check("PR body names the model", "gemini-2.5-flash" in pr)

        # missing / bad key
        r = run(gen, "--dry-run", LLM_API_KEY="")
        check("generate explains missing key", r.returncode != 0 and "LLM_API_KEY" in r.stderr, r.stderr)
        r = run(gen, "--dry-run", LLM_API_KEY="wrong")
        check("generate explains bad key", r.returncode != 0 and "401" in r.stderr and "wrong" not in r.stderr, r.stderr)

        # blank voice is refused
        shutil.copy(os.path.join(ROOT, "templates", "voice.md"), os.path.join(repo, "brand", "voice.md"))
        r = run(gen, "--dry-run")
        check("generate refuses blank voice.md", r.returncode != 0 and "voice.md" in r.stderr, r.stderr)
    finally:
        srv.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)

    print("-" * 60)
    print(f"{passed} passed, {len(failed)} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
