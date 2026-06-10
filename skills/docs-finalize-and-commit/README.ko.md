# Finalize Documentation and Commit (문서 최종 정리 및 커밋)

문서 변경사항을 프로덕션 수준으로 최종 정리합니다.
기존 컨벤션 탐색, 코드-문서 정합성 검증, 브랜치/워크트리 목적 검증,
깔끔한 커밋 구조화를 수행합니다.
모든 문서 프레임워크(Docusaurus, VitePress, MkDocs, Nextra, 순수 Markdown 등)에서 사용 가능합니다.

이 스킬은:

- 기존 문서를 샘플링하여 컨벤션을 탐색 (톤, 용어, 구조)
- 소스 코드가 함께 변경된 경우 코드-문서 정합성을 검증
- 형식, 용어, 톤, 완결성의 일관성을 검토
- 프레임워크별 문법 및 빌드 무결성을 검증
- 스테이징/커밋 전 브랜치와 워크트리 목적 일치 여부 점검
- 변경 유형별 커밋 구조화: `docs(fix)`, `docs(style)`, `docs(content)`, `docs(sync)`

---

## 왜 필요한가

컨벤션 탐색을 건너뛰면 문서 품질이 저하됩니다.
일관성 없는 용어, 깨진 링크, 코드와 맞지 않는 참조는
사용자 신뢰를 떨어뜨립니다. 이 스킬은 외부에서 강제하는 것이 아닌
기존 문서 코퍼스에서 추론한 기준으로 모든 문서 커밋의 품질을 보장합니다.
동시에 오래된 브랜치나 이전 세션의 worktree 변경이 섞이지 않게 합니다.

---

## 절차 (8-Gate)

- **Gate -1: Branch Context Check** — 현재 브랜치/워크트리가 작업 목적과 맞는지 확인
0. **Working Set Validation** — 세션 변경 격리, 범위 외 파일 보호
1. **Convention Discovery** — 기존 문서 10~15개 샘플링하여 스타일, 톤, 용어 추론
2. **Code-Documentation Alignment** — 소스 코드 변경을 문서 참조에 매핑
3. **Documentation Quality Review** — 구조, 용어, 톤, 완결성, 문법, 이미지, 링크, 사이드바
4. **Auto-Fix** — 판단 불필요 항목 자동 수정, 판단 필요 항목 제시
5. **Build Verification** — 문서 빌드 실행 및 결과 확인
6. **Commit Structuring** — 변경 유형별 Conventional Commits 형식 커밋 분리

---

## 구조

- [SKILL.md](SKILL.md) — 메인 스킬
