---
name: branch-context-check
description: >
  Verify that the current Git branch, upstream state, and dirty working tree
  match the user's intended task before staging, committing, pushing, or
  continuing work from another session. Use this to detect stale branch reuse,
  leftover dirty files from previous sessions, unrelated commits on the current
  branch, and cases where work should be split into a new branch or worktree.
license: MIT
compatibility:
  - Claude Code
  - Cursor
metadata:
  type: execution
  category: cleanup
  maturity: draft
  estimated_time: 5 min
---

# Skill: Branch Context Check (Branch / Worktree Intent Guard)

**Type:** Execution

## Purpose

Prevent accidental commits on the wrong branch or into a dirty working tree
owned by another session.

This skill verifies:

- Current branch intent matches the current task
- Recent commits on the branch are related to the current work
- Dirty files are attributable to the current session or intentionally carried
  forward
- The safest next step is clear before staging, committing, pushing, or
  continuing work

---

## When to Use

- Before committing or pushing changes
- Before running a finalize-and-commit workflow
- When continuing work after time has passed or after switching sessions
- When the current branch name looks tied to another task, issue, PR, or agent
  session
- When the working tree is dirty and file ownership is unclear
- When deciding whether to create a new branch or separate worktree

---

## When NOT to Use

- Non-Git directories
- Read-only repository inspection with no intent to edit, stage, commit, or push
- Trivial commands that do not depend on branch state
- Repositories where the user explicitly confirms the current branch is correct
  for this exact task

---

## Inputs Required

Do not run this skill without:

- [ ] A Git repository
- [ ] Current task intent, summarized from the user's request or conversation
- [ ] Access to Git status, branch, diff, and recent commit history

Optional but recommended:

- [ ] Target base branch (e.g., `main`, `develop`, release branch)
- [ ] Intended branch name, ticket ID, PR title, or issue reference
- [ ] List of files modified by the current session
- [ ] Known previous-session work that should remain untouched

---

## Output Format

1. Branch Context Snapshot
2. Intent Match Verdict (`match`, `ambiguous`, `mismatch`, or `blocked`)
3. Dirty Worktree Ownership
4. Recommended Action
5. User Confirmation Required

---

## Procedure

### Gate 0 – Task Intent Capture

Summarize the current task in one sentence before inspecting Git.

Extract these intent signals when available:

- Feature, bug, documentation, or refactor scope
- Ticket/issue/PR ID
- Expected files, packages, or modules
- User-stated branch or worktree preference
- Whether the work is new, a continuation, or finalization of existing work

If intent cannot be summarized, ask the user for a short task description
before recommending any Git action.

---

### Gate 1 – Git Context Snapshot

Collect evidence with non-destructive commands:

- `git status --short --branch`
- `git branch --show-current`
- `git diff --name-only`
- `git diff --cached --name-only`
- `git log --oneline --decorate -5`

When useful and available, also check:

- `git rev-parse --abbrev-ref --symbolic-full-name @{u}` for upstream branch
- `git status --porcelain=v1` for machine-readable dirty files
- `git merge-base --fork-point <base> HEAD` or `git merge-base <base> HEAD`
  when evaluating whether branch commits are tied to the expected base

Do not run commands that alter the index, working tree, branch, or stash.

---

### Gate 2 – Branch Intent Inference

Infer the current branch's likely purpose from:

- Branch name tokens (`feature/foo`, ticket IDs, user names, session IDs)
- Recent commit messages and touched areas
- Upstream branch name and ahead/behind status
- Whether the branch is a protected/shared branch such as `main`, `master`,
  `develop`, `release/*`, or `hotfix/*`
- Whether the branch is clean or already contains task-specific commits

Compare that inferred purpose against the current task intent from Gate 0.

Classify the result:

- **match:** Branch name, recent commits, and file scope clearly align with the
  current task.
- **ambiguous:** Evidence is weak or generic; current branch may be correct but
  needs user confirmation.
- **mismatch:** Branch appears tied to a different task, issue, PR, or previous
  session.
- **blocked:** Dirty state or branch history makes safe continuation impossible
  without a user decision.

---

### Gate 3 – Dirty Worktree Ownership

Separate files into:

- **Current-session changes:** Files edited in the current conversation or
  explicitly requested by the user.
- **Carried-forward changes:** Dirty files that existed before the current task
  or are not attributable to this session.
- **Staged changes:** Files already staged before this skill runs.
- **Unknown ownership:** Files whose origin cannot be determined.

Then check overlap:

- Same file touched by current-session and carried-forward changes
- Same module or feature area touched by unrelated tasks
- Staged changes that do not belong to the current task

If overlap exists, classify the verdict as `blocked` unless the user explicitly
confirms the combined scope.

---

