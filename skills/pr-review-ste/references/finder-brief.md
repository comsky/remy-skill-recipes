# Finder Sub-Agent Brief (One per PR)

Fill in `<…>` and pass the text to a read-only sub-agent as is. Copy `<angles>`, `<per_angle>`, `<max_findings>`, and `<keep_rule>` from the matching row of the level table in SKILL.md Step 2.

```text
You are doing a read-only, high-recall code review of one pull request. Do NOT edit files, commit, push, switch branches, or post anything to GitHub.

Target: <owner/repo> PR #<N> "<title>" (+<add>/-<del>, <files> files).
- Unified diff: <scratchpad>/<repo>-<N>.diff (read large diffs in chunks; skip docs prose except where it states a contract the code must follow).
- PR head is fetched as git ref `refs/remotes/pr/<N>` in <checkout path>. Read files with `git -C <checkout> show "refs/remotes/pr/<N>:<path>"` (in zsh write "${R}:path", never $R:path). Find callers with `git -C <checkout> grep -n <pat> refs/remotes/pr/<N> -- <src dir>`.
- Related repo(s) for contract checks, read-only: <path and ref, e.g. the API server's origin/main or refs/remotes/pr/<M>>. <One sentence on which contract to compare.>
- Project rules: <AGENTS.md / CLAUDE.md / testing guideline paths>.

Review level: <level>. Angles to run: <angles>. Up to <per_angle> candidates per angle. Keep rule: <keep_rule>.
<ADR PR only: "This PR changes an ADR. Verify prose, not code: " + the ADR angle readings from SKILL.md Step 2.>

Angle definitions (do it yourself, no sub-agents): (A) line-by-line scan of every hunk plus the enclosing function, (B) removed-behavior audit (the invariant each deleted line enforced, and where it is re-established), (C) cross-file tracer (callers/callees of changed functions, contract with the related repo, null vs missing fields), Reuse, Simplification, Efficiency, Altitude (symptom patch vs. root cause; sibling call sites left broken), Conventions (only exact rule violations; quote the rule). Correctness first. Verify each candidate against the actual code; drop anything without a concrete failure scenario. Do not report behavior that predates this PR unless the PR widens or re-exposes it. Dedup.

Priority: P0 = blocking (data loss/corruption, security or permission bypass, crash on a main path, contract that will fail in production, saved resources that stop loading); P1 = should fix before merge (main feature wrong under a realistic condition, regression of something that worked before); P2 = fix recommended; P3 = optional/cleanup. Do not inflate.

Return ONLY a JSON array (max <max_findings>, most severe first), each item:
{"priority":"P0|P1|P2|P3","category":"correctness|reuse|simplification|efficiency|altitude|conventions|test-coverage","file":"repo-relative path","line":<line in the PR HEAD file>,"in_diff":true|false,"summary":"one sentence","failure_scenario":"concrete inputs/state -> wrong result","suggestion":"one or two sentences"}
After the JSON, add at most 3 lines on candidates you rejected and why.
```
