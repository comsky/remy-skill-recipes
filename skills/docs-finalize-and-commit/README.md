# Finalize Documentation and Commit

Finalize documentation changes for production readiness by discovering
existing conventions, verifying code-doc alignment, verifying branch/worktree
intent, structuring clean commits, and forcing a post-publish cleanup decision.
Works with any documentation framework (Docusaurus, VitePress, MkDocs, Nextra,
plain Markdown, etc.).

This skill:

- Samples existing docs to discover conventions (tone, terminology, structure)
- Verifies code-documentation alignment when source code also changed
- Reviews format, terminology, tone, and completeness consistency
- Validates framework-specific syntax and build integrity
- Verifies branch/worktree intent before staging or committing
- Structures commits by change type: `docs(fix)`, `docs(style)`, `docs(content)`, `docs(sync)`
- Requires a branch/worktree cleanup choice after push, PR creation, or merge

---

## Why

Documentation quality degrades when convention discovery is skipped.
Inconsistent terminology, broken links, and misaligned code references
erode user trust. This skill ensures every documentation commit meets
the project's established standards — inferred from the existing corpus,
not imposed from outside — while avoiding stale branch or previous-session
worktree mixups and stale task branches after publish.

---

## Procedure (9 Gates)

- **Gate -1: Branch Context Check** — verify current branch/worktree matches the task
0. **Working Set Validation** — isolate session changes, protect out-of-scope files
1. **Convention Discovery** — sample 10–15 existing docs to infer style, tone, terminology
2. **Code-Documentation Alignment** — map source code changes to documentation references
3. **Documentation Quality Review** — structural, terminology, tone, completeness, syntax, images, links, sidebar
4. **Auto-Fix** — apply judgment-free fixes, present judgment-required items
5. **Build Verification** — run documentation build, capture output
6. **Commit Structuring** — separate commits by change type with Conventional Commits format
7. **Post-Publish Cleanup Handoff** — run cleanup choices after commit/push/PR/merge

---

## Structure

- [SKILL.md](SKILL.md) — Main skill
