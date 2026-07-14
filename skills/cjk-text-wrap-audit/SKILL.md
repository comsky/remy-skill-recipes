---
name: cjk-text-wrap-audit
description: >
  Diagnose and fix CJK (Korean, Japanese, Chinese) text-wrapping issues
  in web UIs. Systematically traces mid-syllable breaks, orphaned
  glyphs, and awkward line splits through a layered fix strategy
  covering global CSS cascade, component-library overrides, headline
  balancing, and translation-level phrase binding. Produces an
  evidence-based diagnosis and verification report before any code
  change is applied.
license: MIT
metadata:
  compatibility: Claude Code, Cursor
  type: execution
  category: review
  maturity: draft
  estimated_time: 15 min
---

# Skill: CJK Text Wrap Audit

**Type:** Execution

## Purpose

Turn ad-hoc CJK (Korean, Japanese, Chinese) line-break firefighting into
a layered, evidence-first audit. CJK wrap bugs are a class of
cross-cutting cascade defects: a missing locale-scoped `word-break`
rule, an Ant Design / MUI / Mantine `cssinjs` override that wins on
specificity, an over-eager `text-wrap` algorithm, and a translation
string with no phrase boundary can each independently cause text to
shatter mid-syllable or strand a single glyph at line edge.

This skill prescribes a fixed sequence of diagnostic gates so the audit
produces an evidence-backed report — codepoint dump, computed-style
trace, and verification matrix — *before* any code is changed.

---

## When to Use

- Korean / Japanese / Chinese hero or headline text breaks mid-syllable.
- A single glyph or word is orphaned at the end or start of a line.
- The bug appears only in CJK locales while Latin locales render fine.
- A user reports an awkward break in a screenshot but the code "looks
  right".
- Browser zoom (WCAG 1.4.4 Resize Text) reveals breaks that are
  invisible at 100%.
- A previous "fix" used `<br>`, hardcoded widths, or `!important` and
  the bug came back.

---

## When NOT to Use

- Pure Latin or RTL wrapping issues (use a generic CSS audit instead).
- Font-loading or glyph-substitution problems (FOUT / FOIT, missing
  glyphs, fallback fonts).
- Print or PDF rendering pipelines (different break algorithm).
- Plain-text terminals or markdown `pre` blocks (wrap is a terminal
  concern, not CSS).
- Layout overflow caused by fixed widths or `white-space: nowrap`,
  not by wrapping behavior.

---

## Inputs Required

Do not run this skill without:

- [ ] Screenshot of the offending render at the actual breakpoint.
- [ ] Locale code and the raw translation string (file path + key).
- [ ] Path to the component file containing the element.
- [ ] Live URL or deterministic repro steps.
- [ ] CSS / component framework in use (Tailwind, Ant Design, MUI,
      Mantine, Chakra, plain CSS, …).
- [ ] Browser and zoom level where the bug reproduces.

Optional but recommended:

- [ ] List of all CJK locales the project ships.
- [ ] Light/dark mode information if the affected text changes color.
- [ ] Prior commit(s) that touched the same string or component.

Without asking the user (unless unavailable), gather these inputs
directly from the repository and the running app.

---

## Output Format

Produce a structured 7-section report. Do not produce code changes
until Section 7 is approved.

1. **Symptom Report** — locale, breakpoint, browser, zoom, screenshot
   reference, exact observed break (quote the broken line).
2. **Diagnosis** — codepoint dump of the raw string, computed values
   of `word-break` / `overflow-wrap` / `text-wrap` / `hyphens` /
   `line-break`, and the cascade trace identifying the *winning*
   declaration with its specificity.
3. **Root Cause** — name the failing layer: global CSS, component
   library injector, headline balancing algorithm, or translation
   string itself.
4. **Fix Strategy** — which of the four layers to touch, in what
   order, and *why* additional layers are or are not needed.
5. **Proposed Patch** — minimal concrete diffs (file path + before /
   after). No speculative refactors.
6. **Verification Plan** — explicit matrix of zoom levels ×
   breakpoints × locales × theme modes to be re-checked.
7. **Approval Gate** — explicit statement: "Awaiting approval before
   applying patch." Do not edit code until the user confirms.

---

## Procedure

### Gate 0 – Symptom Capture

Collect screenshot, URL, locale code, breakpoint width, browser, and
zoom level. If any item is missing, request it before proceeding.
Quote the offending broken line verbatim from the screenshot so later
gates have an unambiguous target.

Halt if no screenshot or repro is available — visual bugs cannot be
audited from descriptions alone.

---

### Gate 1 – Raw String Forensics

Read the translation file containing the offending key. Dump the
target string as Unicode codepoints (e.g., `U+C774 U+B3D9 U+D558
U+C138 U+C694`) and annotate:

