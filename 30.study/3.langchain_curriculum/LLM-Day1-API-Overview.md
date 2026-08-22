# LLM 1일차: API 개요 (Python & LangChain 기준)

## 학습 목표
- LLM(특히 GPT-4o/4o-mini) API 호출의 전체 흐름을 이해합니다.
- 안전한 비밀키 관리(.env)와 요청/응답 구조, 토큰/비용/속도 최적화를 이해합니다.
- Python 순정(OpenAI SDK)과 LangChain 래퍼를 모두 사용해 간단한 예제를 완성합니다.
- 스트리밍, 함수호출(툴콜), 구조적 출력(파싱) 기본기를 익힙니다.

---

## 준비물
- Python 3.9+
- 가상환경(venv/uv/conda 등)
- OpenAI API Key (환경변수 `OPENAI_API_KEY` 설정)
- 에디터(추천: VSCode)

### 필수 설치
```bash
pip install --upgrade pip
pip install python-dotenv langchain langchain-openai tiktoken
```

> 선택: 구조화 파싱에 `pydantic` 활용  
```bash
pip install pydantic
```

### .env 예시
```
OPENAI_API_KEY=sk-...yourkey...
```

### 기본 디렉터리
```
project/
 ├─ .env
 └─ main.py
```

---

## 핵심 개념 요약
- **모델**: `gpt-4o`(고성능), `gpt-4o-mini`(저비용/빠름)
- **프롬프트**: 시스템/사용자 지시 → 모델 유도
- **토큰**: 입력+출력 단위. 길이 제한(컨텍스트 윈도) 존재
- **스트리밍**: 토큰 단위로 실시간 수신
- **함수 호출(툴콜)**: 모델이 스스로 도구 호출을 제안 → 코드 실행 → 결과 재주입
- **구조적 출력**: JSON/스키마로 파싱하기 쉽게 받기

---

## OpenAI SDK (순정) 최소 예제

> 안정성을 위해 **예외 처리**와 **재시도**(지수 백오프)를 권장합니다.

```python
# main.py
import os, time, json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"  # 비용/속도 우선
SYSTEM = "당신은 간결하고 정확한 한국어 비서입니다."

def ask(prompt: str) -> str:
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role":"system","content":SYSTEM},
                    {"role":"user","content":prompt}
                ],
                temperature=0.3,
            )
            return resp.choices[0].message.content
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

if __name__ == "__main__":
    print(ask("LangChain의 핵심 구성요소를 5줄로 요약해 주세요."))
```

### 스트리밍 수신 예제
```python
from openai import OpenAI
client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role":"user","content":"딸기잼 만드는 법을 간단 레시피로."}],
    stream=True,
)

for chunk in stream:
    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

---

## LangChain 기본 호출
LangChain은 **LLM 드라이버 + 프롬프트 + 파서**를 체이닝하는 표준 인터페이스를 제공합니다.

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 전문 요리사입니다. 모든 답은 한국어로."),
    ("user", "{question}")
])
chain = prompt | llm | StrOutputParser()

print(chain.invoke({"question":"라자냐 레시피 핵심만 정리"}))
```

### 구조화 출력(파싱) — Pydantic
```python
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

class Recipe(BaseModel):
    title: str
    servings: int = Field(..., ge=1)
    ingredients: list[str]
    steps: list[str]

parser = PydanticOutputParser(pydantic_object=Recipe)

format_instructions = parser.get_format_instructions()
sys_msg = "당신은 JSON 스키마를 엄격히 따르는 요리 비서입니다."

prompt = ChatPromptTemplate.from_messages([
    ("system", sys_msg),
    ("user", "다음 형식을 반드시 따르세요:
{format}
요청: {topic}")
]).partial(format=format_instructions)

chain = prompt | llm | parser
data = chain.invoke({"topic":"김치볶음밥 2인분"})
print(data.model_dump())
```

---

## 함수 호출(툴콜) 개념 맛보기
모델이 **호출 파라미터**를 제안 → 애플리케이션이 해당 함수를 실행 → 결과를 모델에 재주입

**프로토타입**
```python
# 툴 시그니처
def get_weather(city: str, unit: str="c"):
    ...

# 모델 메시지 → 도구 호출 제안(JSON)
# {"tool_call": {"name":"get_weather", "arguments":{"city":"Seoul","unit":"c"}}}
```

> Day 6에서 LangChain 도구/에이전트와 함께 심화 실습합니다.

---

## 토큰/비용/속도 최적화 체크리스트
- `gpt-4o-mini` 우선 검토, 품질 필요 시 `gpt-4o`
- 프롬프트 최소화(시스템 지시 템플릿화), 불필요한 예시 제거
- 스트리밍으로 TTFB 단축, 클라이언트 UX 개선
- 캐시/요약으로 히스토리 압축, 중요 메타데이터만 유지
- 재시도/타임아웃 기본 설정

---

## 실습 과제
1) `ask()` 함수에 **타임아웃, 지수 백오프**를 추가하고 로깅해 보세요.  
2) 구조화 출력으로 **뉴스 요약** 스키마를 정의하고, `PydanticOutputParser`로 파싱하세요.  
3) 하나의 스크립트에서 **순정 SDK vs LangChain** 결과/속도를 간단 비교하세요.

---

## 트러블슈팅
- `401 Unauthorized`: API Key/환경변수 확인(.env, shell export)
- `RateLimitError`: 재시도/큐잉/속도 제한, 모델 변경(gpt-4o-mini)
- `UnicodeEncodeError`: 콘솔 인코딩/파일 저장 시 `encoding="utf-8"`
