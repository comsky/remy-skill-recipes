---
name: notion-format
description: >
  Format and publish rich Notion documents with structured sections, code blocks,
  tables, callouts, quotes, mermaid diagrams, and emojis. Use when the user asks
  to organize, write, or save content to Notion (e.g., "notion에 정리해줘",
  "notion에 저장해줘"), or when invoked with /notion-format.
  Detects content type (tech-doc, meeting-notes, analysis, tutorial, bug-report)
  and applies the appropriate formatting template automatically.
license: MIT
metadata:
  compatibility: Claude Code, Cursor
  type: execution
  category: documentation
  maturity: draft
  estimated_time: 3 min
---

# Skill: Notion Format

**Type:** Execution

## Purpose

Transform unstructured or loosely structured content into richly formatted
Notion-ready documents. Automatically detect content type from keywords and
context, select the matching template, and apply visual formatting elements
(headings, callouts, code blocks, tables, mermaid diagrams, emojis, toggles).

Optionally publish to Notion via MCP.

---

## When to Use

- User says "notion에 정리해줘", "notion에 저장해줘", or similar
- User invokes `/notion-format` explicitly
- Conversation produces output that should be persisted as a structured document
- Raw notes, logs, or analysis results need visual structure before sharing

---

## When NOT to Use

- Content is already well-formatted and user just wants to push to Notion as-is
- User explicitly requests plain text or minimal formatting
- The output is code-only (a script, config file) — not a document
- Content belongs in a database row, not a document page

---

## Inputs Required

Do not run this skill without:

- [ ] Content to format (conversation context, pasted text, or file contents)
- [ ] Identifiable topic or purpose (to detect content type)

Optional but recommended:

- [ ] Explicit content type override (e.g., "기술 문서로 정리해줘")
- [ ] Target Notion parent page ID or database ID (for MCP save)
- [ ] Language preference (Korean / English — default: match input language)

---

## Output Format

1. Detected content type and rationale
2. Formatted Notion-ready Markdown document
3. Notion save prompt (if MCP available)
4. Notion page URL (if saved)

---

## Procedure

### Step 1 — Content Type Detection

Match content against keyword signals. If multiple types match,
use the **priority order** below (first match wins):

| Priority | Type | Keywords / Signals | Emoji |
|---|---|---|---|
| 1 | `bug-report` | 버그, 이슈, 오류, 에러, 장애, 원인, incident, error, stack trace | 🐛 |
| 2 | `meeting-notes` | 회의, 미팅, 논의, 결정사항, 액션아이템, meeting, agenda, attendees | 📋 |
| 3 | `tutorial` | 튜토리얼, 가이드, 사용법, 설치, how-to, step-by-step, prerequisites | 📖 |
| 4 | `tech-doc` | 파이프라인, 아키텍처, API, 스키마, 시스템 설계, spec, schema, infra | 🏗️ |
| 5 | `analysis` | 분석, 비교, 조사, 검토, 결과, 인사이트, benchmark, evaluation, comparison | 📊 |
| 6 | `general` | (fallback — none of the above) | 📝 |

**Priority rationale:** Bug reports and meeting notes have the most
distinctive structure; misclassifying them causes the most damage.
Analysis and tech-doc overlap heavily, so tech-doc takes priority
when both match (structural docs benefit more from mermaid/code blocks).

If the user explicitly states a type, skip detection and use it directly.

---

### Step 2 — Apply Format Template

Each template defines the **section skeleton**. Adapt section count and depth
to actual content — do not generate empty placeholder sections.

섹션 제목 언어는 입력 언어를 따른다 — 아래 스켈레톤은 한국어 예시이며,
영어 콘텐츠에는 동등한 영어 제목을 사용한다 (예: 증상 → Symptoms,
타임라인 → Timeline).

#### `bug-report` 🐛

~~~~
# 🐛 [버그명] 장애 리포트
> **심각도**: 🔴 Critical / 🟡 High / 🟢 Low | **상태**: 조사중 / 해결됨

## 📋 증상
- 발생 현상 bullet

## 🕒 타임라인
| 시각 | 이벤트 |
|---|---|

## 🔬 원인 분석
```
에러 메시지 또는 스택 트레이스
```
> 💡 근본 원인: ... (callout)

## 🛠️ 해결 방법
1. 임시 조치
2. 영구 조치

## 🧪 검증
- [ ] 재현 방법 / 검증 기준

## 📎 관련 이슈
- 링크
~~~~

#### `meeting-notes` 📋

~~~~
# 📋 [날짜] 회의록 — [주제]
> 참석자: A, B, C | 일시: YYYY-MM-DD HH:mm

## 📌 안건
1. ...
2. ...

## 💬 주요 논의
### 안건 1
- 논의 내용 bullet

## ✅ 결정사항
> [결정 내용] — 결정자