- Existing NBSP (`U+00A0`), zero-width joiner (`U+200D`), zero-width
  space (`U+200B`), or soft hyphen (`U+00AD`) — any of these may
  already be influencing the wrap.
- Logical phrase boundaries — mark which adjacent words form a
  semantic unit that should not split (e.g., Korean 어절 / Japanese
  文節 / Chinese 词组).
- Latin-script substrings — these still wrap by Latin rules even
  inside a CJK string.

Output: a labeled codepoint table and a phrase-boundary map.

---

### Gate 2 – Computed Style Inspection

Read the affected component file. Then trace the computed CSS for the
broken element. Document the *winning* declaration (with selector and
specificity) for each of:

- `word-break`
- `overflow-wrap` (and legacy `word-wrap`)
- `text-wrap` (`wrap` / `nowrap` / `balance` / `pretty`)
- `hyphens`
- `line-break`

Note any `white-space` value other than `normal` — it changes wrap
semantics entirely.

If the component is wrapped by a UI library (Ant Design `Typography`,
MUI `Typography`, Mantine `Text`, Chakra `Text`, …), record the
library's injected class and where its rule comes from.

---

### Gate 3 – Override Tracing

For each library identified in Gate 2, locate the injected stylesheet
(usually via `cssinjs` / `emotion` / `stitches`) and capture the rule
that is in effect. Calculate its specificity.

Common offenders:

- Ant Design `Typography`: injects `.ant-typography { word-break:
  break-word }` (specificity 0,1,0).
- MUI `Typography`: injects `.MuiTypography-root { … }` similarly.
- Tailwind preflight: `body` defaults can be overridden by any
  component class.

Identify a *safe* override location and selector. Prefer:

- The doubled-class trick: `.ant-typography.ant-typography { … }`
  (specificity 0,2,0) — beats the library's single-class rule
  *without* `!important`.
- Locale scoping with `:lang(ko)` on the element — a pseudo-class
  *adds* 0,1,0 specificity (unlike `:where()`, which erases it) and
  keeps wrap overrides away from `ja` / `zh` text.
- A scoped wrapper class on the page or layout level.

Avoid:

- `:where(.ant-typography)` — `:where()` collapses specificity to
  `0,0,0`. The override will *lose* every cascade contest.
- `!important` — wins, but pollutes future overrides and is hard to
  audit.

---

### Gate 4 – Layered Fix Proposal

Propose the minimum number of layers needed. Stop at the first layer
that fully resolves the symptom; only escalate if the verification
matrix in Gate 5 still has failing cells.

**Layer 1 — Global cascade.** Add a locale-scoped base rule:

```css
/* Korean only. ja/zh have no inter-word spaces — keep-all would
   remove every break opportunity there and cause overflow. */
:lang(ko) {
  word-break: keep-all;
  overflow-wrap: break-word;
}

/* Always exempt monospace contexts. */
code, pre, kbd, samp {
  word-break: normal;
  overflow-wrap: normal;
}
```

The UA default (`word-break: normal`) allows a break between any two
CJK syllables — that is what shatters Korean mid-word. `keep-all`
forbids those intra-word breaks; Korean still wraps at spaces (어절
boundaries). Japanese and Chinese are written *without* spaces, so
`keep-all` would leave them no break opportunity at all — never apply
it to `ja` / `zh`. For `ja`, keep default breaking (optionally
`line-break: strict` for stricter kinsoku punctuation rules) and bind
phrases at Layer 4 or with a phrase segmenter such as BudouX. For
`zh`, the default break-anywhere behavior is correct.
`overflow-wrap: break-word` is the safety net for very long Latin
tokens. `:lang(ko)` relies on a correct `lang` attribute
(`<html lang="ko">` or on the locale subtree) — most i18n frameworks
set it; verify during Gate 2.

**Layer 2 — Component-library override.** If a UI library injects a
stronger rule, neutralize it at the same scope:

```css
.ant-typography.ant-typography:lang(ko) {
  word-break: keep-all;
  overflow-wrap: break-word;
}
```

(Adjust the selector for whichever library is in use. Use the
doubled-class trick rather than `!important`, and keep the
`:lang(ko)` scope so the override never reaches `ja` / `zh` text.)

**Layer 3 — Headline-specific balancing.** For hero / headline text
where line-length aesthetics matter, add a balanced wrap on the
specific element:

```html
<h1 class="text-balance">…</h1>
```

