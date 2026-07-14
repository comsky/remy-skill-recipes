---
name: gh-ship-pr
description: >
  Ship an already-committed Git branch through GitHub: verify branch/worktree
  intent, push, create or mark a pull request ready for review, optionally wait
  for CI, optionally address review comments automatically, and merge with
  explicit safety gates. Use when a solo developer repeatedly asks to publish
  committed work, register a ready PR, handle PR feedback, and complete merge.
license: MIT
metadata:
  compatibility: Claude Code, Cursor
  type: execution
  category: automation
  maturity: draft
  estimated_time: 10-30 min
  dependencies: branch-context-check
---

# Skill: GH Ship PR (Push, Ready, Review, Merge)

**Type:** Execution

## Purpose

Run the repeated solo-developer shipping workflow after code has already been
committed:

- Verify the current branch/worktree belongs to the intended task
- Push the branch
- Create a GitHub pull request or mark an existing draft PR ready
- Ask whether to wait for CI
- Ask whether to automatically address review comments
- Merge only after explicit safety checks and final confirmation

This skill starts after the commit phase. If there are uncommitted changes that
should be included, run `finalize-and-commit` first.

---

## When to Use

- The user says to push, publish, ship, or finish the current branch through PR
- The user asks for "push -> PR -> review comments -> merge" as one workflow
- A branch already has one or more local commits ready for GitHub
- A draft PR should be made ready for review
- A ready PR should wait for CI, process review comments, and merge
- The user is working alone and wants the standard post-commit routine repeated

---

## When NOT to Use

- The working tree still has changes that need review, staging, or committing
- The task is only to create a commit; use `finalize-and-commit`
- The current branch is `main`, `master`, `develop`, `release/*`, or another
  protected/shared branch and no feature branch exists
- The repository is not hosted on GitHub
- The user only wants read-only PR inspection or a code review
- Required approvals, legal review, release windows, or deployment gates require
  a human decision outside the repository

---

## Inputs Required

Do not run this skill without:

- [ ] A Git repository with a GitHub remote
- [ ] A non-protected current branch
- [ ] The current task intent summarized from the conversation
- [ ] At least one committed change on the branch that should be pushed
- [ ] GitHub authentication through `gh` or an available GitHub connector
- [ ] User choices for:
  - Wait for CI before merge? (`yes` / `no`)
  - Automatically address actionable review comments? (`yes` / `no`)

Optional but recommended:

- [ ] Target base branch
- [ ] PR title/body preference
- [ ] Merge strategy (`squash`, `merge`, `rebase`, or repository default)
- [ ] Whether to delete the branch after merge
- [ ] Whether auto-merge is acceptable when checks are pending

---

## Output Format

1. Branch and PR Snapshot
2. User Options Selected
3. Actions Taken
4. CI Result
5. Review Comment Result
6. Merge Result
7. Cleanup Decision
8. Remaining Manual Follow-ups

---

## Procedure

### Gate -1 - Branch Intent Check

Run `branch-context-check` before pushing or changing PR state. If that skill
is not installed, gather the evidence below directly and classify the verdict
inline using the same four categories (`match`, `ambiguous`, `mismatch`,
`blocked`).

Required evidence:

- `git status --short --branch`
- `git branch --show-current`
- `git log --oneline --decorate -5`
- `git diff --name-only`
- `git diff --cached --name-only`
- Upstream branch, if present

Proceed only when:

- The verdict is `match`, or
- The verdict is `ambiguous` and the user confirms the branch is correct.

Stop when:

- The current branch is protected/shared.
- Dirty or staged files are unrelated to the current task.
- The branch appears tied to a different task.
- The local branch has no committed work to ship.

If the working tree is dirty but all dirty files clearly belong to the current
task, pause and ask whether to run `finalize-and-commit` before continuing.

### Gate 0 - Tool and Remote Check

Confirm GitHub access without modifying state:

- `git remote -v`
- `gh auth status`
- `gh repo view --json nameWithOwner,defaultBranchRef`
- `gh pr view --json number,url,isDraft,state,baseRefName,headRefName,mergeStateStatus,reviewDecision`

If `gh pr view` fails because no PR exists, record that a PR must be created.
Do not treat "no PR yet" as an error.

