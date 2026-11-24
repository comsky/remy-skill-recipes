#!/usr/bin/env python3
"""Post one PR review from a findings JSON file (see SKILL.md Step 5).

Inline comments go on lines inside the PR diff; findings on other lines move
into the review body. Any P0 makes the review REQUEST_CHANGES; findings that are
all P3 (or none) make it APPROVE; anything else is COMMENT. An own PR never
requests changes or approves.

With --defer-approval (the skill's --fix), a review that would approve with P3
findings is a COMMENT instead: the fix push would lift an approval given now.

With --fix-report, post the fix outcomes instead: each finding's `outcome`
(fixed | skipped | no_change_needed) and the fix commit `fix_sha`, which must
already be the PR head (see SKILL.md Step 6). A P3-only PR that is not the
user's gets them as an APPROVE review on that head, unless the base branch does
not count the last pusher's approval and the user pushed the fix; any other PR
gets them as a PR comment.

Fixed text (labels, table headers) comes from TEXT in the findings JSON's
top-level `lang` (ko | en); the findings themselves must already be written in
that language (see SKILL.md Step 4).
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
OUTCOMES = ("fixed", "skipped", "no_change_needed")
TEXT = {
    "ko": {
        "label": {"P0": "차단", "P1": "머지 전 수정", "P2": "수정 권장", "P3": "선택"},
        "outcome": {"fixed": "✅ 수정", "skipped": "⏭️ 건너뜀", "no_change_needed": "➖ 변경 불필요"},
        "count_head": "| 우선순위 | 건수 |",
        "finding_head": "| 우선순위 | 지적 | 위치 |",
        "outcome_count_head": "| 결과 | 건수 |",
        "outcome_head": "| 결과 | 우선순위 | 지적 | 위치 | 사유 |",
        "fix_commit": "수정 커밋",
        "no_findings": "🎉🎉🎉 지적할 항목이 없습니다. 🎉🎉🎉",
        "approve": "🎉🎉🎉 {sha} 기준으로 지적할 항목이 없어 승인합니다. 🎉🎉🎉",
        "p3_approve": "🎉🎉🎉 {sha} 기준으로 P3 제안만 있어 승인합니다. 🎉🎉🎉",
        "stale_note": "> 이 저장소는 새 커밋이 push되면 승인이 자동으로 풀립니다. 이후 커밋은 다시 리뷰해야 합니다.",
        "approve_later": "> P3 제안만 있어, 제안을 반영한 뒤 그 커밋 기준으로 승인합니다.",
        "last_push_note": "> 이 저장소는 마지막으로 push한 사람의 승인을 인정하지 않습니다. 수정 커밋은 다른 리뷰어의 승인이 필요합니다.",
        "own_p0": "> P0 가 있으나 본인 PR 이라 변경 요청 대신 댓글로 남깁니다.",
    },
    "en": {
        "label": {"P0": "Blocking", "P1": "Fix before merge", "P2": "Fix recommended", "P3": "Optional"},
        "outcome": {"fixed": "✅ Fixed", "skipped": "⏭️ Skipped", "no_change_needed": "➖ No change needed"},
        "count_head": "| Priority | Count |",
        "finding_head": "| Priority | Finding | Location |",
        "outcome_count_head": "| Outcome | Count |",
        "outcome_head": "| Outcome | Priority | Finding | Location | Reason |",
        "fix_commit": "Fix commit",
        "no_findings": "🎉🎉🎉 No findings. 🎉🎉🎉",
        "approve": "🎉🎉🎉 Approved at {sha}. No findings. 🎉🎉🎉",
        "p3_approve": "🎉🎉🎉 Approved at {sha}. Only P3 suggestions remain. 🎉🎉🎉",
        "stale_note": "> This repository dismisses approvals when new commits are pushed. Later commits need a new review.",
        "approve_later": "> Only P3 suggestions remain. The approval follows on the commit that applies them.",
        "last_push_note": "> This repository does not count an approval from the last pusher. The fix commit needs another reviewer's approval.",
        "own_p0": "> This PR has a P0. It is your own PR, so this review is a comment, not a change request.",
    },
}


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
    for key in ("repo", "number", "head_sha", "lang", "findings"):
        if key not in data:
            sys.exit(f"findings JSON is missing '{key}'")
    if not isinstance(data["lang"], str) or data["lang"] not in TEXT:
        sys.exit(f"lang is {data['lang']!r}; use one of {tuple(TEXT)}")
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
        if f.get("outcome") not in OUTCOMES:
            sys.exit(f"finding {i} needs outcome in {OUTCOMES}")
        if f["outcome"] != "fixed" and not (isinstance(f.get("reason"), str) and f["reason"].strip()):
            sys.exit(f"finding {i} is {f['outcome']}; give it a reason")
    if any(f["outcome"] == "fixed" for f in findings) and not data.get("fix_sha"):
        sys.exit("a fixed finding needs top-level fix_sha")


def cell(text: str) -> str:
    """Keep free text inside one table cell."""
    return re.sub(r"\s*\n\s*", " ", text.strip()).replace("|", "\\|")


def build_fix_report(data: dict, findings: list[dict]) -> str:
    t = TEXT[data["lang"]]
    blob = f"https://github.com/{data['repo']}/blob/{data['head_sha']}"
    rows = [
        f"| {label} | {n} |"
        for key, label in t["outcome"].items()
        if (n := sum(f["outcome"] == key for f in findings))
    ]
    lines = [t["outcome_count_head"], "| --- | ---: |", *rows, ""]
    if sha := data.get("fix_sha"):
        lines.append(f"{t['fix_commit']}: [`{sha[:9]}`](https://github.com/{data['repo']}/commit/{sha})")
    lines += ["", t["outcome_head"], "| --- | --- | --- | --- | --- |"]
    for f in findings:
        where = f"[`{f['file'].rsplit('/', 1)[-1]}:{f['line']}`]({blob}/{quote(f['file'])}#L{f['line']})"
        reason = cell(f["reason"]) if f["outcome"] != "fixed" else ""
        lines.append(
            f"| {t['outcome'][f['outcome']]} | {MARK[f['priority']]} {f['priority']} | {cell(f['title'])} | {where} | {reason} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def branch_rules(repo: str, base: str) -> dict[str, bool]:
    """What the base branch's rulesets do to approvals; all False when they cannot be read."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/rules/branches/{quote(base, safe='')}", "--jq",
         '[.[] | select(.type == "pull_request") | .parameters] | '
         '{stale: (map(.dismiss_stale_reviews_on_push == true) | any), '
         'last_push: (map(.require_last_push_approval == true) | any)}'],
        capture_output=True, encoding="utf-8",
    )
    try:
        rules = json.loads(result.stdout) if result.returncode == 0 else {}
    except json.JSONDecodeError:
        rules = {}
    return {"stale": rules.get("stale") is True, "last_push": rules.get("last_push") is True}


