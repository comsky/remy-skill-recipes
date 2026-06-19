# Frontend Decision Sync (프론트엔드 결정 동기화)

프론트엔드 작업 중 생긴 재사용 가능한 결정사항을 프로젝트 문서에
지속 가능한 형태로 반영합니다.

이 스킬은:

- 구현 변경에서 오래 유지되어야 할 프론트엔드 결정을 추출
- 각 결정을 적절한 source of truth에 매핑
- 컴포넌트 문서, 디자인 시스템 문서, 에이전트 지시 파일을 갱신
- 일회성 구현 디테일이 전역 규칙으로 승격되는 것을 방지
- 기록한 항목, 제외한 항목, 검증 결과를 요약

---

## 왜 필요한가

프론트엔드 일관성은 구현 중 내려진 결정이 PR이나 대화 안에만 남을 때
자주 무너집니다. 이 스킬은 재사용 가능한 UI 결정을 프로젝트 기억으로
옮겨 이후 작업에서 같은 규칙을 다시 추론하지 않게 합니다.

---

## 절차 (6-Gate)

0. **Scope and Evidence** — diff와 기존 문서 확인
1. **Decision Extraction** — 재사용 결정과 로컬 디테일 분리
2. **Documentation Target Selection** — 가장 좁고 오래가는 source of truth 선택
3. **Minimal Documentation Update** — 짧고 범위가 명확한 규칙 기록
4. **Consistency Check** — 문서가 구현과 일치하는지 검증
5. **Handoff Summary** — 기록/제외/불확실 항목 보고

---

## 구조

- [SKILL.md](SKILL.md) — 메인 스킬