### Gate 1 - Ask User Options

Ask for these decisions unless the user already gave them:

- Wait for CI before merge?
- Automatically address actionable review comments?

Also ask, when not already known:

- Should the workflow merge after the gates pass?
- Merge strategy: `squash`, `merge`, `rebase`, or repository default?
- Delete branch after merge?

Default recommendations:

- Wait for CI: `yes`
- Automatically address review comments: `yes` for low-risk actionable comments
- Merge after gates pass: require explicit confirmation
- Merge strategy: use repository convention; otherwise prefer `squash`
- Delete branch after merge: use repository convention; otherwise ask

### Gate 2 - Push Branch

Push only the current branch:

- If an upstream exists: `git push`
- If no upstream exists: `git push -u origin HEAD`

After pushing, verify:

- `git status --short --branch`
- `git rev-parse HEAD`
- `git rev-parse @{u}`

Stop if the push fails, the remote rejects the branch, or local HEAD no longer
matches the intended commit.

### Gate 3 - Create or Ready the PR

Ensure the PR is formally registered as ready for review.

If no PR exists:

- Create a ready PR, not a draft PR.
- Prefer `gh pr create --fill` when the commit history has a suitable title and
  body.
- Use the target base branch from the user or the repository default.
- Capture the PR number and URL.

If a PR exists and `isDraft=true`:

- Run `gh pr ready`.
- Re-read PR state and verify `isDraft=false`.

If a PR exists and is already ready:

- Re-read title, URL, base, head, review decision, merge state, and checks.

Stop if the PR targets the wrong base branch or the PR head does not match the
current branch.

### Gate 4 - CI Handling

If the user chose to wait for CI:

- Run `gh pr checks --watch --fail-fast`.
- Then run `gh pr checks --json name,state,bucket,link,workflow`.
- Treat exit code `8` from `gh pr checks` as pending, not failed.

If CI fails:

- Inspect failing check logs.
- If a GitHub CI-fixing workflow is available, use it.
- Otherwise diagnose locally, implement the fix, run relevant local checks,
  commit the fix, push, and repeat Gate 4.
- Stop if the failure requires a product, infrastructure, secret, billing, or
  permission decision.

If the user chose not to wait for CI:

- Still record the current check state.
- Do not claim CI passed.
- Prefer auto-merge over direct merge when required checks are pending or
  unknown.

### Gate 5 - Review Comment Handling

If the user chose automatic review comment handling:

1. Collect unresolved review threads, not only flat comments.
2. Prefer an available GitHub PR review-comment skill or connector that exposes
   unresolved thread state.
3. If only `gh` is available, use GraphQL through `gh api graphql` to inspect
   review threads and resolution state.
4. Classify each unresolved item:
   - **Actionable:** concrete code/doc/test change with clear expected result
   - **Question:** requires an answer but not necessarily a code change
   - **Design decision:** needs user or reviewer judgment
   - **Blocked:** cannot be handled without permissions or external context
5. Implement only actionable comments that are in scope.
6. Run relevant local checks.
7. Commit with a clear message such as `fix: address PR review comments`.
8. Push the branch.
9. Re-read unresolved review threads.
10. Repeat until no actionable unresolved comments remain.

Do not mark threads resolved unless the platform operation is explicitly
available and the fix is present in the pushed branch. Never dismiss reviewer
concerns by assumption.

If the user chose not to automatically handle comments:

- Summarize unresolved comments and stop before merge unless the user confirms
  unresolved comments are acceptable.

### Gate 6 - Merge Readiness Check

Before merging, re-read:

- PR `isDraft`
- PR `state`
- `mergeStateStatus`
- `reviewDecision`
- Required checks
- Unresolved review threads, when accessible
- Local and remote branch HEAD

Merge only when:

- PR is open and ready (`isDraft=false`)
- Current branch HEAD matches pushed PR head
- No known required check is failing
- No actionable unresolved review comment remains, or the user explicitly
  accepts the remaining comments
- Required approvals are satisfied, or repository rules allow merge/auto-merge
- The user gives final merge confirmation

If checks are pending and the user does not want to wait, use `gh pr merge --auto`
when repository rules support auto-merge.

### Gate 7 - Merge

Use the selected strategy:

