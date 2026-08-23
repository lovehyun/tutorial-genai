# MCP 유연 포맷 커리큘럼 (시간 포맷별 모듈 조합)

## 과정 정보
- **기간**: 유연 — 4시간 / 8시간(원데이) / 16시간(2일), 3개 포맷 중 상황에 맞게 선택
- **난이도**: 입문~중급
- **대상**: 강사가 청중·가용 시간에 맞춰 포맷을 고르는 용도. 파일명까지 못박은 정식 3일 심화 과정은 [`3.advanced/1.mcp_protocol_deep_dive`](../../3.advanced/1.mcp_protocol_deep_dive/) 참고
- **선수 과목**: LLM tool-calling/에이전트 개념을 한 번은 접해본 사람(복습으로 다시 훑는다). 완전 초심자면 [`2.intermediate/2.agent_development`](../../2.intermediate/2.agent_development/) 선행 권장

같은 교재([`5.mcp/`](../../../5.mcp/))로 **수업 길이·일수**에 맞춰 짜는 커리큘럼 모음.
**모듈(레고 블록)** 을 먼저 정의하고, **시간 포맷**(4H / 8H / 16H×2day)별로 조합한다.

## 구성 파일

| 파일 | 내용 |
|---|---|
| [`0.base.md`](0.base.md) | 모듈 카탈로그(M0~M20) · 주제별 강조 트랙 · 공통 준비물 — 모든 포맷이 공유하는 베이스 |
| [`1.mcp_practice_4hr.md`](1.mcp_practice_4hr.md) | **포맷 1 — 4시간**, 예제 중심(llm-math→MCP stdio→로컬/원격 연동→라우팅/분기→HITL) + 보너스 |
| [`2.mcp_practice_8hr.md`](2.mcp_practice_8hr.md) | **포맷 2 — 8시간(원데이 집중)** |
| [`3.mcp_practice_16hr.md`](3.mcp_practice_16hr.md) | **포맷 3 — 16시간(2일 집중 부트캠프)** |

> 새 포맷을 추가하려면 이 폴더에 `N.mcp_practice_XXhr.md` 로 파일만 늘리고, 이 표와
> [`0.base.md`](0.base.md)의 모듈 카탈로그에서 필요한 모듈을 가져다 쓰면 된다.

## 실습 코드

[`exercise/`](exercise/) — 4대 섹션에 맞춰 `1a,1b,1d / 2a~2d / 3a~3d / 4a,4b` 로 이름 붙인 핸즈온을
`1.instructor`(강사용 완성 코드, 실행 결과 첨부됨) · `2.student(todo)`(빈칸) · `3.student(answer)`(TODO 자리를 DONE으로 채운 정답)
3벌로 정리해뒀다. `1.instructor/`에는 `1cx`·`1ex`·`2bx`·`4cx`·`4dx` 다섯 개의 강사 전용 보너스도
있다(create_agent 내부 구조 손으로 재현, 도구 선택 애매성 실측, MCP JSON-RPC 프록시 관찰, HITL
자동승인, HITL 웹 버전) — 시간이 남을 때만 보여주는 용도라 student 폴더엔 없다. 상세는
[`exercise/README.md`](exercise/README.md) 참고.

## PDF

[`1.mcp_practice_4hr.pdf`](1.mcp_practice_4hr.pdf) — 4시간 포맷을 인쇄/배포용으로 내보낸 PDF
(`.md` 원본이 최신 소스이며, PDF는 그 스냅샷. 저장소에는 커밋되지 않음 — 루트 `.gitignore`의 `*.pdf` 규칙 적용).
