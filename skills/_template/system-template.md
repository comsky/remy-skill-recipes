---
name: my-system-skill-name
description: >
  A clear description of the continuous behavior this skill provides
  and when it should activate.
license: MIT
metadata:
  compatibility: Claude Code, Cursor
  type: system
  category: automation
  maturity: draft
  activation: automatic / command-driven / hybrid
  state: stateless / conversation-wide / external DB-backed
  dependencies: (e.g., Notion MCP)
---

# System Skill Title

**Type:** System

## Purpose

What continuous behavior this skill provides.

---

## Scope

When this skill should be active and what it should ignore.

**Triggers:**

-
-

**Non-triggers:**

-
-

---

## Inputs / Signals

What inputs it reads:

- Conversation content
- Manual commands
- External sources (DB, APIs)

---

## Core Behavior

### 1) Detection / Intake

- Normalization rules
- De-duplication rules

### 2) Decision Logic

- Thresholds
- Gating conditions
- Override commands

### 3) Actions

- Create/update records
- Notify/propose/ask
- Link/relate entities

---

## Output / Side Effects

Define exact outputs:

- Messages shown to the user
- External writes (DB fields, relations, counts)

---

## Guardrails

- Avoid duplicate creation (re-query before write).
- Do not treat vague words as concepts.
- Never write secrets/PII.
- Prefer conservative proposals over spam.

---

## Failure Patterns

- Duplicate entries due to alias mismatch
- Over-triggering on generic terms
- Missing updates because of strict matching

---

## Example 1 (Automatic Trigger)

**Input (conversation snippet):**

**Expected behavior:**

---

## Example 2 (Manual Command)

**Input command:**

**Expected behavior:**

---

## Notes

Migration, schema requirements, operational considerations.
