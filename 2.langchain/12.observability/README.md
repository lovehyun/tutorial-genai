# 관찰가능성 (Observability)

지금까지의 예제들은 잘 동작하는지 `print()`로만 확인했습니다. 실전에서는 "왜 느린가",
"토큰을 얼마나 썼는가", "프롬프트가 실제로 어떻게 만들어졌는가"를 매번 코드에 print를
심지 않고도 봐야 합니다 — 그게 이 폴더의 주제입니다.

`8.agents/11.evaluation`이 "결과가 정확한가?"를 자동 검증한다면, 이 폴더는
"운영 중 무엇이 느리고 왜 그런 결과가 나왔는지 눈으로 보기"라 성격이 다릅니다.

## 학습 순서

| 파일 | 내용 | 필요한 것 |
|------|------|-----------|
| `1.tracing_setup.py` | 환경변수 3줄로 기존 체인을 자동 트레이싱 | LangSmith 무료 계정 |
| `2.run_metadata_and_custom_traceable.py` | 트레이스에 이름표(run_name/tags/metadata) 붙이기 + `@traceable`로 내 함수도 추적 | LangSmith 무료 계정 |
| `3.local_callback_handler.py` | LangSmith 없이 콜백으로 로컬에서 지연시간·토큰 확인 | **없음** (바로 실행 가능) |

## LangSmith — 무료로 충분한가

[Developer 플랜](https://smith.langchain.com)은 **월 5,000 트레이스, 1인 사용, 14일 데이터 보관**입니다.
개인 학습·프로토타이핑에는 충분하고, 이 저장소의 실습 목적에도 딱 맞습니다. 가입 없이 먼저
`3.local_callback_handler.py`부터 해봐도 됩니다 — 이 파일은 LangSmith와 무관하게 동작합니다.

## 가입 및 설정

1. https://smith.langchain.com 무료 가입
2. API 키 발급 (Settings → API Keys)
3. `2.langchain/.env`에 추가:
   ```
   LANGSMITH_TRACING=true
   LANGSMITH_API_KEY=lsv2_...
   LANGSMITH_PROJECT=tutorial-genai-observability
   ```
4. `1.tracing_setup.py` 실행 후 대시보드에서 트레이스 확인

## 설치 및 실행

```bash
pip install langsmith langchain langchain-openai python-dotenv
python 1.tracing_setup.py
```

## 관련 폴더

- [`../8.agents/11.evaluation/`](../8.agents/11.evaluation/) — "얼마나 정확한가"를 자동 검증 (이 폴더는 "왜 그런 결과가 나왔나"를 들여다봄)
- [`../8.agents/12.middleware/`](../8.agents/12.middleware/) — 미들웨어도 `before_model`/`after_model` 훅으로 로깅에 쓸 수 있음(콜백과 유사한 개념)
