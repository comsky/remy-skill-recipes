# Branch Context Check

Verify that the current Git branch, upstream state, and dirty working tree
match the intended task before staging, committing, pushing, or continuing work
from another session. Also force a cleanup decision after push, PR creation, or
PR merge.

This skill:

- Detects stale branch reuse before new commits are added
- Compares current task intent against branch name, recent commits, and dirty files
- Separates current-session changes from carried-forward or unknown changes
- Recommends when to create a new branch or worktree
- Blocks commit flow until ambiguous or risky ownership is confirmed
- Requires a keep/delete/switch/remove cleanup choice after publish workflows

---

## Why

Agents often continue from whatever branch is currently checked out. That is
safe only when the branch and dirty files still match the current task. This
skill adds a lightweight Git context gate at the commit boundary so unrelated
session work is not accidentally mixed into a new task. It also prevents stale
task branches and worktrees from accumulating after the work has been pushed or
merged.

---

## Procedure (7 Gates)

0. **Task Intent Capture** — summarize the current task before checking Git
1. **Git Context Snapshot** — inspect branch, upstream, dirty files, and recent commits
2. **Branch Intent Inference** — compare branch purpose with the current task
3. **Dirty Worktree Ownership** — classify current-session, carried-forward, staged, and unknown files
4. **Decision Matrix** — return `match`, `ambiguous`, `mismatch`, or `blocked`
5. **Handoff** — require confirmation before staging or committing risky states
6. **Post-Publish Cleanup Decision** — choose whether to keep, switch, delete, remove, or prune after push/PR/merge

---

## Structure

- [SKILL.md](SKILL.md) — Main skill
