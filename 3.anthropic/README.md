# Anthropic Claude API 예제

Claude API를 활용한 예제를 기초부터 단계별로 학습합니다. 각 폴더는 **하나의 주제**를 다룹니다
(1.openai, 2.langchain과 같은 조직 원리).

## 학습 순서

`1.basic` 이후로는 서로 독립적입니다. 번호는 **"실전 앱에서 쓰일 확률"** 순서입니다 — 도구
호출·구조화 출력·에러 처리는 프로덕션 앱이라면 거의 항상 필요하지만, 멀티모달·배치·Files API는
그 앱의 성격에 따라 필요 없을 수도 있는 선택적 기능이라 뒤로 뺐습니다.

| 디렉토리 | 주제 | 설명 |
|----------|------|------|
| `1.basic/` | API 기초 | 첫 호출 → system → 멀티턴 → 스트리밍 → 파라미터 → 모델 비교 → thinking → 응답 객체 |
| `2.tools/` | 도구 호출 | 클라이언트 도구(직접 실행) + 서버 도구(웹검색·코드실행, Anthropic이 실행) — 에이전트의 토대 |
| `3.structured_output/` | 구조화 출력 | `messages.parse()` + Pydantic — 거의 모든 실전 연동에 필요 |
| `4.error_handling/` | 에러 처리 | 타입별 예외 + 자동 재시도 — 프로덕션 코드의 필수 조건 |
| `5.prompt_caching/` | 프롬프트 캐싱 | 반복 호출 비용 최대 ~90% 절감 — 규모가 커지면 사실상 필수 |
| `6.multimodal/` | 이미지·문서 입력 | 비전, PDF, Citations(출처 자동 인용) — 필요한 앱만(Anthropic은 이미지 *생성*은 미지원, 입력만) |
| `7.effort/` | effort 파라미터 | 생각 깊이/비용 조절 (Opus·Sonnet 4.6 전용) — 선택적 튜닝 |
| `8.batches/` | Batches API | 대량 비동기 처리, 50% 할인 — 특정 용도(오프라인 대량 처리)에만 필요 |
| `9.files_api/` | Files API | 업로드 후 `file_id` 재사용 — 특정 용도(같은 문서 반복 질의)에만 필요 |
| `10.langchain/` | LangChain 연동 | `ChatAnthropic`으로 프롬프트/메모리/RAG/체인 |
| `11.agent_sdk/` | Claude Agent SDK | Claude Code와 같은 에이전트 루프를 코드로 — 별도 준비 필요(아래 참고) |

> `2.tools`~`9.files_api`는 원래 `2.intermediate`/`3.advanced`라는 두 개의 "난이도별" 폴더에
> 무관한 주제 여러 개가 섞여 있던 것을 각각 독립 폴더로 분리한 것입니다.
> `11.agent_sdk`는 성격이 아예 달라서(가벼운 API 호출이 아니라 에이전트 하나를 통째로 띄움,
> 비용도 다름) 맨 뒤에 뒀습니다 — 자세한 건 [`11.agent_sdk/README.md`](11.agent_sdk/README.md) 참고.

## 사전 준비

```bash
pip install anthropic python-dotenv
```

`.env` 파일에 Anthropic API 키를 설정하세요:
```
ANTHROPIC_API_KEY=sk-ant-...
```

## 모델 선택 (2026 기준)

Haiku 4.5 / Sonnet 4.6 / Opus 4.8 세 모델을 용도에 맞게 씁니다 — 파라미터 지원 여부가 모델마다
달라서(`temperature`, adaptive thinking, effort 등) 헷갈리기 쉽습니다. 정리된 비교표는
[`1.basic/README.md`](1.basic/README.md#모델별-규격-차이-꼭-기억) 참고.

## 다른 벤더와 비교

같은 개념을 벤더마다 어떻게 구현했는지 비교하면 이해가 빠릅니다:

| 개념 | OpenAI | LangChain | Anthropic |
|------|--------|-----------|-----------|
| 구조화 출력 | `1.openai/6.structured_output/` | `2.langchain/3.structured_output/` | `3.structured_output/` |
| 웹 검색(내장 도구) | `1.openai/2.sdk/13.response_web_search.py` | `2.langchain/8.agents/1.builtin_tools/` | `2.tools/3.web_search.py` |
| 배치 처리 | `1.openai/11.batch/` | — | `8.batches/` |
| 가드레일 | `1.openai/10.moderation_content_safety/` | `2.langchain/11.guardrails/` | (해당 없음 — LangChain 폴더 참고) |
