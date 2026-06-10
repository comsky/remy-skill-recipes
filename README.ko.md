# Remy Skill Recipes (한국어 안내)

이 레포는 LLM을 활용한 엔지니어링 작업을
구조화하기 위한 "스킬 레시피" 모음입니다.

단순 프롬프트 모음이 아닙니다.
재사용 가능하고 실패 확률을 줄이는 구조화된 워크플로우 시스템입니다.

모든 스킬은 [SKILL.md 오픈 표준](https://agentskills.io/)을 따릅니다.
Cursor, Claude Code, VS Code + Copilot, Codex, Gemini CLI 등 SKILL.md 호환 에이전트에서 사용할 수 있습니다.

---

## 스킬 목록

| 스킬 | 유형 | 설명 |
|---|---|---|
| [architecture-spec](skills/architecture-spec/) | Execution | 리스크 기반 아키텍처 문서 자동 생성 (A/B/C 레벨) |
| [branch-context-check](skills/branch-context-check/) | Execution | 스테이징/커밋/푸시 전 브랜치와 워크트리 목적 일치 여부 점검 |
| [change-reaudit](skills/change-reaudit/) | Execution | 코드 변경 재감사 — 사이드 이펙트, 회귀, 엣지 케이스 |
| [competitive-feature-benchmark](skills/competitive-feature-benchmark/) | Execution | 경쟁 제품 UX/인터랙션 수준 비교 분석 |
| [docs-finalize-and-commit](skills/docs-finalize-and-commit/) | Execution | 문서 컨벤션 탐색 및 일관성 검증 후 커밋 |
| [finalize-and-commit](skills/finalize-and-commit/) | Execution | 코드 최종 정리 — 중복 제거, 하드코딩 감사, 클린 커밋 |
| [notion-format](skills/notion-format/) | Execution | 콘텐츠 타입 자동 감지 및 Notion 문서 리치 포맷팅 |
| [oss-code-analysis](skills/oss-code-analysis/) | Execution | OSS 레포 코드 수준 분석 (비교/심층 모드) |
| [ux-sentinel](skills/ux-sentinel/) | System | 반복 UX 개념 자동 감지 및 Notion DB 등록 |

---

## 빠른 시작

### 스킬 설치

[skills.sh 마켓](https://skills.sh/comsky/remy-skill-recipes)에서 전체 스킬을 한 번에 설치할 수 있습니다:

```bash
npx skills add comsky/remy-skill-recipes
```

또는 개별 스킬을 직접 복사합니다:

```bash
# Cursor
cp -r skills/change-reaudit ~/.cursor/skills/

# Claude Code
cp -r skills/change-reaudit ~/.claude/skills/

# VS Code + Copilot (.claude/skills/ 자동 인식 또는 전용 경로 사용)
cp -r skills/change-reaudit ~/.copilot/skills/
```

에이전트가 자동으로 스킬을 탐색하고 매칭되는 작업에 활성화합니다.

### 직접 사용

1. `skills/` 폴더에서 스킬을 선택합니다.
2. Execution인지 System인지 구분합니다.
3. 입력 조건을 반드시 확인합니다.
4. 출력 결과를 체크리스트로 검증합니다.

입력 정보가 부족하면 결과 품질이 급격히 낮아집니다.

---

## 스킬 포맷

모든 스킬은 `SKILL.md` 파일이 있는 폴더로 구성됩니다:

```yaml
---
name: change-reaudit
description: >
  코드 변경사항을 재감사하여 사이드 이펙트, 회귀 위험,
  미처리 엣지 케이스를 식별합니다.
license: MIT
compatibility:
  - Claude Code
  - Cursor
metadata:
  type: execution
  category: review
---
```

에이전트는 탐색 단계에서 `name`과 `description`만 읽습니다 (~100 토큰).
전체 마크다운 본문은 활성화 시 로딩됩니다 (<5000 토큰).

---

## 스킬 유형

### 1. Execution Skill (단발 실행형)

한 번 실행하는 구조화된 워크플로우입니다.

예:

- 코드 변경 재감사
- 경쟁 제품 비교
- 리팩토링 검증
- 설계 문서 작성

특징:

- 명확한 입력 요구사항
- 엄격한 출력 형식
- Guardrails 포함
- 실패 패턴 명시
- 최소 2개 예시 포함

---

### 2. System Skill (지속/자동화형)

대화 전반 또는 외부 시스템과 연동되어
지속적으로 동작하는 스킬입니다.

예:

- UX 개념 반복 감지
- Notion DB 동기화
- 상태 기반 자동 처리

특징:

- Activation 규칙 존재
- 상태 유지 (대화 / 외부 DB)
- 명확한 Side Effect 정의
- 중복 방지 및 운영 Guardrails 포함

---

## 설계 철학

LLM은 구조 없이 사용하면 불안정합니다.

이 레포는 다음을 줄이기 위해 설계되었습니다:

- 환각
- 모호성
- 과도한 추론
- 맥락 손실

Execution Skill은 단일 작업의 안정성을 높이고,
System Skill은 반복되는 패턴을 구조화합니다.

프롬프트는 감각이 아니라 엔지니어링입니다.

---

## 기여 규칙

- 올바른 템플릿 사용 (`_template/execution-template.md` 또는 `_template/system-template.md`)
- SKILL.md 표준 준수 (YAML frontmatter 필수)
- Guardrails 필수
- Failure Patterns 필수
- 현실적인 예시 최소 2개 포함

---

## 라이선스

MIT
