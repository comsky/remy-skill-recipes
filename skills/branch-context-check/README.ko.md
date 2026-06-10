# Branch Context Check (브랜치 컨텍스트 점검)

스테이징, 커밋, 푸시, 또는 다른 세션의 작업을 이어가기 전에
현재 Git 브랜치, 업스트림 상태, dirty working tree가 현재 작업 목적과
맞는지 검증합니다.

이 스킬은:

- 새 커밋이 추가되기 전에 오래된 브랜치 재사용을 탐지
- 현재 작업 목적을 브랜치 이름, 최근 커밋, dirty 파일과 비교
- 현재 세션 변경과 이전 세션/소유 불명 변경을 분리
- 새 브랜치 또는 워크트리가 필요한 상황을 권고
- 애매하거나 위험한 파일 소유권이 확인되기 전까지 커밋 흐름을 중단

---

## 왜 필요한가

에이전트는 현재 checkout된 브랜치에서 그대로 작업을 이어가기 쉽습니다.
그 브랜치와 dirty 파일이 현재 작업과 맞을 때만 안전합니다. 이 스킬은
커밋 경계에서 가벼운 Git 컨텍스트 게이트를 추가해, 서로 다른 세션의
작업이 새 작업에 섞이는 사고를 줄입니다.

---

## 절차 (6-Gate)

0. **Task Intent Capture** — Git 확인 전에 현재 작업 목적 요약
1. **Git Context Snapshot** — 브랜치, 업스트림, dirty 파일, 최근 커밋 확인
2. **Branch Intent Inference** — 브랜치 목적과 현재 작업 비교
3. **Dirty Worktree Ownership** — 현재 세션, 이전 세션, staged, 소유 불명 파일 분류
4. **Decision Matrix** — `match`, `ambiguous`, `mismatch`, `blocked` 판정
5. **Handoff** — 위험 상태에서는 스테이징/커밋 전 사용자 확인 요구

---

## 구조

- [SKILL.md](SKILL.md) — 메인 스킬

