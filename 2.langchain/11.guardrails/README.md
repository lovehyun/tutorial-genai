# 가드레일 (Guardrails)

LLM 앱이 **위험하거나 의도치 않은 입출력**을 막는 기법 모음입니다. 에이전트 전용이 아니라
챗봇·RAG·체인 등 어디에나 적용되는 주제라 `8.agents`가 아닌 별도 폴더로 뒀습니다.

각 기법은 **`a`(뚫리는 버전) / `b`(막는 버전)** 쌍으로 되어 있습니다. 똑같은 공격 입력을
두 파일에 나란히 넣어봐서, 가드레일이 없을 때 정확히 무슨 일이 생기고 어떤 기법으로 그걸
막았는지를 결과로 직접 비교할 수 있습니다.

> 모든 쌍을 OpenAI·Ollama 두 모델로 실제 실행해서 결과를 남겨뒀습니다 → [`TEST_EVIDENCE.md`](TEST_EVIDENCE.md)

## 학습 순서

| 쌍 | 막는 것 | `a` (뚫림) | `b` (막음) |
|----|---------|-----------|-----------|
| 1 | 금칙어·길이초과·뻔한 인젝션 문구 | 검사 없이 그대로 통과 | 정규식/키워드 필터 (LLM 미사용, 무료·즉시) |
| 2 | 프롬프트 인젝션 (시스템 프롬프트 유출) | 지침+입력을 한 문자열로 이어붙임, 숨기라는 지시 없음 | system/human 역할 분리 + 명시적 비노출 지시 + `<user_input>` 태그 격리 |
| 3 | 모델이 스스로 만든 부적절한 답변 | 생성된 답을 검사 없이 노출 | 별도 LLM으로 재심사 후 노출 (2-call 분리 게이트) |
| 4 | 스코프 밖 질문 | 스코프 강제 장치 없음 | 프롬프트 유도 + LLM 분류기 사후 검증 |
| 5 | 위 전부 | — | `1b`~`4b`를 하나의 파이프라인으로 조합 (Defense in Depth) |
| 6 | Text-to-SQL 인젝션 (실제 DB 데이터 유출) | 스키마 전체 노출 + 생성된 SQL을 검증 없이 실행 | 프롬프트 제한 + 실행 전 테이블 화이트리스트 검증 |

각 쌍은 **완전히 같은 공격 입력**을 사용합니다 — `a`를 먼저 실행해서 뚫리는 걸 직접 보고,
곧바로 `b`를 실행해서 같은 입력이 막히는 걸 비교하세요.

```bash
python 1a.input_no_filter.py            # 뚫림
python 1b.input_with_filter.py          # 막음 — 결과 비교

python 2a.prompt_injection_vulnerable.py
python 2b.prompt_injection_defended.py

python 3a.output_unmoderated.py
python 3b.output_moderated.py

python 4a.topic_unscoped.py
python 4b.topic_scoped.py

python 5.layered_guardrail_pipeline.py  # 1b~4b를 종합한 실전 파이프라인

python 6a.sql_query_injection_vulnerable.py
python 6b.sql_query_guarded.py
```

## 모델 선택 — OpenAI ↔ Ollama(로컬)

2~4, 6번 쌍(`1a`/`1b`는 LLM을 안 씀)은 실행 파일 상단에서 `GUARDRAIL_PROVIDER` 환경변수로
모델을 고를 수 있습니다. **강하게 정렬된 모델(OpenAI)일수록 "뚫리는 버전"조차 스스로 방어해버려서
취약점이 잘 재현되지 않을 수 있습니다** — 이럴 때 정렬이 상대적으로 약한 로컬 모델로 바꿔보면
훨씬 안정적으로 재현됩니다. 실제로 이 저장소에서 그렇게 재현했습니다 → [`TEST_EVIDENCE.md`](TEST_EVIDENCE.md) 참고.

```bash
# 기본값: OpenAI (gpt-4o-mini)
python 2a.prompt_injection_vulnerable.py

# 로컬 모델로 전환
# pip install langchain-ollama
# ollama pull qwen2.5:7b   (한 번만)
export GUARDRAIL_PROVIDER=ollama          # PowerShell: $env:GUARDRAIL_PROVIDER="ollama"
export GUARDRAIL_OLLAMA_MODEL=qwen2.5:7b  # 생략하면 기본값 qwen2.5:7b 사용
python 2a.prompt_injection_vulnerable.py
```

## 왜 여러 층을 겹치나

한 가지 방법으로는 다 못 막습니다. 정규식은 빠르지만 변형에 약하고, LLM 판정은 견고하지만 느리고 비쌉니다.
그래서 **싸고 확실한 것부터** 앞에 두고, 뒤로 갈수록 정교하지만 비용이 드는 층을 배치합니다.

```
입력 → [1층 규칙 필터] → [2층 인젝션 방어] → [3층 스코프 체크] → 답변 생성 → [4층 출력 검증] → 사용자
        (무료·즉시)        (프롬프트 설계)       (LLM 호출)                    (LLM 호출)
```

## 이 저장소 안의 다른 가드레일 관련 예제

가드레일은 이 저장소 여러 곳에서 다른 각도로 다룹니다 — 이 폴더가 "기법의 카탈로그(+ a/b 비교)"라면,
아래는 각각 특정 맥락에 특화된 구현입니다.

| 위치 | 무엇이 다른가 |
|------|---------------|
| [`../8.agents/12.middleware/12.2_pii_guardrail.py`](../8.agents/12.middleware/12.2_pii_guardrail.py) | `create_agent`의 `PIIMiddleware`로 이메일·카드번호 등 **PII를 자동 마스킹**하는 LangChain 1.x 공식 메커니즘 |
| [`../../1.openai/10.moderation_content_safety/`](../../1.openai/10.moderation_content_safety/) | OpenAI **Moderation API**(무료)로 정책 위반 여부를 검사 — 1-call vs 2-call 트레이드오프 비교표가 자세함 |
| [`../../5.mcp/4.langchain/7.guardrails/`](../../5.mcp/4.langchain/7.guardrails/) | **MCP 도구 호출**에 특화된 가드레일 — 악의적인 MCP 서버(`evil_server.py`)로부터 방어하는 시나리오 |

## 설치 및 실행

```bash
pip install langchain langchain-openai python-dotenv pydantic
pip install langchain-ollama   # GUARDRAIL_PROVIDER=ollama 로 로컬 모델을 쓸 때만 필요
```

API 키는 `2.langchain/.env`에 설정합니다: `OPENAI_API_KEY=sk-...`

## 한계

여기 나온 방어는 **완벽하지 않습니다.** 프롬프트 기반 방어는 충분히 정교한 공격 앞에서 뚫릴 수 있고,
LLM 판정기(3·4단계)도 스스로 오판할 수 있습니다. 정말 민감한 작업(결제, 권한 변경 등)은
가드레일에만 의존하지 말고 **애초에 모델이 그 권한/정보에 접근하지 못하도록 설계**하는 것이 근본적인 방어입니다.
