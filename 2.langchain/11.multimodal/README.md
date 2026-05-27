# 멀티모달 (Multimodal)

텍스트 외에 **이미지 등 다른 형식의 입력**을 LLM 에 함께 보내는 패턴.

## 폴더 구조

```
5.multimodal/
├── 1.chat_with_image.py   ← 이미지 URL 을 chat 메시지에 포함시켜 gpt-4o 호출
└── README.md
```

## 핵심 개념

### chat 메시지의 content 는 문자열이 아니라 "content block 리스트" 가 될 수 있다

OpenAI gpt-4o / gpt-4o-mini 같은 **비전 지원 모델**은 메시지의 content 가 단순 문자열 대신 **type 이 다른 블록의 리스트** 형태도 받습니다:

```python
HumanMessage(content=[
    {"type": "text",      "text": "이 이미지를 한 줄로 설명해줘"},
    {"type": "image_url", "image_url": {"url": "https://example.com/img.jpg"}},
])
```

LangChain 의 `HumanMessage` 가 이 구조를 그대로 받아 OpenAI API 형식으로 전달합니다.

### 이미지 입력 방식 두 가지

| 방식 | 형태 | 용도 |
|------|------|------|
| **URL** | `"url": "https://..."` | 공개 URL 의 이미지 |
| **Base64** | `"url": "data:image/jpeg;base64,...""` | 로컬 파일을 base64 로 인코딩해서 |

### 어떤 모델이 vision 지원하나?

- ✅ `gpt-4o`, `gpt-4o-mini` (OpenAI)
- ✅ `claude-3-5-sonnet`, `claude-opus-4` 계열 (Anthropic)
- ✅ `gemini-1.5-pro`, `gemini-2.0-flash` (Google)
- ❌ `gpt-3.5-turbo`, `gpt-3.5-turbo-instruct`

## 파일 상세

### `1.chat_with_image.py`
- `ChatPromptTemplate` 에 이미지 URL 을 포함시켜 gpt-4o 호출
- 텍스트 prompt + 이미지를 함께 모델에 전달하여 이미지 내용 분석

## 확장 아이디어

- **로컬 파일 → base64 인코딩** 예제 추가
- **여러 이미지 동시 입력** (비교 작업)
- **이미지 + 함수 호출** (vision + tool calling)
- **PDF 페이지 이미지 → 분석** (RAG with vision)

## 관련 폴더

- [`../1.llm_models/`](../1.llm_models/) — 어떤 모델이 멀티모달 지원하는지
- [`../2.prompts/`](../2.prompts/) — chat 메시지 구성 기본기