def approval_line(t: dict, repo: str, sha: str, has_findings: bool) -> str:
    """The approval names the commit it covers, so a later push does not read as approved."""
    link = f"[`{sha[:7]}`](https://github.com/{repo}/commit/{sha})"
    return (t["p3_approve"] if has_findings else t["approve"]).format(sha=link)


def build(
    data: dict, findings: list[dict], diff: str, own_pr: bool,
    stale_dismissed: bool = False, defer_approval: bool = False,
) -> dict:
    t = TEXT[data["lang"]]
    anchorable = diff_right_lines(diff)
    inline, outside = [], []
    for f in findings:
        (inline if f["line"] in anchorable.get(f["file"], ()) else outside).append(f)

    has_p0 = any(f["priority"] == "P0" for f in findings)
    groups = {p: [f for f in findings if f["priority"] == p] for p in PRIORITIES}
    # The body states findings only: no skill, command, level or method names.
    rows = [f"| {MARK[p]} {p} {t['label'][p]} | {len(g)} |" for p, g in groups.items() if g]
    lines = [t["count_head"], "| --- | ---: |", *rows] if rows else [t["no_findings"]]
    blob = f"https://github.com/{data['repo']}/blob/{data['head_sha']}"
    if findings:
        lines += ["", t["finding_head"], "| --- | --- | --- |"]
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
        lines += ["", t["own_p0"]]
    if event == "APPROVE" and findings and defer_approval:
        # The P3s get fixed on the branch next; that push would lift an approval given now, so it waits for the fix report.
        event = "COMMENT"
        lines += ["", t["approve_later"]]
    if event == "APPROVE":
        line = approval_line(t, data["repo"], data["head_sha"], bool(findings))
        lines = [line, "", *lines] if findings else [line]
        if stale_dismissed:
            lines += ["", t["stale_note"]]

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
    parser.add_argument("--fix-report", action="store_true",
                        help="post the fix outcomes: an approval on the fixed head when only P3 findings, else a PR comment")
    parser.add_argument("--defer-approval", action="store_true",
                        help="a P3-only review is posted as a comment; --fix-report approves after the fix")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # a piped stdout on Windows defaults to the locale code page

    with open(args.findings, encoding="utf-8") as fh:
        data = json.load(fh)
    findings = validate(data)
    repo, number = data["repo"], str(data["number"])

    pr = json.loads(
        gh("pr", "view", number, "--repo", repo, "--json", "state,isDraft,headRefOid,baseRefName,author")
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
        # A P3-only PR is approved here, on the head the fix left, so the push cannot lift the approval.
        own_pr = pr["author"]["login"] == gh("api", "user", "--jq", ".login").strip()
        only_p3 = all(f["priority"] == "P3" for f in findings)
        rules = branch_rules(repo, pr["baseRefName"]) if only_p3 and not own_pr else {"stale": False, "last_push": False}
        t = TEXT[data["lang"]]
        approve = only_p3 and not own_pr and not (rules["last_push"] and data.get("fix_sha"))
        if approve:
            body = approval_line(t, repo, expected, True) + "\n\n" + body
            if rules["stale"]:
                body += "\n" + t["stale_note"] + "\n"
        elif only_p3 and not own_pr:  # the push was mine, and this repository does not count the last pusher's approval
            body += "\n" + t["last_push_note"] + "\n"
        kind = "approval" if approve else "comment"
        if args.dry_run:
            print(body)
            print(f"{repo}#{number}: fix report as {kind} (dry run)", file=sys.stderr)
            return
        if approve:
            result = json.loads(
                gh("api", "-X", "POST", f"repos/{repo}/pulls/{number}/reviews", "--input", "-",
                   stdin=json.dumps({"commit_id": expected, "event": "APPROVE", "body": body}))
            )
        else:
            result = json.loads(
                gh("api", "-X", "POST", f"repos/{repo}/issues/{number}/comments", "--input", "-",
                   stdin=json.dumps({"body": body}))
            )
        print(f"{repo}#{number}: fix report as {kind} {result.get('state', '')} {result.get('html_url')}")
        return
    if pr["headRefOid"] != data["head_sha"]:
        sys.exit(
            f"stop: {repo}#{number} head moved to {pr['headRefOid'][:9]} "
            f"(reviewed {data['head_sha'][:9]}); re-check the findings on the new head"
        )
    viewer = gh("api", "user", "--jq", ".login").strip()
    payload = build(
        data, findings, gh("pr", "diff", number, "--repo", repo), pr["author"]["login"] == viewer,
        branch_rules(repo, pr["baseRefName"])["stale"], args.defer_approval,
    )

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
