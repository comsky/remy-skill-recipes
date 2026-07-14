---
name: frontend-decision-sync
description: >
  Sync reusable frontend decisions into persistent project documentation after
  UI work. Use when frontend changes introduce or modify component APIs,
  variants, design-system tokens, styling conventions, layout behavior,
  accessibility rules, interaction patterns, responsive behavior, or agent
  operating instructions; when the user asks to reflect decisions in
  components.md, design system docs, AGENTS.md, CLAUDE.md, GEMINI.md, or
  similar project memory files; or before finalizing frontend work where
  future consistency depends on decisions made during implementation.
license: MIT
metadata:
  compatibility: Claude Code, Cursor
  type: execution
  category: documentation
  maturity: draft
  estimated_time: 10 min
---

# Skill: Frontend Decision Sync (Persistent UI Decision Documentation)

**Type:** Execution

## Purpose

Persist reusable frontend decisions so future UI work applies them
consistently.

This skill identifies frontend decisions made during implementation and records
them in the right project documentation:

- Component contracts and usage rules
- Design-system tokens and visual conventions
- Layout, responsive, interaction, and accessibility decisions
- Agent-facing operating rules for future frontend work

---

## When to Use

- After completing frontend work that changed component APIs, variants, props,
  slots, composition rules, or usage constraints
- After choosing reusable styling, spacing, typography, color, layout,
  responsive, animation, or accessibility conventions
