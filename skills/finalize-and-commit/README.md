# Finalize Changes and Commit

Finalize code changes for production readiness by removing duplicate logic,
auditing hardcoded values, verifying branch/worktree intent, verifying build
integrity, and structuring clean commits with Conventional Commits format.

This skill:

- Isolates current session changes and protects out-of-scope files
- Verifies branch/worktree intent before staging or committing
- Detects and eliminates duplicate logic and dead code
- Audits hardcoded values (constants, policies, test-only)
- Verifies consistency, security, and build integrity
- Structures commits logically: refactor → functional change → tests/docs

---

## Why

Messy working changes produce messy commit history.
Hardcoded values, duplicated logic, and dead code slip into production
when there is no systematic final pass. This skill ensures every commit
is clean, intentional, and safe — without accidentally committing on a stale
branch or staging changes from other sessions.

---

## Procedure (7 Gates)

- **Gate -1: Branch Context Check** — verify current branch/worktree matches the task
0. **Working Set Validation** — isolate session changes, protect out-of-scope files
1. **Duplicate & Dead Code Detection** — extract helpers for 3+ repetitions, remove unused code
2. **Hardcoded Value Audit** — classify as algorithmic constant / operational policy / test-only
3. **Consistency & Quality Review** — error handling, logging, secrets, interface compatibility
4. **Verification Proof** — run tests, lint, typecheck, build
5. **Commit Structuring** — separate by type, Conventional Commits format

---

## Structure

- [SKILL.md](SKILL.md) — Main skill