`text-wrap: balance` (Tailwind utility `text-balance`, or raw CSS)
distributes characters evenly across lines and prevents single-word
orphans on the last line. Use `text-pretty` only if `balance` is too
expensive (it's a hint, not a guarantee).

**Layer 4 — Translation-level phrase binding.** When a specific
phrase must move as a unit (e.g., a verb + its object), insert NBSP
(`\u00a0`) between the words *in the translation file*, not in
JSX:

```json
{
  "hero.title2": "더 스마트하게 구축하고, 더\u00a0빠르게\u00a0이동하세요"
}
```

Use NBSP only for short, semantically tight phrases (≤4 words). Long
NBSP runs prevent any wrapping at all and will overflow on narrow
screens.

---

### Gate 5 – Verification Matrix

Build an explicit matrix and mark pass/fail for every cell:

| Axis        | Values                                          |
| ----------- | ----------------------------------------------- |
| Zoom        | 100%, 125%, 150%, 200% (WCAG 1.4.4)             |
| Breakpoint  | sm, md, lg, xl (whatever the project ships)     |
| Locale      | Every CJK locale + at least one Latin control   |
| Theme       | Light, Dark (only if rendering depends on it)   |

Re-test all cells after every layer added in Gate 4. The fix is only
complete when every cell passes. Latin-locale regressions count as
failures even if the CJK bug is resolved.

---

### Gate 6 – Approval Gate

Present the full report (Sections 1–6 above) plus the proposed patch.
State explicitly: "Awaiting approval before applying patch." Do not
edit any file until the user confirms.

After approval, apply the patch *exactly* as proposed and re-run
Gate 5 on the live build. Report the matrix again.

---

## Guardrails

- Never use `!important` to win a specificity contest. Use the
  doubled-class trick (`.foo.foo`) instead.
- Never wrap framework overrides in `:where(...)`. It collapses
  specificity to 0 and the override will silently lose.
- Never apply `word-break: keep-all` to `code`, `pre`, `kbd`, or
  `samp`. Always carve out monospace contexts.
- Never apply `word-break: keep-all` to Japanese or Chinese text.
  They have no inter-word spaces, so `keep-all` removes every break
  opportunity and causes overflow. Scope the rule with `:lang(ko)`.
- Never edit a translation file without first dumping the existing
  string as Unicode codepoints. Hidden characters (NBSP, ZWJ, soft
  hyphens) are common and easy to miss.
- Use NBSP only for short, semantically tight phrases (≤4 words).
  Long NBSP runs prevent wrapping entirely and cause overflow on
  narrow screens.
- Do not add hardcoded `max-width` or `width` to "fix" wrapping. It
  masks the cascade bug and breaks at other breakpoints.
- Do not use `<br>` for wrap control. It does not survive translation
  length variance and breaks the moment another locale is added.
- Verify the fix in the *actual* component, not in DevTools-only
  edits. DevTools changes don't capture cssinjs injection order.
- Always test at ≥150% browser zoom. WCAG 1.4.4 requires text to
  remain usable at 200%, and CJK breaks often only appear when zoomed.
- Always test every CJK locale the project ships, not just the
  reported one. The same string can wrap differently across `ko`,
  `ja`, and `zh`.
- Confirm the fix does not regress Latin locales (`en`, `de`, `fr`,
  `es`, …). German is ~30% longer and is the canonical regression
  case for headline wrapping.
- Do not change directory structure or extract shared utilities as
  part of this audit. Stay scoped to the bug.
- Honor the project's existing styling convention. If the project
  uses Tailwind utilities, prefer `text-balance` over inline
  `style={{ textWrap: 'balance' }}`.

---

## Failure Patterns

Common bad outputs:

- Applying `word-break: keep-all` globally without exempting
  `code` / `pre` — breaks code blocks across the entire app.
- Applying `word-break: keep-all` unscoped (e.g., on `body`) in a
  product that also ships `ja` / `zh` — those locales have no spaces,
  so whole clauses become unbreakable and overflow narrow screens.
- Wrapping the override in `:where(.ant-typography)` — specificity
  drops to 0, the library rule wins, and the "fix" silently has no
  effect.
- Adding `text-wrap: balance` *without* fixing the underlying cascade
  — balances the broken text into a *different* broken layout.
- Inserting NBSP between every word in a string — text refuses to
  wrap on narrow screens, causing horizontal overflow.
- Editing the JSX but not the *Korean* translation file (or only the
  English one) — the bug persists in the actual locale that has the
  problem.
- Testing only at 100% zoom — ships a fix that breaks at 150% or
  200%.
- Using `<br>` to force a break — works once, breaks the moment copy
  changes or another locale is added.
- Hardcoding a `max-width` to dodge the issue — masks the cascade
  bug and reintroduces overflow at unrelated breakpoints.
- Treating a single-glyph orphan as "by design" without first
  checking the cascade for a missing rule.
- Skipping the codepoint dump in Gate 1 — missing pre-existing NBSP
  or ZWJ that would have explained the symptom in seconds.

---

## Example 1 (Minimal Context)

**Input:**

A single Korean `<h1>` in a plain Tailwind project breaks as
`이동하세` / `요` at the `md` breakpoint. No UI library is in use.
Project has no global `word-break` rule.

**Output:**

1. **Symptom Report** — locale `ko`, breakpoint `md` (768px), Chrome
   123, zoom 100%, line broken as `이동하세` / `요`.
2. **Diagnosis** — codepoints `U+C774 U+B3D9 U+D558 U+C138 U+C694`
   (no hidden characters). Computed `word-break: normal` (UA
   default). Cascade winner: user-agent stylesheet.
3. **Root Cause** — Layer 1 (global cascade). UA default
   `word-break: normal` allows breaks between any two CJK syllables.
4. **Fix Strategy** — Layer 1 only. No library override or balancing
   needed.
5. **Proposed Patch** — add to `src/styles/globals.css`:
   ```css
   :lang(ko) { word-break: keep-all; overflow-wrap: break-word; }
   code, pre, kbd, samp { word-break: normal; overflow-wrap: normal; }
   ```
6. **Verification Plan** — re-test at 100/125/150/200% × sm/md/lg ×
   `ko` and `en`.
7. **Approval Gate** — Awaiting approval before applying patch.

---

## Example 2 (Realistic Scenario)

**Input:**

A SaaS admin portal's Korean login hero shows three rotating slogans
built with Ant Design `<Typography.Title>`. Slogan 2 reads
`"더 스마트하게 구축하고, 더 빠르게 이동하세요"` and breaks as
`"이동하세"` / `"요"` at `lg`. Project uses Tailwind 3 + Ant Design 5.
Hero element is `src/pages/login/index.tsx`. Translation key
`login.hero.title2` lives in `public/locales/ko/common.json`.

**Output:**

1. **Symptom Report** — locale `ko`, breakpoint `lg` (1024px), Chrome
   123, zoom 100% and 150%, line broken as `이동하세` / `요`. Bug
   reproduces only in `ko`; `en` renders fine.

2. **Diagnosis** — codepoint dump of the raw string contains no
   NBSP / ZWJ / soft hyphens. Computed style on the `<h1>` shows
   `word-break: break-word` winning from `.ant-typography`
   (specificity 0,1,0), overriding the project's
   `body { word-break: keep-all }` (specificity 0,0,1). `text-wrap`
   is `wrap` (default).

3. **Root Cause** — Layers 1 + 2 + 3 + 4 are all required:
   - Global rule was unscoped (`body`) and missing the monospace
     exemption; it must move to `:lang(ko)`.
   - Ant Design's `cssinjs` rule wins over `body`.
   - Even after the override, `text-wrap: wrap` will orphan `더` on
     the previous line because the natural break lands one word
     short.
   - The phrase `더 빠르게 이동하세요` is semantically a single unit
     and must move together.

4. **Fix Strategy** — apply all four layers in order; verify after
   each.

5. **Proposed Patch:**

   `src/index.css` (replaces the existing unscoped `body` rule):
   ```css
   /* Korean-scoped text wrapping */
   :lang(ko) {
     word-break: keep-all;
     overflow-wrap: break-word;
   }
   code, pre, kbd, samp {
     word-break: normal;
     overflow-wrap: normal;
   }
   /* Ant Design override — doubled-class beats single-class without !important */
   .ant-typography.ant-typography:lang(ko) {
     word-break: keep-all;
     overflow-wrap: break-word;
   }
   ```

   `src/pages/login/index.tsx` (hero `<Title>`, three places):
   ```tsx
   <Title
     level={1}
     className="!mb-3 text-4xl md:text-5xl lg:text-6xl text-balance"
     style={{ color: 'var(--color-heading)' }}
   >
   ```

   `public/locales/ko/common.json`:
   ```diff
   - "title2": "더 스마트하게 구축하고, 더 빠르게 이동하세요"
   + "title2": "더 스마트하게 구축하고, 더\u00a0빠르게\u00a0이동하세요"
   ```

6. **Verification Plan** — matrix:

   | Cell                          | Result    |
   | ----------------------------- | --------- |
   | 100% / lg / ko / dark         | pass      |
   | 125% / lg / ko / dark         | pass      |
   | 150% / lg / ko / dark         | pass      |
   | 200% / lg / ko / dark         | pass      |
   | 100% / md / ko / dark         | pass      |
   | 100% / xl / ko / light        | pass      |
   | 100% / lg / en / dark (control) | pass    |

7. **Approval Gate** — Awaiting approval before applying patch.

---

## Notes

**FAST MODE** (only if explicitly requested):

- Skip Gate 5's full matrix. Test only the reported zoom and
  breakpoint, plus 150% as a WCAG sanity check.
- Still produce Gates 1–4. Diagnosis without verification is
  acceptable in fast mode; fixes without diagnosis are not.
