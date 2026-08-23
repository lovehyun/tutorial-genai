# 6.structured_output — 구조화 출력

모델의 출력을 '자유 텍스트'에서 **코드가 신뢰하고 파싱할 수 있는 구조**로 바꿉니다.
가장 단순한 방법(프롬프트로 부탁하기)에서 시작해, 한 단계씩 신뢰도를 높여갑니다.

## 왜 필요한가

지금까지 모델의 답변은 자유 형식 텍스트였습니다. 사람이 읽기엔 좋지만,
코드가 그 답을 받아 처리하려면(DB 저장·API 호출·UI 표시) 형식이 불안정해 곤란합니다.
→ 출력을 JSON 같은 정해진 구조로 받으면 LLM을 **프로그램 부품처럼** 쓸 수 있습니다.

## 학습 순서

| 파일 | 이 단계에서 새로 배우는 것 |
|------|---------------------------|
| `1.json_prompt.py` | 프롬프트로 JSON 부탁 — 동작하지만 불안정함을 확인 |
| `2.json_mode.py` | `response_format=json_object` — 올바른 JSON임을 API가 보장 |
| `3.json_schema.py` | `json_schema` strict — 필드·타입까지 100% 강제 |
| `4.pydantic_parse.py` | Pydantic 클래스 + `parse()` — 스키마를 간결하게 (실무 표준) |

각 단계는 직전 단계의 '한계'를 해결하며 이어집니다. 헤더 주석의
"이 단계 문제 / 해결"을 따라 읽으면 *왜* 다음 단계가 필요한지 보입니다.

## 다음 단계

구조화 출력으로 **행동**까지 시키려면(모델이 "이 함수를 이 인자로 불러라"라고 판단하게 하기) →
[`../7.function_calling/`](../7.function_calling/). Function Calling은 사실
"구조화 출력을 *행동*에 적용한 특수 케이스"입니다 — 모델이 내놓는 게 `{함수이름, 인자}` JSON이고
같은 json_schema/pydantic 기계를 씁니다.

## 설치 및 실행

```bash
pip install openai pydantic python-dotenv
python 1.json_prompt.py   # 1단계부터 순서대로
```

API 키는 상위 폴더의 `.env`(`../.env`)에 설정합니다: `OPENAI_API_KEY=sk-...`
