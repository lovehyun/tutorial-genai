# 7.function_calling — Function Calling

모델이 구조화된 출력으로 **함수를 호출**하게 만듭니다. [`../6.structured_output/`](../6.structured_output/)에서
익힌 "출력의 모양 고정하기"를 "그 모양으로 행동하기"에 적용한 것입니다.

> **구조화 출력과의 관계**: Function Calling은 사실 "구조화 출력을 *행동*에 적용한 특수 케이스"입니다 —
> 모델이 내놓는 게 `{함수이름, 인자}` JSON이고, 구조화 출력과 같은 json_schema/pydantic 기계를 씁니다.

## 학습 순서

| 파일 | 이 단계에서 새로 배우는 것 |
|------|---------------------------|
| `1.func_calling_basic.py` | 모델이 '어떤 함수를 어떤 인자로' 호출할지 판단 |
| `2.func_calling_basic_test.py` | 1을 여러 입력으로 확인(테스트/변형) |
| `3.func_calling_loop.py` | 함수 실행 → 결과 반영 → 최종 답변까지 전체 왕복 |

각 단계는 직전 단계의 '한계'를 해결하며 이어집니다.

## 여기서 배운 함수 호출, 그다음은

- **Function Calling은 에이전트(agent)의 토대**입니다 → `2.langchain/8.agents`로 이어집니다.
- 여기서는 함수를 **내가 직접** 정의하고 실행합니다. OpenAI가 서버에서 대신 실행해주는
  내장 도구(예: 웹 검색)는 [`../2.sdk/9.response_web_search.py`](../2.sdk/9.response_web_search.py) 참고.
- 표준 프로토콜(MCP)로 도구를 빼내 재사용하는 건 → `5.mcp/`

## 설치 및 실행

```bash
pip install openai pydantic python-dotenv
python 1.func_calling_basic.py   # 1단계부터 순서대로
```

API 키는 상위 폴더의 `.env`(`../.env`)에 설정합니다: `OPENAI_API_KEY=sk-...`
