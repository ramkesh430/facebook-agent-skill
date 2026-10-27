# Changelog

## 1.2.1 - 2026-10-27

- Autopilot drafting moved off GitHub Models (retired 30 July 2026) to any OpenAI-compatible API.
  Default: Google Gemini free tier (`LLM_API_KEY` secret). Groq via the `LLM_BASE_URL` variable.
- `model: auto` picks the best model the provider lists; clear errors for missing/bad keys and rate limits.
- Tests: 33 autopilot checks.

## 1.2.0 - 2026-10-27

- **Autopilot** (`automation/`): free weekly drafting with an LLM API, approval by merging a pull
  request, and hourly publishing to a Facebook Page through the Graph API (v26.0). Text, link and
  photo posts, with a first comment. Refuses placeholders, linter FAILs and duplicates.
- `automation/get_page_token.py`: turns a short-lived token into a non-expiring Page token, locally.
- `automation/SETUP.md`: step-by-step setup.
- `templates/ideas.md`: the weekly facts file the drafts are built from.
- `tests/test_automation.py`: end-to-end checks against mock Graph API and LLM servers.

## 1.1.0 - 2026-10-27

- New skill `/fb-live`: plan and script a Facebook Live, from announcement to replay clips.
- New skill `/fb-boost`: decide whether a post is worth boosting and write the boost/ad copy. Never spends.
- Nepali engagement-bait detection (romanized and Devanagari) in `post.py`, `hookscore.py` and the humanizer.
- `examples/` with sample hooks, a script, posts (English and Nepali) and a captured TSV.
- `tests/run_tests.py`: 49 end-to-end checks, run on every push by GitHub Actions.
- README: one-step plugin install line.

## 1.0.0 - 2026-10-27

- First release: 14 skills, hook scorer, beat sheet, post linter, humanizer, detector, swipe file ranking, Page rubric.
