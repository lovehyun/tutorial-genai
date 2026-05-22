# OpenAI 구조화 출력 (Structured Output)

모델의 출력을 '자유 텍스트'에서 **코드가 신뢰하고 파싱할 수 있는 구조**로 바꿉니다.
가장 단순한 방법에서 시작해 한 단계에 개념 하나씩 더해갑니다.

## 왜 필요한가

1~8단계까지 모델의 답변은 자유 형식 텍스트였습니다. 사람이 읽기엔 좋지만,
코드가 그 답을 받아 처리하려면(DB 저장·API 호출·UI 표시) 형식이 불안정해 곤란합니다.
→ 출력을 JSON 같은 정해진 구조로 받으면 LLM을 **프로그램 부품처럼** 쓸 수 있습니다.

## 학습 순서

### 1부. 출력의 '모양' 고정하기
| 파일 | 이 단계에서 새로 배우는 것 |
|------|---------------------------|
| `1.json_prompt.py` | 프롬프트로 JSON 부탁 — 동작하지만 불안정함을 확인 |
| `2.json_mode.py` | `response_format=json_object` — 올바른 JSON임을 API가 보장 |
| `3.json_schema.py` | `json_schema` strict — 필드·타입까지 100% 강제 |
| `4.pydantic_parse.py` | Pydantic 클래스 + `parse()` — 스키마를 간결하게 (실무 표준) |

### 2부. 출력으로 '행동' 시키기 (Function Calling)
| 파일 | 이 단계에서 새로 배우는 것 |
|------|---------------------------|
| `5.function_calling_basic.py` | 모델이 '어떤 함수를 어떤 인자로' 호출할지 판단 |
| `6.function_calling_loop.py` | 함수 실행 → 결과 반영 → 최종 답변까지 전체 왕복 |

각 단계는 직전 단계의 '한계'를 해결하며 이어집니다. 헤더 주석의
"이 단계 문제 / 해결"을 따라 읽으면 *왜* 다음 단계가 필요한지 보입니다.

## 두 가지 큰 개념

- **Structured Output** (1~4) = 출력의 *모양*을 고정한다 — "반드시 이 JSON 구조로"
- **Function Calling** (5~6) = 출력으로 *행동*을 시킨다 — "이 함수를 이 인자로 불러라"
  - Function Calling은 에이전트(agent)의 토대이며, `2.langchain/7.agents`로 이어집니다.

## 설치 및 실행

```bash
pip install openai pydantic python-dotenv
python 1.json_prompt.py   # 1단계부터 순서대로
```

API 키는 상위 폴더의 `.env`(`../.env`)에 설정합니다: `OPENAI_API_KEY=sk-...`