## 🎯 액션아이템
| 담당자 | 내용 | 기한 | 상태 |
|---|---|---|---|
| @name | task | YYYY-MM-DD | 🔲 |

## 📅 다음 회의
- 일정 / 안건 예고
~~~~

#### `tutorial` 📖

~~~~
# 📖 [주제] 가이드
> **Prerequisites**: 사전 조건 (callout)

## 🚀 빠른 시작
```bash
핵심 커맨드
```

## 📝 단계별 설명

### Step 1 — [단계명]
설명 ...
```코드```

### Step 2 — [단계명]
...

## 💡 Tips
> 팁 내용 (callout)

## ❓ FAQ
| 질문 | 답변 |
|---|---|

## 📎 관련 자료
- 링크
~~~~

#### `tech-doc` 🏗️

~~~~
# 🏗️ [제목]
> 한 줄 요약 (quote 블록)

## 🎯 개요
- 목적·배경 bullet

## 🏛️ 아키텍처
```mermaid
graph TD / flowchart / sequenceDiagram
```

## ⚙️ 상세 스펙
| 항목 | 값 | 비고 |
|---|---|---|

## 💻 코드 예시
```언어
코드
```

## ⚠️ 주의사항
> ⚠️ WARNING callout

## 📎 참조
- 링크/문서
~~~~

#### `analysis` 📊

~~~~
# 📊 [분석 주제]
> **핵심 요약**: 한 문장 결론 (callout)

## 🔍 분석 배경
- 문제 정의 / 분석 목적

## 📈 데이터 / 근거
| 항목 | 현황 | 목표 | 비고 |
|---|---|---|---|

## 💡 인사이트
1. ...
2. ...

## 🏁 결론 및 권고
> 권고사항 (callout)

## 📎 출처
- 참조 자료
~~~~

#### `general` 📝

No fixed skeleton. Apply these rules:

- 3개 이상 논리 단위 → H2로 섹션 분리
- 나열형 → bullet list 또는 numbered list
- 비교/대조 → table
- 핵심 메시지 → quote 또는 callout
- 코드 포함 시 → 언어 지정 code block
- 문서 상단에 한 줄 요약 quote 블록 추가

---

### Step 3 — Formatting Rules

**항상 적용:**

- 문서 상단에 한 줄 요약 `quote` 블록
- 주요 경고/팁은 `callout` (아이콘 이모지 포함)
- 코드는 반드시 언어 지정 (`python`, `bash`, `typescript`, `json`, `mermaid`, `sql` 등)
- 흐름/구조 설명이 있으면 `mermaid` 다이어그램 추가
- 비교 데이터는 테이블 우선
- 섹션 간 `divider` 삽입
- 섹션 제목에 이모지 포함

**콘텐츠 길이별 조정:**

| 길이 | 포맷 전략 |
|---|---|
| 짧은 (~300자) | 섹션 최소화, callout + quote 위주 |
| 중간 (300~1000자) | 풀 템플릿 적용 |
| 긴 (1000자+) | toggle 블록으로 상세 내용 접기, TOC 역할의 요약 섹션 추가 |

**빈 섹션 금지:** 템플릿 섹션 중 채울 내용이 없으면 해당 섹션을 생략한다.

---

### Step 4 — Notion MCP Save (Optional)

사용자가 이미 저장을 요청한 경우(예: "notion에 저장해줘"로 시작한 요청)에는
다시 묻지 않고 저장을 진행한다. 이때 부모 페이지 ID나 데이터베이스 ID를
모르면 그것만 물어본다.

저장 요청이 없었던 경우에는 포맷팅 완료 후 물어보기:

> "Notion에 저장할까요? 저장할 경우 부모 페이지 ID나 데이터베이스 ID를 알려주세요."

저장 진행 시:

1. `API-post-search`로 동일 제목 페이지 존재 여부 확인
2. 없으면 `API-post-page`로 신규 생성
3. 이미 존재하면 사용자에게 "동일 제목의 페이지가 있습니다. 덮어쓸까요?" 확인 후 `API-patch-block-children`으로 업데이트
4. 완료 후 Notion 페이지 URL 반환

**Notion Block 타입 매핑:**

| Markdown / 요소 | Notion Block type |
|---|---|
| `# H1` | `heading_1` |
| `## H2` | `heading_2` |
| `### H3` | `heading_3` |
| 일반 텍스트 | `paragraph` |
| `- bullet` | `bulleted_list_item` |
| `1. list` | `numbered_list_item` |
| `- [ ] checkbox` | `to_do` |
| ` ```code``` ` | `code` (language 지정) |
| `> quote` | `quote` |
| callout (이모지 + 강조 텍스트) | `callout` (icon emoji 포함) |
| `---` | `divider` |
| 테이블 | `table` + `table_row` |
| toggle (접기) | `toggle` |
| URL 단독 | `bookmark` |
| 이미지 URL | `image` (external) |

