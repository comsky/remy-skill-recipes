# Frontend Decision Sync

Sync reusable frontend decisions into persistent project documentation after UI
work.

This skill:

- Extracts durable frontend decisions from implementation changes
- Maps each decision to the right source of truth
- Updates component docs, design-system docs, or agent instruction files
- Avoids promoting one-off implementation details into global rules
- Summarizes what was recorded, skipped, and verified

---

## Why

Frontend consistency often fails because implementation decisions stay trapped
in a single PR or chat thread. This skill turns reusable UI decisions into
project memory so later work can apply them without rediscovering the same
rules.

---

## Procedure (6 Gates)

0. **Scope and Evidence** — inspect the diff and existing docs
1. **Decision Extraction** — separate reusable decisions from local details
2. **Documentation Target Selection** — choose the narrowest durable source of truth
3. **Minimal Documentation Update** — record concise, scoped rules
4. **Consistency Check** — verify docs match implementation
5. **Handoff Summary** — report recorded, skipped, and uncertain items

---

## Structure

- [SKILL.md](SKILL.md) — Main skill
