# 응용 태스크 (Applied Tasks)

`2.prompts` 와 `4.chaining` 에서 배운 도구를 **실제 작업**에 적용한 예제 모음.
각 파일은 독립적으로 실행 가능한 미니 앱입니다.

## 폴더 구조

```
6.tasks/
├── 0.legacy(instruct)/      ← 옛 PromptTemplate / Instruct 버전 (비교용)
├── 1.summarization_chat.py  ← 텍스트 요약
├── 2.translation_chat.py    ← 번역
├── 3.emailgeneration_chat.py← 이메일 생성
├── 4.sqlgeneration_chat.py  ← SQL 생성
└── README.md
```

## 파일별 요약

| # | 파일 | 작업 | 핵심 패턴 |
|---|------|------|---------|
| 1 | `1.summarization_chat.py` | 긴 텍스트 요약 | system prompt 로 요약 길이/스타일 강제, 한 줄/세 줄 등 형식 지정 |
| 2 | `2.translation_chat.py` | 한↔영 번역 | 원본 언어 / 대상 언어 변수화, 톤 조절 |
| 3 | `3.emailgeneration_chat.py` | 비즈니스 이메일 작성 | 톤/맥락/수신자 정보를 변수로 받기, 전문성·친근함 강제 |
| 4 | `4.sqlgeneration_chat.py` | 자연어 → SQL | DB 스키마를 prompt 에 끼워 자연어 질문을 SQL 로 변환 |

> 모든 파일은 `ChatOpenAI(model="gpt-4o-mini")` + LCEL 파이프(`|`) 패턴을 사용합니다.

## 학습 방법

각 파일은 **독립 예제**라 순서대로 학습할 필요가 없습니다. 관심 있는 작업부터 보세요.

같은 번호의 **legacy 파일과 나란히 비교**해보면:
- `PromptTemplate` (legacy) ↔ `ChatPromptTemplate` (chat) 차이
- `OpenAI` + `gpt-3.5-turbo-instruct` ↔ `ChatOpenAI` + `gpt-4o-mini` 차이
- 단일 문자열 prompt ↔ system/user 메시지 분리 차이

## `0.legacy(instruct)/` — 옛 버전 (비교 학습용)

| 파일 | 짝지 |
|------|------|
| `1.summarization_instruct.py` | ↔ `1.summarization_chat.py` |
| `2.translation_instruct.py` | ↔ `2.translation_chat.py` |
| `3.emailgeneration_instruct.py` | ↔ `3.emailgeneration_chat.py` |
| `4.sqlgeneration_instruct.py` | ↔ `4.sqlgeneration_chat.py` |

> 새 프로젝트는 chat 버전만 따라가면 충분합니다. legacy 는 "옛날엔 이렇게 했다" 정도 참고.

## 확장 아이디어

- **요약**: 청크 분할 후 map-reduce 식 (긴 문서용) → `8.RAG` 와 연결
- **번역**: 다국어 → 다국어 (`RunnableBranch` 로 언어별 분기)
- **이메일**: 출력 형식 정형화 (`3.structured_output/PydanticOutputParser`) → 제목/본문 필드 분리
- **SQL**: 생성된 SQL 을 실제로 실행 (`9.agents/` 의 tool 패턴)

## 관련 폴더

- [`../2.prompts/`](../2.prompts/) — 사용된 ChatPromptTemplate 기본기
- [`../4.chaining/`](../4.chaining/) — 사용된 LCEL 체이닝 패턴
- [`../3.structured_output/`](../3.structured_output/) — 결과를 구조화하고 싶을 때

## 실행

```bash
pip install langchain langchain-openai python-dotenv

python "1.summarization_chat.py"
python "0.legacy(instruct)/1.summarization_instruct.py"   # legacy 비교용
```
