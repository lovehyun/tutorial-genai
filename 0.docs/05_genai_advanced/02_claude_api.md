# Claude API (Anthropic SDK)

> OpenAI와는 다른 철학으로 설계된 Claude API — Messages API 구조, tool_use, Extended Thinking까지 Anthropic SDK의 핵심 기능을 실습하며 익힙니다

---

## 1. Anthropic SDK 설치와 클라이언트 초기화

### SDK 설치

Claude API를 사용하려면 Anthropic 공식 Python SDK를 설치해야 합니다. `anthropic 0.40+` 버전을 기준으로 설명합니다.

```bash
# 터미널 -- Anthropic SDK 설치
pip install anthropic>=0.40
```

설치 확인은 다음과 같이 합니다.

```python
# check_version.py -- SDK 설치 확인
import anthropic
print(anthropic.__version__)
# 출력 예: 0.42.0
```

### API 키 발급과 환경변수 설정

Anthropic Console(https://console.anthropic.com)에서 API 키를 발급받습니다. 발급받은 키는 `sk-ant-api03-` 접두어로 시작합니다.

```bash
# .env -- 환경변수 파일
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxx
```

> **핵심 포인트:** API 키를 코드에 직접 하드코딩하면 안 됩니다. 반드시 환경변수나 `.env` 파일을 통해 관리하고, `.gitignore`에 `.env`를 추가하십시오.

### 클라이언트 초기화 패턴

```python
# client_init.py -- 클라이언트 초기화
import os
from anthropic import Anthropic

# 방법 1: 환경변수에서 자동으로 읽기 (ANTHROPIC_API_KEY)
client = Anthropic()

# 방법 2: 명시적으로 API 키 전달
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 방법 3: dotenv 활용
from dotenv import load_dotenv
load_dotenv()
client = Anthropic()
```

### OpenAI SDK와의 차이점 요약

| 항목 | OpenAI | Anthropic |
|------|--------|-----------|
| 패키지명 | `openai` | `anthropic` |
| 클라이언트 | `OpenAI()` | `Anthropic()` |
| 환경변수 | `OPENAI_API_KEY` | `ANTHROPIC_API_KEY` |
| 메인 메서드 | `client.chat.completions.create()` | `client.messages.create()` |
| system 메시지 | messages 배열 안에 포함 | 별도 `system` 파라미터로 분리 |
| 응답 객체 | `response.choices[0].message.content` | `response.content[0].text` |

> **핵심 포인트:** Anthropic SDK는 `client.messages.create()` 단일 엔드포인트로 대부분의 기능을 처리합니다. OpenAI처럼 `chat.completions`, `embeddings`, `images` 등으로 분산되어 있지 않아 구조가 단순합니다.

---

## 2. Messages API 구조

### 기본 요청 구조

Messages API는 Claude와 상호작용하기 위한 핵심 인터페이스입니다. 가장 기본적인 호출 형태를 살펴보겠습니다.

```python
# basic_message.py -- 기본 Messages API 호출
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5-20250514",
    max_tokens=1024,
    system="당신은 친절한 한국어 AI 비서입니다.",
    messages=[
        {"role": "user", "content": "안녕하세요, Claude! 자기소개를 해주세요."}
    ]
)

print(response.content[0].text)
```

### system 파라미터 — OpenAI와의 핵심 차이

OpenAI에서는 system 메시지를 `messages` 배열 안에 `{"role": "system", ...}` 형태로 넣습니다. 반면 Claude는 **`system` 파라미터를 별도로 분리**합니다.

```python
# system_comparison.py -- system 메시지 방식 비교

# OpenAI 방식
openai_messages = [
    {"role": "system", "content": "당신은 전문 번역가입니다."},
    {"role": "user", "content": "Hello, world!"}
]

# Anthropic 방식 — system이 messages 밖에 있음
response = client.messages.create(
    model="claude-sonnet-4-5-20250514",
    max_tokens=1024,
    system="당신은 전문 번역가입니다.",  # 별도 파라미터
    messages=[
        {"role": "user", "content": "Hello, world!"}
    ]
)
```

> **핵심 포인트:** Claude의 `system` 파라미터 분리 설계는 시스템 프롬프트가 대화의 일부가 아니라 모델의 **행동 지침**이라는 철학을 반영합니다. 이 분리 덕분에 시스템 프롬프트 캐싱도 더 효율적으로 처리됩니다.

### user/assistant 교번 규칙

Claude Messages API는 `user`와 `assistant` 역할이 **반드시 번갈아** 나와야 합니다. 같은 역할의 메시지가 연속으로 오면 에러가 발생합니다.

```python
# alternation_rule.py -- 올바른 교번 구조와 잘못된 구조

# 올바른 구조 (user → assistant → user → assistant)
valid_messages = [
    {"role": "user", "content": "파이썬이란 무엇인가요?"},
    {"role": "assistant", "content": "파이썬은 범용 프로그래밍 언어입니다."},
    {"role": "user", "content": "주요 특징은 무엇인가요?"},
]

# 잘못된 구조 — user가 연속으로 등장
invalid_messages = [
    {"role": "user", "content": "파이썬이란 무엇인가요?"},
    {"role": "user", "content": "그리고 자바와 비교해주세요."},  # 에러!
]
```

연속된 사용자 입력을 보내야 할 경우, 하나의 메시지로 합치거나 줄바꿈으로 구분해서 보냅니다.

### content 블록 구조

Claude의 요청과 응답에서 `content`는 **문자열 또는 블록 배열** 형태를 갖습니다.

| 블록 타입 | 설명 | 사용 위치 |
|-----------|------|-----------|
| `TextBlock` | 텍스트 콘텐츠 | 요청/응답 |
| `ImageBlock` | Base64 또는 URL 이미지 | 요청 |
| `ToolUseBlock` | 도구 호출 요청 | 응답 |
| `ToolResultBlock` | 도구 실행 결과 | 요청 |
| `ThinkingBlock` | 확장 사고 과정 | 응답 |

```python
# content_blocks.py -- 다양한 content 블록 구조

# 1. 문자열 단축형 (가장 간단)
simple_message = {"role": "user", "content": "안녕하세요"}

# 2. TextBlock 명시적 사용
text_block_message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "이 이미지를 설명해주세요."}
    ]
}

# 3. 이미지 + 텍스트 멀티모달 요청
import base64

with open("photo.jpg", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

multimodal_message = {
    "role": "user",
    "content": [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": image_data
            }
        },
        {"type": "text", "text": "이 사진에서 보이는 건물의 이름을 알려주세요."}
    ]
}
```

### 멀티턴 대화 예제

```python
# multi_turn.py -- 멀티턴 대화 구현
from anthropic import Anthropic

client = Anthropic()
conversation_history = []

def chat(user_message: str) -> str:
    """멀티턴 대화를 유지하며 Claude에게 메시지를 보냅니다."""
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    response = client.messages.create(
        model="claude-sonnet-4-5-20250514",
        max_tokens=2048,
        system="당신은 파이썬 튜터입니다. 초보자 눈높이에 맞춰 설명합니다.",
        messages=conversation_history
    )

    assistant_message = response.content[0].text
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message

# 대화 실행
print(chat("리스트와 튜플의 차이가 뭔가요?"))
print(chat("그러면 어떤 상황에서 튜플을 쓰는 게 좋나요?"))
print(chat("딕셔너리 키로 튜플을 쓸 수 있다고요?"))
```

### 응답 객체 구조

```python
# response_structure.py -- 응답 객체 필드 확인
response = client.messages.create(
    model="claude-sonnet-4-5-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "1+1은?"}]
)

print(f"ID: {response.id}")               # msg_01XFDUDYJgAACzvnptvVoYEL
print(f"Model: {response.model}")          # claude-sonnet-4-5-20250514
print(f"Role: {response.role}")            # assistant
print(f"Stop reason: {response.stop_reason}")  # end_turn
print(f"Input tokens: {response.usage.input_tokens}")   # 12
print(f"Output tokens: {response.usage.output_tokens}")  # 8
print(f"Content: {response.content[0].text}")  # 1+1은 2입니다.
```

### Messages API 요청/응답 구조

```mermaid
flowchart LR
    subgraph Request["요청 (Request)"]
        direction TB
        M["model\nclaude-sonnet-4-5"]
        MT["max_tokens\n1024"]
        SYS["system\n시스템 프롬프트"]
        MSG["messages\n[user/assistant 배열]"]
    end

    subgraph Processing["Claude 처리"]
        direction TB
        P1["시스템 프롬프트\n적용"]
        P2["대화 맥락\n분석"]
        P3["응답 생성"]
    end

    subgraph Response["응답 (Response)"]
        direction TB
        RID["id\nmsg_01XXX..."]
        RROLE["role\nassistant"]
        RCONT["content\n[TextBlock, ...]"]
        RSTOP["stop_reason\nend_turn | tool_use"]
        RUSAGE["usage\ninput/output tokens"]
    end

    M --> P1
    MT --> P1
    SYS --> P1
    MSG --> P2
    P1 --> P2
    P2 --> P3
    P3 --> RID
    P3 --> RROLE
    P3 --> RCONT
    P3 --> RSTOP
    P3 --> RUSAGE

    style M fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style MT fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style SYS fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style MSG fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style P1 fill:#0984e3,stroke:#74b9ff,color:#fff
    style P2 fill:#0984e3,stroke:#74b9ff,color:#fff
    style P3 fill:#0984e3,stroke:#74b9ff,color:#fff
    style RID fill:#00b894,stroke:#55efc4,color:#fff
    style RROLE fill:#00b894,stroke:#55efc4,color:#fff
    style RCONT fill:#00b894,stroke:#55efc4,color:#fff
    style RSTOP fill:#00b894,stroke:#55efc4,color:#fff
    style RUSAGE fill:#00b894,stroke:#55efc4,color:#fff
```

---

## 3. Claude 모델 라인업

### 최신 모델 목록

Anthropic은 용도에 따라 여러 모델 계열을 제공합니다. 2025년 기준 주요 모델은 다음과 같습니다.

| 모델 ID | 계열 | 컨텍스트 윈도우 | 최대 출력 | 특징 |
|---------|------|-----------------|-----------|------|
| `claude-opus-4-5-20250514` | Opus | 200K | 16,384 | 최고 성능, 복잡한 분석 |
| `claude-sonnet-4-5-20250514` | Sonnet | 200K | 16,384 | 성능/비용 균형, **범용 추천** |
| `claude-haiku-3-5-20241022` | Haiku | 200K | 8,192 | 빠른 속도, 저비용 |

### 200K 컨텍스트 윈도우

Claude의 모든 최신 모델은 **200,000 토큰**의 컨텍스트 윈도우를 지원합니다. 이는 대략 다음과 같은 분량입니다.

| 기준 | 대략적인 분량 |
|------|--------------|
| 영문 단어 | 약 150,000 단어 |
| 한국어 글자 | 약 100,000자 |
| A4 문서 | 약 500페이지 |
| 소스 코드 | 약 50,000줄 |

> **핵심 포인트:** 200K 컨텍스트 윈도우는 긴 PDF 문서 전체를 한 번에 넣고 분석하거나, 대규모 코드베이스를 통째로 리뷰하는 작업에 매우 유용합니다.

### 모델별 비용 비교

| 모델 | 입력 (1M 토큰당) | 출력 (1M 토큰당) | 상대 속도 |
|------|------------------|------------------|-----------|
| Opus 4.5 | $15.00 | $75.00 | 느림 |
| Sonnet 4.5 | $3.00 | $15.00 | 보통 |
| Haiku 3.5 | $0.80 | $4.00 | 빠름 |

### 용도별 모델 선택 가이드

| 용도 | 추천 모델 | 이유 |
|------|-----------|------|
| 프로토타입 개발 | Sonnet 4.5 | 성능과 비용의 최적 균형 |
| 단순 분류/추출 | Haiku 3.5 | 빠른 응답, 저렴한 비용 |
| 복잡한 코드 생성 | Opus 4.5 | 최고 수준의 추론 능력 |
| 고객 챗봇 | Haiku 3.5 | 실시간 응답 필요 |
| 문서 요약/분석 | Sonnet 4.5 | 긴 문서 처리 + 적절한 비용 |
| 연구/논문 분석 | Opus 4.5 | 깊은 이해와 정확한 분석 |

```python
# model_selection.py -- 용도별 모델 선택 예시
from anthropic import Anthropic

client = Anthropic()

# 빠른 분류 작업 → Haiku
classification = client.messages.create(
    model="claude-haiku-3-5-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "이 리뷰의 감성을 분류하세요: '배송이 빨라서 좋았어요'"}]
)

# 복잡한 코드 생성 → Sonnet (비용 대비 성능)
code_gen = client.messages.create(
    model="claude-sonnet-4-5-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": "FastAPI로 JWT 인증이 포함된 CRUD API를 만들어주세요."}]
)
```

---

## 4. 도구 사용 (Tool Use)

### Tool Use란?

Claude는 외부 함수를 호출하여 실시간 데이터를 조회하거나 계산을 수행할 수 있습니다. 이를 **Tool Use**라고 합니다. OpenAI의 Function Calling과 유사한 개념이지만 구현 방식에 차이가 있습니다.

Tool Use의 핵심 흐름은 다음과 같습니다.

1. 개발자가 사용 가능한 **도구(tools)**를 정의하여 API에 전달합니다
2. Claude가 사용자의 질문을 분석하고, 도구가 필요하다고 판단하면 **`tool_use` 블록**을 응답합니다
3. 개발자가 해당 도구를 실제로 실행하고, 결과를 **`tool_result` 블록**으로 돌려보냅니다
4. Claude가 도구 결과를 참고하여 최종 답변을 생성합니다

### 도구 정의

```python
# tool_definition.py -- 도구 스키마 정의
tools = [
    {
        "name": "get_weather",
        "description": "지정된 도시의 현재 날씨 정보를 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "날씨를 조회할 도시명 (예: '서울', '부산')"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "온도 단위"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "calculator",
        "description": "수학 계산을 수행합니다. 사칙연산, 거듭제곱, 제곱근 등을 지원합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "계산할 수학 표현식 (예: '2 + 3 * 4')"
                }
            },
            "required": ["expression"]
        }
    }
]
```

### tool_use 응답과 tool_result 요청

Claude가 도구를 사용하기로 결정하면, `stop_reason`이 `"end_turn"` 대신 `"tool_use"`가 되고, `content` 배열에 `tool_use` 블록이 포함됩니다.

```python
# tool_use_flow.py -- tool_use 전체 흐름 구현
from anthropic import Anthropic
import json

client = Anthropic()

# 실제 도구 함수 구현
def get_weather(city: str, unit: str = "celsius") -> dict:
    """실제로는 외부 API를 호출합니다. 여기서는 더미 데이터를 반환합니다."""
    weather_data = {
        "서울": {"temp": 22, "condition": "맑음", "humidity": 45},
        "부산": {"temp": 25, "condition": "구름 조금", "humidity": 60},
        "제주": {"temp": 27, "condition": "흐림", "humidity": 75},
    }
    return weather_data.get(city, {"temp": 20, "condition": "정보 없음", "humidity": 50})

def calculator(expression: str) -> str:
    """수학 표현식을 안전하게 계산합니다."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"계산 오류: {str(e)}"

# 도구 실행 함수 매핑
tool_functions = {
    "get_weather": lambda params: get_weather(**params),
    "calculator": lambda params: calculator(**params),
}

# 1단계: Claude에게 질문 + 도구 정의 전달
response = client.messages.create(
    model="claude-sonnet-4-5-20250514",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "서울의 현재 날씨를 알려주세요."}
    ]
)

# 2단계: stop_reason 확인 및 도구 실행
if response.stop_reason == "tool_use":
    # tool_use 블록 찾기
    tool_use_block = next(
        block for block in response.content
        if block.type == "tool_use"
    )

    tool_name = tool_use_block.name       # "get_weather"
    tool_input = tool_use_block.input     # {"city": "서울"}
    tool_id = tool_use_block.id           # "toolu_01XXX..."

    # 도구 실제 실행
    result = tool_functions[tool_name](tool_input)

    # 3단계: tool_result를 Claude에게 돌려보내기
    final_response = client.messages.create(
        model="claude-sonnet-4-5-20250514",
        max_tokens=1024,
        tools=tools,
        messages=[
            {"role": "user", "content": "서울의 현재 날씨를 알려주세요."},
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": json.dumps(result, ensure_ascii=False)
                    }
                ]
            }
        ]
    )

    print(final_response.content[0].text)
    # 출력: 서울의 현재 날씨는 맑음이며, 기온은 22°C, 습도는 45%입니다.
```

### 자동 도구 실행 루프

실제 애플리케이션에서는 Claude가 도구를 여러 번 연속으로 호출할 수 있으므로, **루프 방식**으로 처리합니다.

```python
# tool_loop.py -- 자동 도구 실행 루프
from anthropic import Anthropic
import json

client = Anthropic()

def run_conversation(user_message: str, tools: list, tool_functions: dict) -> str:
    """도구 호출이 끝날 때까지 자동으로 루프를 돌며 대화합니다."""
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        # 도구 호출이 아니면 최종 응답 반환
        if response.stop_reason == "end_turn":
            return response.content[0].text

        # 도구 호출 처리
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = tool_functions[block.name](block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })

        messages.append({"role": "user", "content": tool_results})

# 실행
answer = run_conversation(
    "서울 날씨를 확인하고, 기온을 화씨로 변환해주세요. 계산기를 사용하세요.",
    tools=tools,
    tool_functions=tool_functions
)
print(answer)
```

### OpenAI Function Calling vs Claude Tool Use 비교

| 항목 | OpenAI Function Calling | Claude Tool Use |
|------|------------------------|-----------------|
| 도구 정의 위치 | `tools` 파라미터 | `tools` 파라미터 |
| 스키마 키 | `parameters` (JSON Schema) | `input_schema` (JSON Schema) |
| 응답 위치 | `tool_calls` 배열 | `content` 배열 내 `tool_use` 블록 |
| 결과 전달 | `{"role": "tool", "tool_call_id": ...}` | `{"type": "tool_result", "tool_use_id": ...}` |
| 종료 판단 | `finish_reason != "tool_calls"` | `stop_reason != "tool_use"` |
| 병렬 호출 | `parallel_tool_calls` 지원 | content 배열에 여러 tool_use 블록 |
| 강제 호출 | `tool_choice: {"type": "function", ...}` | `tool_choice: {"type": "tool", "name": ...}` |

> **핵심 포인트:** Claude의 Tool Use는 결과를 `tool_result` 타입의 content 블록으로 전달하는 반면, OpenAI는 별도의 `tool` 역할 메시지를 사용합니다. 구조적으로 Claude 쪽이 더 일관된 content 블록 시스템을 유지합니다.

### Tool Use 루프 흐름

```mermaid
flowchart TB
    A["사용자 질문 입력"] --> B["Claude API 호출\ntools + messages 전달"]
    B --> C{"stop_reason\n확인"}
    C -->|"end_turn"| D["최종 텍스트 응답\n사용자에게 반환"]
    C -->|"tool_use"| E["tool_use 블록 파싱\nname, input, id 추출"]
    E --> F["로컬 함수 실행\ntool_functions 매핑"]
    F --> G["tool_result 생성\ntool_use_id + 결과"]
    G --> H["messages에\nassistant 응답 + tool_result 추가"]
    H --> B

    style A fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style B fill:#0984e3,stroke:#74b9ff,color:#fff
    style C fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style D fill:#00b894,stroke:#55efc4,color:#fff
    style E fill:#e17055,stroke:#fab1a0,color:#fff
    style F fill:#e17055,stroke:#fab1a0,color:#fff
    style G fill:#e17055,stroke:#fab1a0,color:#fff
    style H fill:#0984e3,stroke:#74b9ff,color:#fff
```

---

## 5. 확장 사고 (Extended Thinking)

### Extended Thinking이란?

Claude Sonnet 4.5는 **확장 사고(Extended Thinking)** 기능을 지원합니다. 이 기능을 활성화하면 Claude가 답변을 생성하기 전에 **내부적으로 단계적 추론 과정**을 거칩니다. 이 사고 과정은 별도의 `thinking` 블록으로 반환되어 개발자가 확인할 수 있습니다.

복잡한 수학 문제, 다단계 논리 추론, 코드 디버깅 등에서 정확도가 크게 향상됩니다.

### thinking 파라미터 활성화

```python
# extended_thinking_basic.py -- Extended Thinking 활성화
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # 사고 과정에 할당할 최대 토큰 수
    },
    messages=[
        {
            "role": "user",
            "content": "1부터 100까지의 소수를 모두 찾고, 그 합을 구해주세요."
        }
    ]
)
```

> **핵심 포인트:** `budget_tokens`는 Claude가 사고 과정에 사용할 수 있는 **최대 토큰 수**입니다. 이 값은 `max_tokens`에 포함되지 않으며 별도로 계산됩니다. 복잡한 문제일수록 `budget_tokens`를 크게 설정해야 합니다.

### thinking 블록과 text 블록 분리 파싱

Extended Thinking이 활성화되면 응답의 `content` 배열에 `thinking` 블록과 `text` 블록이 순서대로 포함됩니다.

```python
# parse_thinking.py -- thinking 블록 분리 파싱
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 8000
    },
    messages=[
        {
            "role": "user",
            "content": "372 × 841 + 1597 ÷ 13의 결과를 단계별로 계산해주세요."
        }
    ]
)

# content 배열에서 블록 타입별 분리
for block in response.content:
    if block.type == "thinking":
        print("=== 사고 과정 ===")
        print(block.thinking)
        print()
    elif block.type == "text":
        print("=== 최종 답변 ===")
        print(block.text)

# 토큰 사용량 확인
print(f"\n입력 토큰: {response.usage.input_tokens}")
print(f"출력 토큰: {response.usage.output_tokens}")
```

### 코드 예제: 복잡한 수학 문제 + thinking 출력

```python
# thinking_math.py -- 복잡한 수학 문제에 Extended Thinking 적용
from anthropic import Anthropic

client = Anthropic()

problem = """
한 공장에서 제품 A와 제품 B를 생산합니다.
- 제품 A는 1개당 원재료 3kg, 노동 2시간이 필요하며, 이익은 5만원입니다.
- 제품 B는 1개당 원재료 2kg, 노동 4시간이 필요하며, 이익은 4만원입니다.
- 하루에 사용 가능한 원재료는 120kg, 노동시간은 100시간입니다.
- 이익을 최대화하려면 각 제품을 몇 개씩 생산해야 하나요?
선형 계획법(LP)으로 풀어주세요.
"""

response = client.messages.create(
    model="claude-sonnet-4-5-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    messages=[{"role": "user", "content": problem}]
)

# 사고 과정과 최종 답변 분리 출력
for block in response.content:
    if block.type == "thinking":
        print("[Claude의 사고 과정]")
        print(block.thinking[:500] + "...")  # 처음 500자만 출력
        print()
    elif block.type == "text":
        print("[최종 답변]")
        print(block.text)
```

### Extended Thinking 사용 시 주의사항

| 항목 | 설명 |
|------|------|
| 지원 모델 | `claude-sonnet-4-5`, `claude-opus-4-5` |
| `budget_tokens` 범위 | 1,024 ~ 128,000 |
| 비용 | thinking 토큰도 출력 토큰 요금 적용 |
| `temperature` | Extended Thinking 사용 시 반드시 `1` (변경 불가) |
| 스트리밍 호환 | 스트리밍과 함께 사용 가능 |
| 멀티턴 | thinking 블록은 다음 턴의 messages에 포함하지 않음 |

### Extended Thinking 처리 흐름

```mermaid
flowchart TB
    A["사용자: 복잡한 질문 입력"] --> B["API 호출\nthinking.type = enabled\nbudget_tokens = 10000"]
    B --> C["Claude 내부 추론 시작\nThinking 블록 생성"]
    C --> D["단계적 사고 과정\n수식 전개, 논리 점검, 검증"]
    D --> E["사고 과정 완료\n최종 답변 도출"]
    E --> F["응답 반환\ncontent: [ThinkingBlock, TextBlock]"]
    F --> G["개발자: 블록 타입별 파싱"]
    G --> H["thinking 블록\n사고 과정 로그 저장"]
    G --> I["text 블록\n사용자에게 최종 답변 표시"]

    style A fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style B fill:#0984e3,stroke:#74b9ff,color:#fff
    style C fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style D fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style E fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style F fill:#00b894,stroke:#55efc4,color:#fff
    style G fill:#e17055,stroke:#fab1a0,color:#fff
    style H fill:#fd79a8,stroke:#e84393,color:#fff
    style I fill:#00b894,stroke:#55efc4,color:#fff
```

---

## 6. 스트리밍과 대용량 처리

### 스트리밍이 필요한 이유

Claude가 긴 응답을 생성할 때, 전체 응답이 완성될 때까지 기다리면 사용자는 수 초에서 수십 초간 아무런 피드백 없이 대기해야 합니다. **스트리밍**을 사용하면 토큰이 생성되는 즉시 실시간으로 전달받아 사용자에게 점진적으로 표시할 수 있습니다.

### 기본 스트리밍 패턴

```python
# streaming_basic.py -- 기본 스트리밍 구현
from anthropic import Anthropic

client = Anthropic()

# with 문을 사용한 스트리밍
with client.messages.stream(
    model="claude-sonnet-4-5-20250514",
    max_tokens=2048,
    messages=[
        {"role": "user", "content": "파이썬의 데코레이터를 상세히 설명해주세요."}
    ]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print()  # 줄바꿈
```

### 이벤트 기반 스트리밍

더 세밀한 제어가 필요한 경우 이벤트 타입별로 처리할 수 있습니다.

```python
# streaming_events.py -- 이벤트 타입별 스트리밍 처리
from anthropic import Anthropic

client = Anthropic()

with client.messages.stream(
    model="claude-sonnet-4-5-20250514",
    max_tokens=2048,
    messages=[
        {"role": "user", "content": "REST API 설계 원칙을 설명해주세요."}
    ]
) as stream:
    for event in stream:
        if event.type == "message_start":
            print(f"[시작] 모델: {event.message.model}")
        elif event.type == "content_block_start":
            print(f"[블록 시작] 타입: {event.content_block.type}")
        elif event.type == "content_block_delta":
            if event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)
        elif event.type == "message_delta":
            print(f"\n[완료] stop_reason: {event.delta.stop_reason}")
            print(f"[토큰] 출력: {event.usage.output_tokens}")
        elif event.type == "message_stop":
            print("[메시지 종료]")
```

### 주요 스트리밍 이벤트 타입

| 이벤트 타입 | 설명 | 포함 데이터 |
|-------------|------|------------|
| `message_start` | 메시지 생성 시작 | model, usage (입력 토큰) |
| `content_block_start` | content 블록 시작 | 블록 index, type |
| `content_block_delta` | content 블록 데이터 조각 | text_delta / tool_use delta |
| `content_block_stop` | content 블록 완료 | 블록 index |
| `message_delta` | 메시지 수준 업데이트 | stop_reason, usage (출력 토큰) |
| `message_stop` | 전체 메시지 완료 | 없음 |

### FastAPI SSE 연동

실제 웹 애플리케이션에서 스트리밍을 활용하는 가장 일반적인 방식은 **Server-Sent Events(SSE)** 입니다.

```python
# fastapi_sse.py -- FastAPI SSE 스트리밍 엔드포인트
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from anthropic import Anthropic
import json

app = FastAPI()
client = Anthropic()

async def generate_stream(user_message: str):
    """Claude 스트리밍 응답을 SSE 형식으로 변환합니다."""
    with client.messages.stream(
        model="claude-sonnet-4-5-20250514",
        max_tokens=4096,
        system="당신은 친절한 AI 비서입니다.",
        messages=[{"role": "user", "content": user_message}]
    ) as stream:
        for text in stream.text_stream:
            # SSE 형식: "data: ...\n\n"
            data = json.dumps({"text": text}, ensure_ascii=False)
            yield f"data: {data}\n\n"

    yield "data: [DONE]\n\n"

@app.post("/chat/stream")
async def chat_stream(request: dict):
    """SSE 스트리밍 채팅 엔드포인트"""
    return StreamingResponse(
        generate_stream(request["message"]),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

프론트엔드에서는 `EventSource` 또는 `fetch` API로 SSE를 수신합니다.

```javascript
// frontend_sse.js -- 프론트엔드 SSE 수신
const response = await fetch("/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: "안녕하세요!" })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n");

    for (const line of lines) {
        if (line.startsWith("data: ") && line !== "data: [DONE]") {
            const data = JSON.parse(line.slice(6));
            document.getElementById("output").textContent += data.text;
        }
    }
}
```

> **핵심 포인트:** 스트리밍을 사용하면 첫 토큰 응답 시간(TTFT, Time To First Token)이 크게 단축됩니다. 사용자 체감 속도가 향상되므로, 사용자에게 직접 응답을 보여주는 서비스에서는 반드시 스트리밍을 적용하십시오.

### 스트리밍 이벤트 시퀀스

```mermaid
flowchart LR
    A["API 요청"] --> B["message_start"]
    B --> C["content_block_start"]
    C --> D["content_block_delta<br/>반복"]
    D --> E["content_block_stop"]
    E --> F["message_delta<br/>stop_reason"]
    F --> G["message_stop"]

    style A fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style B fill:#0984e3,stroke:#74b9ff,color:#fff
    style C fill:#0984e3,stroke:#74b9ff,color:#fff
    style D fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style E fill:#0984e3,stroke:#74b9ff,color:#fff
    style F fill:#e17055,stroke:#fab1a0,color:#fff
    style G fill:#00b894,stroke:#55efc4,color:#fff
