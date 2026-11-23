# PR Review STE

Review one or more GitHub pull requests at a chosen level, verify each finding
on the PR head, and post one review per PR. Comments follow STE-style Korean
with P0–P3 priority marks. With `--fix`, fix the findings on the PR branch and
post the outcome of each one.

This skill:

- Skips merged, closed, and draft PRs
- Sets scope and count per level (`low` · `medium` · `high` · `xhigh` · `max`); ADR PRs default to `xhigh`
- Takes candidates from `/code-review` when the host provides it; otherwise runs its own angle table
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
2. **Review at the Chosen Level** — take candidates from `/code-review` (or the level table's angles); verify each on the PR head
3. **Assign Priority** — P0–P3 without inflation or deflation
4. **Write in STE-Style Korean** — one fact per sentence, 합니다체, no method talk
5. **Post** — findings JSON → `post_review.py --dry-run` → post
6. **Fix (`--fix` only)** — isolated worktree, checks, one commit, push, outcome comment
7. **Final Report** — one table per run

---

## Posted Format

Priority marks: 🚨 P0 차단 · ⚠️ P1 머지 전 수정 · 💡 P2 수정 권장 · 💬 P3 선택.

The review body is a count table, then one row per finding. A finding on a
diff line gets an inline comment (`⚠️ **P1** …`); a finding outside the diff
carries its detail below the table.

```markdown
| 우선순위 | 건수 |
| --- | ---: |
| ⚠️ P1 머지 전 수정 | 1 |
| 💬 P3 선택 | 1 |

| 우선순위 | 지적 | 위치 |
| --- | --- | --- |
| ⚠️ P1 | 필터를 모두 지우면 조회 조건이 `null` 로 저장됩니다 | [`filters.ts:58`](…#L58) |
| 💬 P3 | `formatRange` 가 `toRangeLabel` 과 같은 일을 합니다 | [`Header.tsx:21`](…#L21) |
```

The `--fix` outcome comment has the same shape: a count table per outcome, the
fix commit link, then one row per finding.

```markdown
| 결과 | 건수 |
| --- | ---: |
| ✅ 수정 | 1 |
| ⏭️ 건너뜀 | 1 |

수정 커밋: [`0123456ab`](…)

| 결과 | 우선순위 | 지적 | 위치 | 사유 |
| --- | --- | --- | --- | --- |
| ✅ 수정 | ⚠️ P1 | 필터를 모두 지우면 조회 조건이 `null` 로 저장됩니다 | [`filters.ts:58`](…#L58) |  |
| ⏭️ 건너뜀 | 💬 P3 | `formatRange` 가 `toRangeLabel` 과 같은 일을 합니다 | [`Header.tsx:21`](…#L21) | 다른 PR 범위입니다 |
```

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