- Squash: `gh pr merge --squash`
- Merge commit: `gh pr merge --merge`
- Rebase: `gh pr merge --rebase`
- Repository/merge queue default: `gh pr merge`

Add flags only when appropriate:

- `--auto` when checks or merge queue requirements should complete later
- `--delete-branch` only if the user selected branch deletion
- `--match-head-commit <sha>` when available to prevent merging a changed head

Never use `--admin` unless the user explicitly asks to bypass protections.

### Gate 8 - Post-Merge Cleanup

After merge or auto-merge setup:

- Report PR URL and merge/auto-merge status.
- Report whether the branch was deleted.
- Ask or record the post-publish cleanup decision:
  - Stay on current branch/worktree
  - Switch back to base branch
  - Pull latest base branch
  - Remove a temporary worktree
  - Leave cleanup to the user

Do not delete local branches, remove worktrees, or switch branches unless the
user explicitly selected that cleanup action.

These options mirror `branch-context-check` Gate 6; when that skill is
installed, apply its Gate 6 safety checks before any deletion.

---

## Guardrails

- Treat this as a post-commit workflow; do not silently stage or commit dirty
  files before the user confirms scope.
- Never run destructive Git commands such as `reset --hard`, `checkout --`, or
  branch deletion without explicit user approval.
- Never push from a protected/shared branch as the feature branch.
- Never merge a draft PR.
- Never say CI passed unless check data shows a passing state.
- Never treat all review comments as actionable; classify them first.
- Never bypass branch protections with `--admin` unless explicitly requested.
- Prefer repository conventions over generic defaults for base branch, PR body,
  merge strategy, and branch deletion.
- Keep out-of-scope dirty files untouched.

---

## Failure Patterns

Common bad outputs:

- Pushing from `main` because the working tree looked clean
- Creating a draft PR when the user asked for formal ready registration
- Skipping the CI/review-comment user choices
- Calling flat PR comments "resolved" without checking unresolved threads
- Applying reviewer suggestions that require product judgment without asking
- Merging while required checks are pending but auto-merge would have been safer
- Deleting a local branch or worktree as part of cleanup without permission
- Reporting "merged" when only auto-merge was enabled

---

## Example 1 (Minimal Context)

**Input:**

> Current branch is committed. Push it, make the PR ready, wait for CI, and
> merge if everything passes. No need to auto-handle review comments.

**Output:**

1. Branch and PR Snapshot
   - Branch `feature/settings-copy` matches the task.
   - Working tree is clean.
   - No PR exists yet.
2. User Options Selected
   - Wait for CI: yes
   - Auto-address review comments: no
   - Merge after gates pass: confirmed
   - Merge strategy: squash
3. Actions Taken
   - Pushed `feature/settings-copy` with upstream.
   - Created ready PR #42 against `main`.
4. CI Result
   - Required checks passed.
5. Review Comment Result
   - Not processed by user choice.
6. Merge Result
   - PR #42 squash-merged.
7. Cleanup Decision
   - Branch deletion was not selected; branch left intact.
8. Remaining Manual Follow-ups
   - None.

---

## Example 2 (Realistic Scenario)

**Input:**

> Ship this committed branch. Ask me whether to wait for CI and whether to
> handle review comments automatically.

**Output:**

1. Branch and PR Snapshot
   - Branch `fix/billing-retry` is two commits ahead of origin.
   - Working tree is clean.
   - Existing PR #87 is draft and targets `main`.
2. User Options Selected
   - Wait for CI: yes
   - Auto-address review comments: yes
   - Merge after gates pass: final confirmation required
3. Actions Taken
   - Pushed branch.
   - Marked PR #87 ready for review.
4. CI Result
   - First run failed in unit tests.
   - Fixed retry-count assertion, committed, pushed, and reran checks.
   - Required checks passed on the updated head.
5. Review Comment Result
   - Found three unresolved threads.
   - Addressed two actionable code comments.
   - Left one design question unresolved and summarized it for user decision.
6. Merge Result
   - Stopped before merge because one design question remains unresolved.
7. Cleanup Decision
   - No cleanup performed.
8. Remaining Manual Follow-ups
   - Decide whether to change the retry policy requested in the remaining
     review thread.