---

## Guardrails

- 콘텐츠가 비어있거나 너무 짧으면(<20자) 추가 입력 요청
- 명시적 저장 요청이 없으면 Notion 저장 전 사용자 확인 (이미 요청했다면
  재확인 없이 진행하되, parent ID를 모르면 그것만 확인)
- 기존 페이지 덮어쓰기 시 명시적 동의 필요
- Notion MCP 불가 시 포맷팅된 마크다운만 제공하고 경고 메시지 출력
- parent_id 미제공 시 workspace 최상위에 저장하지 말고 사용자에게 요청
- 사용자가 명시한 콘텐츠 타입이 있으면 자동 감지를 무시
- 빈 섹션을 placeholder로 남기지 않음

---

## Failure Patterns

Common bad outputs:

- 콘텐츠 타입을 잘못 감지해 회의록을 tech-doc 형태로 포맷팅
- 모든 섹션을 비어있는 채로 남겨둔 스켈레톤만 출력 (빈 섹션 금지 규칙 위반)
- mermaid 다이어그램을 언어 지정 없이 일반 코드 블록으로 출력
- 긴 문서에서 toggle 없이 모든 내용을 펼쳐 가독성 저하
- Notion 저장 시 동일 제목 페이지를 확인하지 않고 중복 생성
- callout을 일반 quote로 대체해 시각적 강조 효과 상실
- 이모지를 섹션 제목에서 누락해 밋밋한 구조 생성
- 사용자가 명시한 타입을 무시하고 자동 감지 결과를 사용
- 사용자가 이미 저장을 요청했는데 "저장할까요?"를 다시 물어 흐름을 끊음

---

## Example 1 (Minimal Context)

**Input:**

사용자가 대화 중 정리한 내용:
"Redis 캐시 도입 검토. 현재 DB 직접 조회로 응답시간 200ms. 캐시 적용 시 예상 50ms. TTL은 5분으로 설정. 만료 전략은 LRU. 비용은 월 $50 추가."

**Output:**

Detected type: `analysis` (검토 키워드 + 수치 비교 구조)

~~~~
# 📊 Redis 캐시 도입 검토
> **핵심 요약**: DB 직접 조회 대비 응답시간 75% 개선 예상 (200ms → 50ms), 월 $50 추가 비용

---

## 🔍 분석 배경
- 현재 DB 직접 조회 방식의 응답시간 병목 해소 필요

## 📈 비교 분석
| 항목 | 현재 (DB 직접) | 캐시 적용 후 |
|---|---|---|
| 응답시간 | 200ms | ~50ms |
| 월 비용 | - | +$50 |
| TTL | - | 5분 |
| 만료 전략 | - | LRU |

## 🏁 결론 및 권고
> 💡 응답시간 75% 개선 효과 대비 비용이 합리적. 도입 권고.
~~~~

---

## Example 2 (Realistic Scenario)

**Input:**

사용자가 장애 대응 내용을 정리 요청:
"오늘 14시에 결제 API에서 500 에러 발생. 원인은 PG사 인증서 만료. 15시에 인증서 교체 후 복구. 재발 방지를 위해 인증서 만료 30일 전 알림 설정 필요. 영향 범위는 약 200건 결제 실패."

**Output:**

Detected type: `bug-report` (에러, 장애, 원인 키워드)

~~~~
# 🐛 결제 API 500 에러 — PG사 인증서 만료
> **심각도**: 🔴 Critical | **상태**: 해결됨

---

## 📋 증상
- 결제 API에서 500 Internal Server Error 반환
- 약 200건 결제 실패 발생

## 🕒 타임라인
| 시각 | 이벤트 |
|---|---|
| 14:00 | 결제 API 500 에러 최초 감지 |
| 14:00~15:00 | 원인 분석 — PG사 인증서 만료 확인 |
| 15:00 | 인증서 교체 완료, 서비스 복구 |

## 🔬 원인 분석
> 💡 근본 원인: PG사 SSL/TLS 인증서 만료로 인한 연동 실패

## 🛠️ 해결 방법
1. **임시 조치**: PG사 인증서 수동 교체 (15:00 완료)
2. **영구 조치**: 인증서 만료 30일 전 자동 알림 설정

## 🧪 검증
- [ ] 결제 API 정상 응답 확인
- [ ] 인증서 만료 알림 스크립트 동작 테스트

## 📎 관련 이슈
- 영향: 약 200건 결제 실패 (14:00~15:00)
~~~~

---

## Notes

**FAST MODE** (only if explicitly requested):

- 콘텐츠 타입 감지 생략 → `general` 적용
- 섹션 최소화 (H2 + bullet 위주)
- Step 4 (Notion save) 건너뜀