- When a decision should be applied consistently in later frontend tasks
- When the user asks to update `components.md`, design system docs,
  `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or similar project memory files
- Before finalizing frontend changes when implementation decisions are likely
  to become conventions

---

## When NOT to Use

- Pure backend, infrastructure, data, or CLI changes with no frontend decision
- One-off visual tweaks that should not become a reusable convention
- Documentation-only edits where no new decision needs to be extracted
- Prototypes or throwaway experiments unless the user explicitly asks to
  preserve the decisions
- External design research without implemented or approved project decisions

---

## Inputs Required

Do not run this skill without:

- [ ] The frontend diff or list of changed frontend files
- [ ] A summary of the task goal and decisions made during implementation
- [ ] Access to existing project documentation and agent instruction files
- [ ] Knowledge of which files were changed in the current session

Optional but recommended:

- [ ] Existing design-system, component, styling, or architecture docs
- [ ] Screenshots, design specs, or issue/PR context
- [ ] The user's preferred long-term documentation target
- [ ] Project conventions for headings, terminology, and examples

Without asking the user, gather available inputs directly from the repository.
Ask only when the correct documentation target cannot be inferred safely.

---

## Output Format

1. Decisions Identified
2. Documentation Target Map
3. Actions Taken
4. Items Not Recorded
5. Verification Results

---

## Procedure

### Gate 0 - Scope and Evidence

Inspect the current frontend work before editing documentation:

- Review the diff and changed files.
- Identify frontend entry points, shared components, style files, tokens,
  stories, tests, and docs touched by the task.
- Read nearby documentation before deciding where to write.
- Separate current-session changes from unrelated dirty files.

Do not update broad project memory based only on intuition. Tie every recorded
decision to a concrete implementation change, explicit user instruction, or
existing documentation gap.

### Gate 1 - Decision Extraction

Extract only decisions that should affect future work.

Classify each candidate:

| Class | Examples | Record? |
|---|---|---|
| Component contract | Prop names, variants, slots, composition rules, disabled/loading behavior | Yes |
| Design-system rule | Token usage, spacing scale, typography, color semantics, elevation, radius | Yes |
| Layout/responsive rule | Breakpoints, density behavior, overflow strategy, touch target rules | Yes |
| Interaction/accessibility rule | Keyboard behavior, focus management, ARIA pattern, motion constraints | Yes |
| Agent operating rule | Which docs to read, required verification, screenshot checks, lint/test gates | Yes |
| Local implementation detail | File-local helper names, transient CSS workaround, one-off copy change | Usually no |

For each accepted decision, write:

- Decision
- Rationale
- Scope of applicability
- Source evidence (`file:line` or diff reference when possible)
- Owner document to update

### Gate 2 - Documentation Target Selection

Choose the narrowest durable location:

| Target | Use for |
|---|---|
| `components.md` / component docs | Public component API, variants, usage examples, composition rules |
| Design-system docs | Tokens, visual language, spacing, typography, color, layout, motion, elevation |
| `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` | Agent instructions, required reads, verification workflow, repo-specific frontend rules |
| Storybook docs / examples | Visual examples or usage states that need executable documentation |
| ADR / architecture docs | High-impact trade-offs, cross-layer decisions, migration strategy |
| Existing feature docs | Feature-specific UI behavior that should not become a global rule |

If multiple targets fit, prefer the most specific source of truth and add a
short cross-reference only when future readers would otherwise miss it.

### Gate 3 - Minimal Documentation Update

Update documentation with minimal, durable changes:

- Match existing document structure, tone, terminology, and heading style.
- Add concise rules with enough context to apply them later.
- Include examples only when they prevent ambiguity.
- Avoid duplicating the same rule in multiple files.
- Mark scope explicitly when a rule is feature-specific or experimental.
- Preserve unrelated document content.

When no suitable documentation file exists, create the smallest conventional
file only if the project already has a clear docs location. Otherwise, ask the
user before creating a new top-level memory file.

### Gate 4 - Consistency Check

Verify that the written decision aligns with the implementation:

- The documented component names, props, tokens, routes, and file paths exist.
- The stated convention is not contradicted by nearby code or docs.
- No outdated guidance remains in the same document.
- Agent-facing instructions are actionable, not vague preferences.
- One-off implementation details were not promoted to global rules.

### Gate 5 - Handoff Summary

Report:

- Decisions recorded
- Files updated
- Decisions intentionally not recorded and why
- Any remaining documentation target uncertainty
- Verification performed

---

## Guardrails

- Do not invent design-system rules that were not implemented, approved, or
  already implied by existing documentation.
- Do not turn one-off styling into a global convention without evidence.
- Do not overwrite user-authored docs or unrelated changes.
- Do not duplicate the same rule across several files unless one entry is a
  short pointer to the source of truth.
- Do not make `AGENTS.md` a dumping ground for component details; reserve it for
  operating instructions future agents must follow.
- Do not create new top-level documentation files when an existing source of
  truth is available.
- Explicitly state assumptions when a target document is ambiguous.

---

## Failure Patterns

Common bad outputs:

- Updating only `AGENTS.md` even though the decision belongs in component or
  design-system docs
- Recording vague rules such as "keep UI consistent" without concrete scope
- Duplicating the same decision in `components.md`, design docs, and agent docs
  with no source of truth
- Promoting a one-screen workaround into a global design-system rule
- Forgetting to read existing docs before editing them
- Documenting decisions that do not match the actual code
- Omitting the final summary of what was recorded and what was skipped

---

## Example 1 (Minimal Context)

**Input:**

A change adds a `loading` prop to `Button` and standardizes that loading buttons
keep their width while showing a spinner. Existing docs include
`docs/components.md`.

**Output:**

1. Decisions Identified:
   - `Button` loading state preserves width and replaces the leading icon with
     a spinner.
2. Documentation Target Map:
   - `docs/components.md` -> Button API and behavior.
3. Actions Taken:
   - Add `loading` to the Button prop table.
   - Add one usage note under Button states.
4. Items Not Recorded:
   - Spinner implementation details were left out because they are internal.
5. Verification Results:
   - Confirmed `Button` exports `loading` and no other component docs define a
     conflicting loading pattern.

---

## Example 2 (Realistic Scenario)

**Input:**

A dashboard redesign introduces compact density rules, replaces ad hoc spacing
with `space.3` / `space.4`, adds a reusable `MetricTile` variant, and requires
agents to check desktop and mobile screenshots before finalizing dashboard UI.
The repo has `docs/design-system.md`, `docs/components.md`, and `AGENTS.md`.

**Output:**

1. Decisions Identified:
   - Dashboard density uses `space.3` for internal tile gaps and `space.4` for
     section gaps.
   - `MetricTile` supports `default`, `warning`, and `critical` variants.
   - Future dashboard UI changes require desktop and mobile screenshot checks.
2. Documentation Target Map:
   - `docs/design-system.md` -> dashboard spacing rule.
   - `docs/components.md` -> `MetricTile` variants.
   - `AGENTS.md` -> screenshot verification workflow.
3. Actions Taken:
   - Added dashboard spacing rule to the layout section.
   - Added `MetricTile` variant table and usage constraint.
   - Added a frontend verification bullet to `AGENTS.md`.
4. Items Not Recorded:
   - Feature-specific copy changes were not recorded because they are not
     reusable UI decisions.
5. Verification Results:
   - Checked changed component exports, token names, and existing docs for
     conflicts.

---

## Notes

This skill complements finalization workflows. Run it before commit preparation
when frontend decisions should survive beyond the current implementation.
