#!/usr/bin/env python3
"""Print the comment language of a repository: ko or en (see SKILL.md Step 1).

Reads the titles and bodies of recent PRs and recent PR review comments, skips
bot authors, and strips code, links, and HTML comments (PR template hints).
Each remaining text votes: ko when Hangul makes up at least 20% of its letters,
otherwise en. More ko votes than en votes prints ko; anything else prints en,
because en is the fallback for every language other than Korean.

The counts go to stderr so the decision can be checked.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

STRIP = re.compile(r"```.*?```|`[^`\n]*`|<!--.*?-->|https?://\S+", re.S)
HANGUL = re.compile(r"[가-힣ㄱ-ㆎ]")
LATIN = re.compile(r"[A-Za-z]")
MIN_LETTERS = 10  # shorter texts ("WIP", "LGTM") say nothing about the language


def gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, encoding="utf-8")
    if result.returncode != 0:
        sys.exit(f"gh {' '.join(args[:3])} failed: {result.stderr.strip()}")
    return result.stdout


def vote(text: str) -> str | None:
    text = STRIP.sub(" ", text or "")
    hangul, latin = len(HANGUL.findall(text)), len(LATIN.findall(text))
    if hangul + latin < MIN_LETTERS:
        return None
    return "ko" if hangul >= 0.2 * (hangul + latin) else "en"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="owner/repo")
    parser.add_argument("--limit", type=int, default=20, help="recent PRs and review comments to read")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    texts = []
    prs = json.loads(
        gh("pr", "list", "--repo", args.repo, "--state", "all", "--limit", str(args.limit),
           "--json", "title,body,author")
    )
    for pr in prs:
        if not pr["author"].get("is_bot"):
            texts += [pr["title"], pr["body"]]
    comments = json.loads(
        gh("api", f"repos/{args.repo}/pulls/comments?sort=created&direction=desc&per_page={args.limit}")
    )
    texts += [c["body"] for c in comments if (c.get("user") or {}).get("type") != "Bot"]

    votes = [v for v in map(vote, texts) if v]
    ko, en = votes.count("ko"), votes.count("en")
    print(f"{args.repo}: ko {ko}, en {en} (from {len(prs)} PRs, {len(comments)} review comments)", file=sys.stderr)
    print("ko" if ko > en else "en")


if __name__ == "__main__":
    main()
