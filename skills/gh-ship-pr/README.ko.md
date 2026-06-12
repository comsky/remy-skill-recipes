# GH Ship PR (Push, PR 정식 등록, 리뷰 처리, 머지)

이미 커밋된 Git 브랜치를 GitHub PR 흐름으로 출고합니다. 현재 브랜치를 push하고,
PR을 생성하거나 draft PR을 ready 상태로 전환한 뒤, 선택에 따라 CI 완료를
기다리고 리뷰 코멘트를 자동 처리하며, 명시적인 안전 게이트를 통과한 경우에만
머지합니다.

이 스킬은:

- push 또는 PR 작업 전에 브랜치와 워크트리 목적을 확인
- 보호/공유 브랜치가 아닌 현재 브랜치만 push
- ready PR을 생성하거나 기존 draft PR을 리뷰 가능 상태로 전환
- 머지 전 CI 완료를 기다릴지 사용자에게 확인
- actionable 리뷰 코멘트를 자동 처리할지 사용자에게 확인
- 머지 전 PR 상태, 체크 상태, 리뷰 상태, head commit을 다시 확인
- 머지와 cleanup 작업에 대해 명시적인 결정을 요구

---

## 왜 필요한가

혼자 작업할 때도 PR 출고 과정은 같은 위험한 순서를 반복합니다. push, PR 생성
또는 ready 전환, 체크 대기, 리뷰 피드백 처리, 수정 커밋 push, 머지까지의
절차를 명시적으로 고정해 두면 에이전트가 CI를 건너뛰거나 draft PR을 머지하거나,
unresolved review thread를 놓치거나, 잘못된 브랜치에서 push하거나, 허락 없이
브랜치/워크트리를 삭제하는 일을 줄일 수 있습니다.

---

## 절차 (10-Gate)

- **Gate -1: Branch Intent Check** — 현재 브랜치/워크트리가 작업 목적과 맞는지 확인
0. **Tool and Remote Check** — GitHub remote, 인증, repo, PR 상태 확인
1. **Ask User Options** — CI 대기, 리뷰 처리, 머지, cleanup 방식 선택
2. **Push Branch** — 현재 브랜치를 push하고 remote head 확인
3. **Create or Ready the PR** — ready PR 생성 또는 draft PR을 ready로 전환
4. **CI Handling** — 체크 대기, 실패 진단/수정, pending 상태 기록
5. **Review Comment Handling** — unresolved thread 분류 및 actionable 항목 처리
6. **Merge Readiness Check** — PR 상태, 체크, 리뷰 결정, head commit 재확인
7. **Merge** — 선택한 merge strategy와 안전 플래그로 머지
8. **Post-Merge Cleanup** — 선택한 cleanup 작업 기록 또는 수행

---

## 구조

- [SKILL.md](SKILL.md) — 메인 스킬

