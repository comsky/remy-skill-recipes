# GH Ship PR

Ship an already-committed Git branch through GitHub: push the branch, create a
ready pull request or mark an existing draft ready, optionally wait for CI,
optionally address review comments, and merge only after explicit safety gates.

This skill:

- Verifies branch and worktree intent before any push or PR action
- Pushes only the current non-protected branch
- Creates a ready PR or marks an existing draft PR ready for review
- Asks whether to wait for CI before merge
- Asks whether to automatically address actionable review comments
- Re-checks PR state, checks, review status, and head commit before merge
- Requires explicit merge and cleanup decisions

---

## Why

Solo PR shipping often repeats the same risky sequence: push, open or ready the
PR, wait for checks, process reviewer feedback, push fixes, and merge. This
skill makes that sequence explicit so the agent does not skip CI, merge a draft
PR, ignore unresolved review threads, push from the wrong branch, or delete
branches/worktrees without permission.

---

## Procedure (10 Gates)

- **Gate -1: Branch Intent Check** — verify the branch/worktree matches the task
0. **Tool and Remote Check** — confirm GitHub remote, auth, repo, and PR state
1. **Ask User Options** — choose CI waiting, review handling, merge, and cleanup behavior
2. **Push Branch** — push the current branch and verify remote head
3. **Create or Ready the PR** — create a ready PR or convert draft to ready
4. **CI Handling** — wait, inspect, fix, or record pending/failing checks
5. **Review Comment Handling** — classify and address actionable unresolved threads
6. **Merge Readiness Check** — re-read PR state, checks, review decision, and head
7. **Merge** — use the selected merge strategy with safety flags
8. **Post-Merge Cleanup** — record or perform the selected cleanup action

---

## Structure

- [SKILL.md](SKILL.md) — Main skill
