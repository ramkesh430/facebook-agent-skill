#!/usr/bin/env python3
"""get_page_token.py - turn a short-lived token into a Page token that doesn't expire.

Run this ON YOUR OWN COMPUTER, once. It asks for three things and never saves
them anywhere:

  1. your Meta app's App ID           (developers.facebook.com > your app > Settings > Basic)
  2. your Meta app's App Secret       (same page; click Show)
  3. a short-lived User access token  (Graph API Explorer, with pages_show_list,
                                       pages_manage_posts, pages_read_engagement,
                                       pages_manage_engagement)

It exchanges (3) for a 60-day user token, then asks Facebook for your Pages.
A Page token obtained from a long-lived user token does not expire (until you
change your password, remove the app, or lose admin on the Page).

It prints each Page's id and token. Copy the one you want into GitHub:
  repo > Settings > Secrets and variables > Actions > New repository secret
    FB_PAGE_ID     = the id
    FB_PAGE_TOKEN  = the token
Then close the terminal. Never paste the token into a chat, an issue or a file.

Standard library only.
"""
import getpass
import json
import os
import urllib.error
import urllib.parse
import urllib.request

VERSION = os.environ.get("GRAPH_VERSION", "v26.0")
BASE = f"https://graph.facebook.com/{VERSION}"


def get(path, params):
    url = f"{BASE}/{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode("utf-8")).get("error", {})
        raise SystemExit(f"Facebook said: {err.get('message', e.code)}")


def main():
    app_id = input("App ID: ").strip()
    secret = getpass.getpass("App Secret (hidden): ").strip()
    short = getpass.getpass("Short-lived User token (hidden): ").strip()
    long_user = get("oauth/access_token", {
        "grant_type": "fb_exchange_token", "client_id": app_id,
        "client_secret": secret, "fb_exchange_token": short})["access_token"]
    pages = get("me/accounts", {"access_token": long_user, "fields": "id,name,access_token,tasks"})
    data = pages.get("data", [])
    if not data:
        raise SystemExit("No Pages found. Did you grant pages_show_list and pick your Page in the login dialog?")
    for p in data:
        can = "CREATE_CONTENT" in (p.get("tasks") or [])
        print("\n" + "=" * 60)
        print(f"Page:   {p['name']}")
        print(f"FB_PAGE_ID     {p['id']}")
        print(f"FB_PAGE_TOKEN  {p['access_token']}")
        if not can:
            print("WARNING: you can't create content on this Page with this login.")
    print("\nCopy FB_PAGE_ID and FB_PAGE_TOKEN into GitHub secrets, then close this window.")


if __name__ == "__main__":
    main()
