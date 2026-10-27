# Facebook autopilot: setup

Free, runs on GitHub. Every week it drafts your posts, you approve them with
one tap, and it posts each one to your Facebook Page at its time.

```
Saturday 08:08 (Nepal)   generate.yml drafts next week's posts with Gemini (free tier)
                         -> opens a pull request; GitHub emails you
You                      read the drafts on your phone, edit if needed, tap Merge
Every hour               publish.yml posts anything that's due through the Graph API,
                         adds the first comment, records the post id
```

Cost: 0. GitHub Actions free minutes, Gemini API free tier (no card), Meta Graph API.

What it does **not** automate, on purpose:

- **Reels and video.** They need your face and your footage. Use `/fb-reel` and post them yourself.
- **Comments, Messenger, Groups.** Automating replies outside Meta's own tools breaks the Terms.
  Use Meta Business Suite's free automations for instant replies and FAQs.
- **Approval.** Nothing is posted that you didn't merge.

## One-time setup (about 30 minutes)

### 1. The repo (private)

Create a **private** repo from this template (your drafts shouldn't be public
before they're posted). Then:

- copy `automation/workflows/publish.yml` and `generate.yml` into `.github/workflows/`
- copy `templates/voice.md` to `brand/voice.md` and fill it in
- copy `templates/ideas.md` to `brand/ideas.md` and fill it in
- Settings > Actions > General > Workflow permissions: tick
  **Allow GitHub Actions to create and approve pull requests**

### 2. A Meta app (free, stays in development mode)

1. Go to developers.facebook.com, log in with the Facebook account that is
   admin of your Page, and **Create app**.
2. Use case: choose the one for **managing everything on your Page** (Pages API).
3. In the app, open **Graph API Explorer**. Pick your app, then add permissions:
   `pages_show_list`, `pages_manage_posts`, `pages_read_engagement`,
   `pages_manage_engagement`. Click **Generate Access Token** and choose your Page
   in the dialog.
4. Copy that (short-lived) token.

Your own Page works while the app is in development mode, because you are the
app's admin. No app review is needed for this.

### 3. A Page token that doesn't expire

On your own computer:

```bash
python3 automation/get_page_token.py
```

It asks for the App ID, App Secret (Settings > Basic) and the token from step
2, and prints `FB_PAGE_ID` and `FB_PAGE_TOKEN`. It saves nothing.

### 4. A free AI key (Gemini)

1. Go to aistudio.google.com, sign in with a Google account, click **Get API key** > **Create API key**.
2. No card is needed for the free tier. Note: on the free tier Google may use prompts to improve its products, so don't put anything secret in `brand/`.

Prefer Groq? Create a key at console.groq.com, and add a repo **variable** (not secret) `LLM_BASE_URL` = `https://api.groq.com/openai/v1`.

### 5. Secrets

Private repo > Settings > Secrets and variables > Actions > **New repository secret**:

| name | value |
|---|---|
| `FB_PAGE_ID` | the id from step 3 |
| `FB_PAGE_TOKEN` | the token from step 3 |
| `LLM_API_KEY` | the Gemini (or Groq) key from step 4 |

Never paste the token into a chat, an issue, a commit or a file.

### 6. Test

- Actions > **publish** > Run workflow > tick "Only check" > Run. It should
  say `CHECK OK  token can act as Page: <your Page>`.
- Actions > **generate** > Run workflow. A pull request with drafts appears.
  Read it, edit any file, merge.
- At the next hour after a draft's time, **publish** posts it. Check your Page.

## Day to day

- **Saturday**: GitHub emails you a PR. Fix any `{{...}}` (a fact the drafts
  needed and didn't have), edit what you don't like, merge. Close it to skip a week.
- **Any time**: add a post by hand: create `queue/2026-11-05-1830-anything.md`:

  ```
  ---
  publish_at: 2026-11-05T18:30:00+05:45
  type: text
  first_comment: optional
  ---
  Your post.
  ```

  `type: photo` with `image: brand/images/x.jpg` (upload the image to the repo)
  or an https URL. `type: link` with `link: https://...`.
- **Change the schedule**: `automation/config.json` (`slots`, `timezone`, `model`; `auto` picks the best free model the provider lists).
- **See what went out**: `published/` and `published/log.tsv`.
- **See what was refused**: `failed/`, each file says why (linter FAIL,
  placeholder left in, duplicate, API error).

## Safety built in

- Merge = approval. Unmerged drafts never publish.
- Posts with a `{{placeholder}}` are refused.
- Every post is linted again right before publishing; any FAIL (engagement
  bait in English or Nepali, greeting opener, hashtag wall) is refused.
- Exact duplicates of anything already posted are refused.
- At most 2 posts per hourly run.
- A rejected token stops the run and leaves the post in the queue.
- The token is only read from the secret and is redacted from all output.

## When something breaks

| symptom | fix |
|---|---|
| `CHECK FAILED ... 190` | token expired or revoked (password change, app removed). Redo steps 2-4. |
| `(#200) ... permission` | regenerate the token with all four permissions and pick the Page. |
| generate: `rate limit` | the free tier is used up for now; re-run later or wait for the weekly run. |
| generate: `API key rejected` / `could not list models` | regenerate the Gemini key and update `LLM_API_KEY`. |
| generate: `voice.md ... blank` | fill in `brand/voice.md`. |
| no PR opened | the "Allow GitHub Actions to create pull requests" setting is off. |
| scheduled runs stopped | GitHub pauses schedules after 60 days with no repo activity; publishing keeps it active, or re-enable in Actions. |
