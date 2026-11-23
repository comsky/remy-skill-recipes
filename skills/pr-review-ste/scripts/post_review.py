#!/usr/bin/env python3
"""Post one PR review from a findings JSON file (see SKILL.md Step 5).

Inline comments go on lines inside the PR diff; findings on other lines move
into the review body. Any P0 makes the review REQUEST_CHANGES; findings that are
all P3 (or none) make it APPROVE; anything else is COMMENT. An own PR never
requests changes or approves.

With --fix-report, post one PR comment instead: each finding's `outcome`
(fixed | skipped | no_change_needed) and the fix commit `fix_sha`, which must
already be the PR head (see SKILL.md Step 6).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from urllib.parse import quote

PRIORITIES = ("P0", "P1", "P2", "P3")
MARK = {"P0": "🚨", "P1": "⚠️", "P2": "💡", "P3": "💬"}
LABEL = {"P0": "차단", "P1": "머지 전 수정", "P2": "수정 권장", "P3": "선택"}
OUTCOME = {"fixed": "✅ 수정", "skipped": "⏭️ 건너뜀", "no_change_needed": "➖ 변경 불필요"}


def gh(*args: str, stdin: str | None = None) -> str:
    result = subprocess.run(["gh", *args], input=stdin, capture_output=True, encoding="utf-8")
    if result.returncode != 0:
        sys.exit(f"gh {' '.join(args[:3])} failed: {result.stderr.strip()}")
    return result.stdout


def diff_right_lines(diff: str) -> dict[str, set[int]]:
    """Lines a RIGHT-side review comment can anchor to: added and context lines per file."""
    lines: dict[str, set[int]] = {}
    path, line, in_hunk = None, 0, False
    for raw in diff.split("\n"):  # not splitlines(): it also splits on \f, \x85, \u2028 inside a line
        if raw.startswith("diff --git "):
            path, in_hunk = None, False
        elif not in_hunk and raw.startswith("+++ "):  # inside a hunk, "+++ " is an added "++ " line
            name = raw[4:].removesuffix("\t")  # git appends a tab when the path has a space
            if name.startswith('"'):  # git C-quotes non-ASCII paths with octal escapes
                name = name[1:-1].encode("latin-1").decode("unicode_escape").encode("latin-1").decode("utf-8")
            path = name[2:] if name.startswith("b/") else None
            if path:
                lines.setdefault(path, set())
        elif m := re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", raw):
            line, in_hunk = int(m.group(1)), True
        elif path and raw[:1] in ("+", " "):
            lines[path].add(line)
            line += 1
    return lines


def validate(data: dict) -> list[dict]:
    for key in ("repo", "number", "head_sha", "findings"):
        if key not in data:
            sys.exit(f"findings JSON is missing '{key}'")
    findings = data["findings"]
    for i, f in enumerate(findings):
        missing = [k for k in ("priority", "file", "line", "title", "body") if k not in f]
        if missing:
            sys.exit(f"finding {i} is missing {missing}")
        if f["priority"] not in PRIORITIES:
            sys.exit(f"finding {i} has priority {f['priority']!r}; use one of {PRIORITIES}")
        if not isinstance(f["line"], int) or f["line"] < 1:
            sys.exit(f"finding {i} needs a positive integer line")
        if not isinstance(f["title"], str) or not f["title"].strip() or not isinstance(f["body"], str):
            sys.exit(f"finding {i} needs a non-empty string title and a string body")
    return sorted(findings, key=lambda f: PRIORITIES.index(f["priority"]))


def validate_outcomes(data: dict) -> None:
    findings = data["findings"]  # file order, so the index matches the JSON
    if not findings:
        sys.exit("no findings: there is no outcome to report")
    for i, f in enumerate(findings):
        if f.get("outcome") not in OUTCOME:
            sys.exit(f"finding {i} needs outcome in {tuple(OUTCOME)}")
        if f["outcome"] != "fixed" and not (isinstance(f.get("reason"), str) and f["reason"].strip()):
            sys.exit(f"finding {i} is {f['outcome']}; give it a reason")
    if any(f["outcome"] == "fixed" for f in findings) and not data.get("fix_sha"):
        sys.exit("a fixed finding needs top-level fix_sha")


def cell(text: str) -> str:
    """Keep free text inside one table cell."""
    return re.sub(r"\s*\n\s*", " ", text.strip()).replace("|", "\\|")


def build_fix_report(data: dict, findings: list[dict]) -> str:
    blob = f"https://github.com/{data['repo']}/blob/{data['head_sha']}"
    rows = [
        f"| {label} | {n} |"
        for key, label in OUTCOME.items()
        if (n := sum(f["outcome"] == key for f in findings))
    ]
    lines = ["| 결과 | 건수 |", "| --- | ---: |", *rows, ""]
    if sha := data.get("fix_sha"):
        lines.append(f"수정 커밋: [`{sha[:9]}`](https://github.com/{data['repo']}/commit/{sha})")
    lines += ["", "| 결과 | 우선순위 | 지적 | 위치 | 사유 |", "| --- | --- | --- | --- | --- |"]
    for f in findings:
        where = f"[`{f['file'].rsplit('/', 1)[-1]}:{f['line']}`]({blob}/{quote(f['file'])}#L{f['line']})"
        reason = cell(f["reason"]) if f["outcome"] != "fixed" else ""
        lines.append(
            f"| {OUTCOME[f['outcome']]} | {MARK[f['priority']]} {f['priority']} | {cell(f['title'])} | {where} | {reason} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def build(data: dict, findings: list[dict], diff: str, own_pr: bool) -> dict:
    anchorable = diff_right_lines(diff)
    inline, outside = [], []
    for f in findings:
        (inline if f["line"] in anchorable.get(f["file"], ()) else outside).append(f)

    has_p0 = any(f["priority"] == "P0" for f in findings)
    groups = {p: [f for f in findings if f["priority"] == p] for p in PRIORITIES}
    # The body states findings only: no skill, command, level or method names.
    rows = [f"| {MARK[p]} {p} {LABEL[p]} | {len(g)} |" for p, g in groups.items() if g]
    lines = ["| 우선순위 | 건수 |", "| --- | ---: |", *rows] if rows else ["지적할 항목이 없습니다."]
    blob = f"https://github.com/{data['repo']}/blob/{data['head_sha']}"
    if findings:
        lines += ["", "| 우선순위 | 지적 | 위치 |", "| --- | --- | --- |"]
    details = []
    for f in findings:  # validate() sorted these by priority
        where = f"[`{f['file'].rsplit('/', 1)[-1]}:{f['line']}`]({blob}/{quote(f['file'])}#L{f['line']})"
        lines.append(f"| {MARK[f['priority']]} {f['priority']} | {cell(f['title'])} | {where} |")
        if f in outside:  # no inline comment can carry the detail
            details += ["", f"**{MARK[f['priority']]} {f['priority']} {where}**", "", f["body"].strip()]
    lines += details

    only_p3 = all(f["priority"] == "P3" for f in findings)
    event = "REQUEST_CHANGES" if has_p0 else "APPROVE" if only_p3 else "COMMENT"
    if only_p3 and own_pr:
        event = "COMMENT"
    if has_p0 and own_pr:
        event = "COMMENT"
        lines += ["", "> P0 가 있으나 본인 PR 이라 변경 요청 대신 댓글로 남깁니다."]

    return {
        "commit_id": data["head_sha"],
        "event": event,
        "body": "\n".join(lines).rstrip() + "\n",
        "comments": [
            {
                "path": f["file"],
                "line": f["line"],
                "side": "RIGHT",
                "body": f"{MARK[f['priority']]} **{f['priority']}** {f['title']}\n\n{f['body'].strip()}",
            }
            for f in inline
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("findings", help="findings JSON file")
    parser.add_argument("--dry-run", action="store_true", help="print the payload, post nothing")
    parser.add_argument("--fix-report", action="store_true", help="post the fix outcomes as a PR comment")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # a piped stdout on Windows defaults to the locale code page

    with open(args.findings, encoding="utf-8") as fh:
        data = json.load(fh)
    findings = validate(data)
    repo, number = data["repo"], str(data["number"])

    pr = json.loads(
        gh("pr", "view", number, "--repo", repo, "--json", "state,isDraft,headRefOid,author")
    )
    if pr["state"] != "OPEN":
        sys.exit(f"skip: {repo}#{number} is {pr['state']}")
    if pr["isDraft"]:
        sys.exit(f"skip: {repo}#{number} is a draft")
    if args.fix_report:
        validate_outcomes(data)
        expected = data.get("fix_sha") or data["head_sha"]
        if pr["headRefOid"] != expected:
            sys.exit(
                f"stop: {repo}#{number} head is {pr['headRefOid'][:9]}, expected {expected[:9]}; "
                "wait for the pushed fix to show on the PR, or re-check a concurrent push"
            )
        body = build_fix_report(data, findings)
        if args.dry_run:
            print(body)
            print(f"{repo}#{number}: fix report (dry run)", file=sys.stderr)
            return
        result = json.loads(
            gh("api", "-X", "POST", f"repos/{repo}/issues/{number}/comments", "--input", "-",
               stdin=json.dumps({"body": body}))
        )
        print(f"{repo}#{number}: fix report {result.get('html_url')}")
        return
    if pr["headRefOid"] != data["head_sha"]:
        sys.exit(
            f"stop: {repo}#{number} head moved to {pr['headRefOid'][:9]} "
            f"(reviewed {data['head_sha'][:9]}); re-check the findings on the new head"
        )
    viewer = gh("api", "user", "--jq", ".login").strip()
    payload = build(data, findings, gh("pr", "diff", number, "--repo", repo), pr["author"]["login"] == viewer)

    summary = (
        f"{repo}#{number}: {payload['event']}, {len(payload['comments'])} inline, "
        f"{len(findings) - len(payload['comments'])} in body"
    )
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print(summary, "(dry run)", file=sys.stderr)
        return
    result = json.loads(
        gh("api", "-X", "POST", f"repos/{repo}/pulls/{number}/reviews", "--input", "-",
           stdin=json.dumps(payload))
    )
    print(summary)
    print(f"{result.get('state')} {result.get('html_url')}")


if __name__ == "__main__":
    main()
