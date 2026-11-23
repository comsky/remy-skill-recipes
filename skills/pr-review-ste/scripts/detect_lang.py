#!/usr/bin/env python3
"""Print the comment language of a repository: ko or en (see SKILL.md Step 1).

Reads the bodies of recent PRs and recent PR review comments. PR titles are
left out: many teams write Conventional Commits titles in English and discuss
in another language. Bot authors and comments this skill posted earlier
(starting with a priority mark such as `💡 **P2**`) are left out too. Code,
links, and HTML comments (PR template hints) are stripped, closed or not.

Each remaining text votes: ko when Hangul makes up at least 20% of its letters,
otherwise en. More ko votes prints ko; more en votes prints en. A tie (also
0 to 0) falls back to the README's vote, then to en. Every language other than
Korean counts as en.

The counts and the deciding source go to stderr so the decision can be checked.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys

STRIP = re.compile(r"```.*?(?:```|\Z)|`[^`\n]*`|<!--.*?(?:-->|\Z)|https?://\S+", re.S)
HANGUL = re.compile(r"[가-힣ㄱ-ㆎ]")
LATIN = re.compile(r"[A-Za-z]")
# Priority marks of this skill, current and earlier versions.
OWN_COMMENT = re.compile(r"^\s*(?:🚨|⚠️|💡|💬|🔴|🟠|🟡|⚪)\s*\*\*P[0-3]\*\*")
MIN_LETTERS = 10  # shorter texts ("WIP", "LGTM") say nothing about the language
MAX_LIMIT = 100  # GitHub's page size; the review comment call does not paginate


def gh(*args: str, check: bool = True) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, encoding="utf-8")
    if result.returncode != 0:
        if not check:
            return ""
        sys.exit(f"gh {' '.join(args[:3])} failed: {result.stderr.strip()}")
    return result.stdout


def vote(text: str) -> str | None:
    text = STRIP.sub(" ", text or "")
    hangul, latin = len(HANGUL.findall(text)), len(LATIN.findall(text))
    if hangul + latin < MIN_LETTERS:
        return None
    return "ko" if hangul >= 0.2 * (hangul + latin) else "en"


def limit(value: str) -> int:
    n = int(value)
    if not 1 <= n <= MAX_LIMIT:
        raise argparse.ArgumentTypeError(f"use 1 to {MAX_LIMIT}")
    return n


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repo", help="owner/repo")
    parser.add_argument("--limit", type=limit, default=20, help=f"recent PRs and review comments to read (1-{MAX_LIMIT})")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    texts = []
    prs = json.loads(
        gh("pr", "list", "--repo", args.repo, "--state", "all", "--limit", str(args.limit), "--json", "body,author")
    )
    texts += [pr["body"] for pr in prs if not pr["author"].get("is_bot")]
    comments = json.loads(
        gh("api", f"repos/{args.repo}/pulls/comments?sort=created&direction=desc&per_page={args.limit}")
    )
    texts += [
        c["body"]
        for c in comments
        if (c.get("user") or {}).get("type") != "Bot" and not OWN_COMMENT.match(c["body"] or "")
    ]

    votes = [v for v in map(vote, texts) if v]
    ko, en = votes.count("ko"), votes.count("en")
    if ko != en:
        lang, source = ("ko" if ko > en else "en"), "PRs and review comments"
    else:
        readme = json.loads(gh("api", f"repos/{args.repo}/readme", check=False) or "{}")
        text = base64.b64decode(readme["content"]).decode("utf-8", "replace") if readme.get("content") else ""
        lang, source = (vote(text), "README (PR votes tied)")
        if not lang:
            lang, source = "en", "default (no signal: PR votes tied, no readable README)"
    print(
        f"{args.repo}: ko {ko}, en {en} (from {len(prs)} PRs, {len(comments)} review comments); decided by {source}",
        file=sys.stderr,
    )
    print(lang)


if __name__ == "__main__":
    main()