```

---

## 7. 핵심 정리

### OpenAI vs Claude API 기능 비교 대형 표

이번 강의에서 배운 Claude API의 특징을 OpenAI API와 비교하여 정리합니다.

| 기능 영역 | OpenAI API | Claude API (Anthropic) |
|-----------|-----------|----------------------|
| **SDK 패키지** | `openai` | `anthropic` |
| **기본 엔드포인트** | `chat.completions.create()` | `messages.create()` |
| **시스템 프롬프트** | messages 배열 내 `role: "system"` | 별도 `system` 파라미터 |
| **메시지 규칙** | system/user/assistant 자유 배치 | user/assistant 엄격한 교번 |
| **컨텍스트 윈도우** | 128K (GPT-4o) | 200K (전 모델) |
| **응답 접근** | `response.choices[0].message.content` | `response.content[0].text` |
| **Function Calling** | `tools` + `tool_calls` | `tools` + `tool_use` content 블록 |
| **도구 결과 전달** | `role: "tool"` 메시지 | `type: "tool_result"` content 블록 |
| **도구 스키마 키** | `parameters` | `input_schema` |
| **구조화 출력** | `response_format: { type: "json_schema" }` | system 프롬프트에서 JSON 지시 |
| **스트리밍** | `stream=True` + 이터레이터 | `client.messages.stream()` context manager |
| **확장 사고** | o1/o3 계열 reasoning_effort | `thinking` 파라미터 + budget_tokens |
| **사고 과정 접근** | reasoning 토큰 비공개 | `thinking` 블록으로 직접 확인 가능 |
| **이미지 입력** | `image_url` 타입 | `image` 타입 (base64/URL) |
| **임베딩** | `embeddings.create()` | 별도 임베딩 API 없음 (Voyage AI 권장) |
| **파인튜닝** | Fine-tuning API 제공 | 공식 파인튜닝 미제공 |
| **배치 처리** | Batch API 제공 | Message Batches API 제공 |
| **비용 모델** | 모델/토큰 기반 과금 | 모델/토큰 기반 과금 |
| **Rate Limit** | TPM/RPM 기반 | RPM/TPM/TPMD 기반 |

### 주요 설계 철학 차이

| 관점 | OpenAI | Anthropic |
|------|--------|-----------|
| API 구조 | 기능별 분산 엔드포인트 | 단일 Messages API 중심 |
| 안전성 | 사후 필터링 중심 | Constitutional AI, 사전 학습 중심 |
| 사고 과정 | 비공개 (reasoning tokens) | 공개 (thinking block) |
| 확장성 | 다양한 부가 서비스 (DALL-E, Whisper 등) | 텍스트/비전 특화, 파트너 생태계 |

### 이번 강의에서 배운 것

1. **Anthropic SDK 설치와 초기화** — `pip install anthropic`, 환경변수 기반 API 키 관리
2. **Messages API 구조** — system 파라미터 분리, user/assistant 교번 규칙, content 블록 시스템
3. **모델 라인업** — Opus(최고 성능), Sonnet(균형), Haiku(속도/비용) 3단계 전략
4. **Tool Use** — 도구 정의, `stop_reason: "tool_use"` 분기, 자동 루프 패턴
5. **Extended Thinking** — `thinking` 파라미터, `budget_tokens`, 사고 블록 파싱
6. **스트리밍** — `client.messages.stream()`, SSE 연동, 이벤트 타입별 처리

### 실습 과제

| 과제 | 난이도 | 설명 |
|------|--------|------|
| 기본 챗봇 | 초급 | 멀티턴 대화를 유지하는 콘솔 챗봇 구현 |
| 도구 통합 챗봇 | 중급 | 계산기 + 날씨 + 환율 도구를 갖춘 챗봇 구현 |
| 스트리밍 웹 챗봇 | 중급 | FastAPI + SSE로 실시간 스트리밍 챗봇 구현 |
| Thinking 분석기 | 고급 | Extended Thinking으로 수학 문제를 풀고 사고 과정을 시각화 |

### 다음 강의 예고

다음 강의에서는 **Google Gemini API**를 살펴봅니다. Google의 Gemini 모델은 멀티모달 성능이 특히 뛰어나며, 100만 토큰의 컨텍스트 윈도우, 네이티브 Google Search 통합 등 독자적인 특징을 가지고 있습니다. OpenAI, Anthropic, Google 세 가지 주요 LLM API를 모두 다룬 후, 이를 통합하여 활용하는 방법을 배우게 됩니다.

---
