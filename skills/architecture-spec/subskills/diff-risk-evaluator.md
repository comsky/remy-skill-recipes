# Subskill: Diff Risk Evaluator

**Parent:** [SKILL.md](../SKILL.md)  
**Role:** Risk scoring (Step 1 of parent skill)

---

## Purpose

Analyze changed files / diff summary and calculate a deterministic risk
score.

This subskill does NOT generate documentation. It only returns:

- risk signals (matched patterns)
- total score (numeric)
- recommended documentation level (A/B/C)

---

## Inputs

- changed_files (required)
- diff_summary — LOC or file count (required)
- diff_snippets (optional)

---

## Output Format

Return a structured risk summary:

```
Path Score:      +N  (matched: <patterns>)
Layer Score:     +N  (<count> layers)
Magnitude Score: +N  (<LOC> LOC)
Total Score:     N
Level:           A / B / C
Hard Override:   <applied rule or "none">
```

---

## Step 1 — Path-Based Risk Detection

| Pattern | Score |
|---|---|
| /auth/, security, rbac | +4 |
| migration, schema | +3 |
| /infra/, terraform | +4 |
| k8s, Dockerfile | +3 |
| /integrations/, oauth, oidc | +3 |
| middleware, global | +3 |
| config, .env | +3 |
| payment, billing | +4 |

Match each changed file path against these patterns. Sum all unique matches
(do not double-count the same file if it matches multiple patterns in the
same row).

---

## Step 2 — Layer Spread

| Layers Touched | Score |
|---|---|
| 1 | +1 |
| 2–3 | +3 |
| 4+ | +5 |

Layers are architectural boundaries (e.g., routes, middleware, services,
repositories, config, infra). Test files do not count as a separate layer.

---

## Step 3 — Change Magnitude

| LOC Changed | Score |
|---|---|
| <150 | +1 |
| 150–500 | +2 |
| 500–1500 | +4 |
| 1500+ | +6 |

Fallback: file-count based estimation (1 file ≈ 50 LOC).

---

## Step 4 — Total Score

`total_score = path_score + layer_score + magnitude_score`

---

## Level Mapping

| Score | Level |
|---|---|
| 0–6 | A |
| 7–13 | B |
| 14+ | C |

---

## Hard Overrides

These rules override the calculated level:

- Auth + multi-layer → minimum B
- Infra change → minimum B
- Migration + medium magnitude → minimum B
- Financial impact → C
- Global middleware + high magnitude → C

---

## Guardrails

- Do not double-count the same file across multiple risk patterns.
- Use only deterministic path matching; do not infer risk from file content unless diff_snippets are provided.
- If LOC and file count are both unavailable, ask for clarification rather than guessing.

---

## Failure Patterns

- Double-counting a file that matches both "config" and ".env" patterns, inflating the score
- Treating test files as production layer spread (tests should not count as a separate architectural layer)
- Ignoring hard overrides after calculating the total score

---

## Example

**Input:**

changed_files: `auth/jwt.ts`, `middleware/auth.ts`, `config/auth.ts`, `routes/login.ts`
diff_summary: 200 LOC

**Output:**

```
Path Score:      +10 (matched: auth +4, middleware +3, config +3)
Layer Score:     +5  (4 layers: auth, middleware, config, routes)
Magnitude Score: +2  (200 LOC)
Total Score:     17
Level:           C
Hard Override:   Auth + multi-layer → minimum B (already exceeded)
```