### Gate 4 – Decision Matrix

Use this matrix to recommend the next action:

| Condition | Verdict | Recommended Action |
|---|---|---|
| Branch matches current task and dirty files are in-scope | match | Continue finalize, stage only confirmed files |
| Branch is generic or evidence is weak, but no conflicting dirty files exist | ambiguous | Ask user to confirm branch before commit |
| Clean branch clearly belongs to another task | mismatch | Create/switch to a task-appropriate branch or worktree before editing/committing |
| Dirty branch contains previous-session work unrelated to current task | blocked | Do not commit; ask whether to finish previous work, split via worktree, or isolate current-session patch |
| Current branch is protected/shared and task is non-trivial | blocked | Create a feature/fix branch before committing |
| Staged files include unknown or unrelated changes | blocked | Unstage only with explicit user approval; otherwise stop before commit |
| Branch is ahead of upstream with unrelated commits | mismatch | Do not add new task commits; create a separate branch from the correct base or ask user to confirm stacking |

When recommending a new branch, propose a concrete name derived from the task,
for example `codex/fix-login-timeout` or `codex/docs-branch-guard`.

When recommending a worktree, include the base branch assumption and state that
only user-confirmed changes should be moved or recreated there.

---

### Gate 5 – Handoff

Before any staging or commit:

- Present the verdict and evidence.
- State exactly which files are safe to commit now.
- State which files must be left untouched.
- Ask for user confirmation when verdict is `ambiguous`, `mismatch`, or
  `blocked`.

If used inside `finalize-and-commit` or `docs-finalize-and-commit`, this gate
must complete before their Working Set Validation gate proceeds.

---

## Guardrails

- Do not treat the current branch as valid just because it is already checked
  out.
- Do not assume a new session can be reliably detected; infer risk from branch,
  commits, dirty files, and task intent.
- Do not run destructive Git commands (`reset`, `checkout --`, `restore`,
  `clean`, `stash`, rebase, branch deletion) without explicit user approval.
- Do not use `git add .`, `git add -A`, or `git add --all`.
- Do not commit staged changes until staged ownership is confirmed.
- Do not move dirty changes across branches or worktrees automatically.
- Do not mix unrelated tasks in one commit just because they are already dirty.
- Explicitly state assumptions about base branch and branch naming.

---

## Failure Patterns

Common bad outputs:

- Saying "working tree clean" but ignoring that the branch itself belongs to a
  previous task
- Continuing on a feature branch whose recent commits are unrelated to the
  current request
- Treating dirty files as current-session changes without evidence
- Recommending `git stash` as a default solution, hiding ownership instead of
  clarifying it
- Creating a new branch from the wrong feature branch when the correct base
  should be `main` or `develop`
- Staging all files after warning that some files are out of scope
- Asking for generic confirmation without listing the exact branch, commits, and
  files that caused the risk

---

## Example 1 (Clean Wrong Branch)

**Input:**

Current task: add billing export tests. `git status --short --branch` shows a
clean working tree on `feature/oauth-login`. Recent commits mention OAuth
callback handling.

**Output:**

1. Branch Context Snapshot: branch `feature/oauth-login`, clean tree, recent
   commits are OAuth-related.
2. Intent Match Verdict: `mismatch` — current task is billing export tests, but
   branch intent is OAuth login.
3. Dirty Worktree Ownership: no dirty files.
4. Recommended Action: create a new branch from the correct base, for example
   `codex/test-billing-export`, before making or committing billing changes.
5. User Confirmation Required: yes — confirm base branch (`main` assumed) and
   new branch/worktree preference.

---

## Example 2 (Dirty Previous Session)

**Input:**

Current task: update dashboard copy. Current branch is `codex/aaa-refactor`.
Working tree has modified `src/auth/session.ts` and `src/dashboard/Home.tsx`.
Conversation history only touched `src/dashboard/Home.tsx`. Recent commits on
the branch mention auth session refactoring.

**Output:**

1. Branch Context Snapshot: branch `codex/aaa-refactor`, dirty files in auth and
   dashboard, recent commits are auth-related.
2. Intent Match Verdict: `blocked` — branch and one dirty file appear to belong
   to a previous auth refactor session.
3. Dirty Worktree Ownership: `src/dashboard/Home.tsx` is current-session;
   `src/auth/session.ts` is carried-forward/unknown.
4. Recommended Action: do not commit from this state. Ask whether to finish the
   auth refactor first, create a separate worktree for dashboard copy, or commit
   only the confirmed dashboard file after explicit approval.
5. User Confirmation Required: yes — exact commit scope must be confirmed before
   staging.

---

## Notes

This skill is intentionally conservative. Its goal is not to automate branch
management; it is to prevent accidental task mixing at the commit boundary.

