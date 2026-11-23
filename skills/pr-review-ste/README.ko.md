# PR Review STE (PR 리뷰 → STE 댓글)

GitHub PR 하나 이상을 지정한 강도로 리뷰하고, 지적마다 PR head 에서 확인한 뒤
PR 마다 리뷰 하나를 게시합니다. 댓글은 저장소 언어(한국어 또는 영어)로 STE
원칙을 적용해 쓰고 P0–P3 우선순위를 표시합니다. `--fix` 를 붙이면 PR 브랜치에서 지적을 고치고 결과를
지적마다 남깁니다.

이 스킬은:

- 머지됨·닫힘·초안 PR 을 건너뜀
- 강도(`low` · `medium` · `high` · `xhigh` · `max`)별로 범위와 개수를 고정. ADR PR 은 기본 `xhigh`
- 호스트에 `/code-review` 가 있으면 그 결과를 후보로 받음. 없으면 자체 관점 표로 리뷰
- 구체적인 실패 시나리오가 있는 지적만 남김
- 댓글을 저장소 언어로 씀: `--lang`, 규칙 파일, 최근 PR·리뷰 댓글 순으로 정함. 한국어 → 한국어, 그 밖의 언어 → 영어
- 같은 계약의 양쪽인 PR 을 맞대어 확인
- 우선순위로 리뷰 이벤트를 정함: P0 → `REQUEST_CHANGES`, P3 만 → `APPROVE`, 그 밖 → `COMMENT`
- 게시하는 글에 리뷰 방법·도구 이름·강도를 쓰지 않음
- `--fix`: 격리 워크트리에서 고치고, 커밋 하나를 force 없이 푸시하고, 결과를 게시

---

## 왜 필요한가

리뷰 댓글이 막연하거나, 우선순위가 부풀려지거나, 과정 설명이 섞이면 가치가
떨어집니다. 강도별 범위 고정, 실패 시나리오 요구, 스크립트가 정하는 리뷰
이벤트로 모든 댓글을 구체적으로 유지하고 PR 마다 판정을 일관되게 맞춥니다.

---

## 절차 (7단계)

1. **대상 확인** — 상태, head SHA, ADR 여부 확인. 댓글 언어 결정. diff 와 head ref 가져오기
2. **강도별 리뷰** — `/code-review`(없으면 강도 표의 관점)로 후보를 받고 PR head 에서 후보마다 확인
3. **우선순위** — 부풀리거나 낮추지 않고 P0–P3 지정
4. **STE 문체** — 한 문장에 한 사실, 정한 언어로(한국어 합니다체 또는 쉬운 영어), 방법 언급 없음
5. **게시** — findings JSON → `post_review.py --dry-run` → 게시
6. **수정 (`--fix` 만)** — 격리 워크트리, 검사, 커밋 하나, 푸시, 결과 댓글
7. **최종 보고** — 실행마다 표 하나

---

## 게시 형식

우선순위 표시: 🚨 P0 차단 · ⚠️ P1 머지 전 수정 · 💡 P2 수정 권장 · 💬 P3 선택.
영어: 🚨 P0 Blocking · ⚠️ P1 Fix before merge · 💡 P2 Fix recommended · 💬 P3 Optional.

아래 예시는 한국어입니다. 영어 저장소는 같은 모양에 영어 레이블과 머리글
(`| Priority | Finding | Location |`)을 씁니다. 지적이 없으면 본문은
`🎉🎉🎉 지적할 항목이 없습니다. 🎉🎉🎉`(영어: `🎉🎉🎉 No findings. 🎉🎉🎉`) 한 줄입니다.

리뷰 본문은 건수 표 다음에 지적마다 한 행을 둡니다. diff 안 줄의 지적은
인라인 댓글(`⚠️ **P1** …`)로 달고, diff 밖 지적은 표 아래에 상세를 붙입니다.

```markdown
| 우선순위 | 건수 |
| --- | ---: |
| ⚠️ P1 머지 전 수정 | 1 |
| 💬 P3 선택 | 1 |

| 우선순위 | 지적 | 위치 |
| --- | --- | --- |
| ⚠️ P1 | 필터를 모두 지우면 조회 조건이 `null` 로 저장됩니다 | [`filters.ts:58`](…#L58) |
| 💬 P3 | `formatRange` 가 `toRangeLabel` 과 같은 일을 합니다 | [`Header.tsx:21`](…#L21) |
```

`--fix` 결과 댓글도 같은 모양입니다. 결과별 건수 표, 수정 커밋 링크, 지적마다
한 행 순서입니다.

```markdown
| 결과 | 건수 |
| --- | ---: |
| ✅ 수정 | 1 |
| ⏭️ 건너뜀 | 1 |

수정 커밋: [`0123456ab`](…)

| 결과 | 우선순위 | 지적 | 위치 | 사유 |
| --- | --- | --- | --- | --- |
| ✅ 수정 | ⚠️ P1 | 필터를 모두 지우면 조회 조건이 `null` 로 저장됩니다 | [`filters.ts:58`](…#L58) |  |
| ⏭️ 건너뜀 | 💬 P3 | `formatRange` 가 `toRangeLabel` 과 같은 일을 합니다 | [`Header.tsx:21`](…#L21) | 다른 PR 범위입니다 |
```

---

## 사용

```text
/pr-review-ste 3338 3339
/pr-review-ste xhigh 3338
/pr-review-ste --fix 3338
/pr-review-ste --lang en 3338
```

인증된 `gh` 와 Python 3.9 이상이 필요합니다.

---

## 구조

- [SKILL.md](SKILL.md) — 메인 스킬
- [scripts/post_review.py](scripts/post_review.py) — 리뷰 또는 수정 결과 댓글을 만들고 게시
- [scripts/detect_lang.py](scripts/detect_lang.py) — 최근 PR·리뷰 댓글로 댓글 언어(`ko` 또는 `en`) 감지
- [references/finder-brief.md](references/finder-brief.md) — 큰 PR·여러 PR 용 서브 에이전트 브리프
