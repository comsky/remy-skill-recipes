# PR Review STE

Review one or more GitHub pull requests at a chosen level, verify each finding
on the PR head, and post one review per PR. Comments follow STE-style Korean
with P0–P3 priority marks. With `--fix`, fix the findings on the PR branch and
post the outcome of each one.

This skill:

- Skips merged, closed, and draft PRs
- Sets scope and count per level (`low` · `medium` · `high` · `xhigh` · `max`); ADR PRs default to `xhigh`
- Keeps only findings with a concrete failure scenario
- Cross-checks PRs that form two sides of one contract
- Derives the review event from the priorities: P0 → `REQUEST_CHANGES`, only P3 → `APPROVE`, otherwise `COMMENT`
- Leaves review method, tool names, and level out of posted text
- With `--fix`: fixes in an isolated worktree, pushes one commit without force, and posts each outcome

---

## Why

Review comments lose value when they are vague, inflated, or padded with
process talk. Fixed scope per level, a failure-scenario requirement, and a
script that picks the review event keep every posted comment specific and the
verdict consistent across PRs.

---

## Procedure (7 Steps)

1. **Confirm Targets** — read state, head SHA, and ADR status; fetch the diff and head ref
2. **Review at the Chosen Level** — run the angles in the level table; verify each candidate
3. **Assign Priority** — P0–P3 without inflation or deflation
4. **Write in STE-Style Korean** — one fact per sentence, 합니다체, no method talk
5. **Post** — findings JSON → `post_review.py --dry-run` → post
6. **Fix (`--fix` only)** — isolated worktree, checks, one commit, push, outcome comment
7. **Final Report** — one table per run

---

## Usage

```text
/pr-review-ste 3338 3339
/pr-review-ste xhigh 3338
/pr-review-ste --fix 3338
```

Requires an authenticated `gh` and Python 3.9+.

---

## Structure

- [SKILL.md](SKILL.md) — Main skill
- [scripts/post_review.py](scripts/post_review.py) — Builds and posts the review or the fix-outcome comment
- [references/finder-brief.md](references/finder-brief.md) — Sub-agent brief for large or multi-PR runs
