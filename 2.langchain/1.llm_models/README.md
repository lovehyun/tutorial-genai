# LLM 모델 가이드 — OpenAI API · Instruct 튜닝 · 오픈소스 모델

이 문서는 `1.llm_models` 폴더의 예제들을 이해하기 위해 알아두어야 할 배경 지식을 정리합니다.

## 다루는 내용

1. **OpenAI API 두 종류** — Chat Completions vs Legacy Completions
2. **Instruct Fine-tuning 개념** — Instruct 모델이란 무엇이고 파인튜닝과 어떤 관계인지
3. **오픈소스 LLM 모델 비교** — GPT-2 / GPT-Neo / Mistral 등 학습/실습용 참고
4. **실무 가이드 (2026년 기준)** — 새 프로젝트에서 어떻게 선택할지

---

## 1. OpenAI API: Chat Completions vs Legacy Completions

OpenAI에는 이름에 "completions"가 들어가는 엔드포인트가 **두 개**입니다. 이걸 같은 것으로 오해하면 설명이 완전히 꼬이므로 먼저 구분해 둡니다.

### 1.1 두 엔드포인트 비교

| 구분 | 엔드포인트 | 상태 | 입력 형식 | 지원 모델 | LangChain 래퍼 |
|------|-----------|------|----------|----------|---------------|
| **Chat Completions API** | `POST /v1/chat/completions` | ✅ 현역 / 표준 | `messages=[{role, content}, ...]` | gpt-4o, gpt-4o-mini, gpt-4, gpt-3.5-turbo, o1 시리즈 등 거의 전부 | `ChatOpenAI` |
| **(Legacy) Completions API** | `POST /v1/completions` | ⚠️ Legacy | `prompt="..."` (단일 문자열) | 사실상 `gpt-3.5-turbo-instruct` 하나 | `OpenAI` (`langchain_openai.OpenAI`) |

### 1.2 OpenAI 모델별 지원 현황

| 모델 | Chat (`/v1/chat/completions`) | Legacy Completion (`/v1/completions`) | 비고 |
|------|-------------------------------|---------------------------------------|------|
| `gpt-4o` | ✅ | ❌ | 최신 멀티모달 Chat 모델 |
| `gpt-4o-mini` | ✅ | ❌ | 경량 Chat 모델 |
| `gpt-4` | ✅ | ❌ | Chat 모델 |
| `gpt-3.5-turbo` | ✅ | ❌ | Chat 모델 |
| `gpt-3.5-turbo-instruct` | ❌ | ✅ | 현재 유일하게 살아있는 Instruct 모델 |
| `text-davinci-003` | ❌ | (deprecated) | 2024년 1월 사용 중단 |

### 1.3 헷갈리기 쉬운 질문

- **"Completions API 많이 쓰지 않나요?"**
  → 맞습니다. 단, 그건 **Chat Completions** (`/v1/chat/completions`) 얘기입니다. 새 프로젝트는 사실상 전부 이걸 씁니다.
- **"gpt-4o-mini도 completions에서 쓰는 거 아닌가요?"**
  → Chat Completions에서는 ✅ 쓰지만, Legacy Completions(`/v1/completions`)로는 ❌ 호출할 수 없습니다.
- **"그럼 Legacy Completions는 이제 안 쓰나요?"**
  → 거의 안 씁니다. 다만 다음 경우에 여전히 살아있습니다.
  1. 기존 레거시 코드/시스템 유지보수
  2. 코드 자동완성처럼 "대화 구조"가 오히려 방해되는 작업
  3. `logprobs`, `echo`, `suffix`(중간 채우기) 등 Chat API에 없는 옛 옵션이 필요한 경우
  4. `gpt-3.5-turbo-instruct`의 저렴한 단가로 대량 배치 처리할 때

### 1.4 입력 형식 비교 (코드)

```python
# (A) Chat Completions API — 표준
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "당신은 한영 번역가입니다."},
        {"role": "user",   "content": "안녕하세요, 반갑습니다."},
    ],
)

# (B) Legacy Completions API
response = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="다음 문장을 영어로 번역해줘:\n안녕하세요, 반갑습니다.",
)
```

### 1.5 `gpt-3.5-turbo` vs `gpt-3.5-turbo-instruct` — 대체 뭐가 다른가?

이름이 비슷해서 가장 많이 헷갈리는 두 모델입니다. **같은 GPT-3.5 가문에서 갈라져 나왔지만, 학습 목적과 API 자체가 다른 별개의 제품**입니다.

**한 줄 요약**

- `gpt-3.5-turbo` = "**대화**"용으로 다듬은 모델 → Chat Completions API
- `gpt-3.5-turbo-instruct` = "**단발 지시 수행**"용으로 다듬은 모델 (`text-davinci-003`의 후속) → Legacy Completions API

**세부 비교**

| 항목 | `gpt-3.5-turbo` | `gpt-3.5-turbo-instruct` |
|------|-----------------|--------------------------|
| **포지셔닝** | ChatGPT 엔진 — 멀티턴 대화용 | `text-davinci-003`의 후속 — 한 방 지시 수행용 |
| **API 엔드포인트** | `/v1/chat/completions` | `/v1/completions` (legacy) |
| **입력 형식** | `messages=[{role, content}, ...]` | `prompt="..."` (단일 문자열) |
| **출력 형식** | 구조화된 객체 (`.message.content`) | 평문 문자열 |
| **튜닝 방식** | Chat 스타일 RLHF (대화 흐름·역할 분리·페르소나 강조) | Instruction-following SFT (지시→정답 한 번에) |
| **Role / System 메시지** | ✅ 있음 | ❌ 없음 (다 prompt에 직접 적어야 함) |
| **Function / Tool calling** | ✅ 지원 | ❌ 미지원 |
| **JSON mode / structured output** | ✅ 지원 | ❌ 미지원 |
| **`logprobs`, `echo`, `suffix`(중간 채우기)** | ❌ 미지원 | ✅ 지원 (legacy 옵션) |
| **LangChain 래퍼** | `ChatOpenAI` | `OpenAI` |
| **가격 (참고)** | 더 저렴 | 더 비쌈 (의외) |
| **현재 상태** | 현역, 새 프로젝트 추천 | 살아있지만 사실상 maintenance 모드 |

**같은 작업을 시켜보면 차이가 보임**

작업: "아케이드 게임 회사 이름 추천해줘"

```python
# gpt-3.5-turbo (Chat) — 페르소나/지시 분리 가능
client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "너는 작명 전문가야."},
        {"role": "user",   "content": "아케이드 게임 회사 이름 추천해줘."},
    ],
)

# gpt-3.5-turbo-instruct (Completion) — 한 줄짜리 지시
client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="아케이드 게임 회사 이름 추천해줘.",
)
```

**그래서 왜 둘 다 살아있나?**

- **`gpt-3.5-turbo`**: ChatGPT / 일반 대화 / 에이전트의 주력 모델로 여전히 자주 쓰임 (특히 비용 민감한 곳).
- **`gpt-3.5-turbo-instruct`**: 옛 Davinci 기반 시스템 마이그레이션, 코드 자동완성(중간 채우기 `suffix`), `logprobs` 분석 같은 **Chat API에는 없는 옛 기능이 필요한 케이스**에 한정해서 쓰임.

**한 줄 결론**

같은 가문 출신이지만, **`gpt-3.5-turbo`는 "대화하는 사람"으로 키워졌고, `gpt-3.5-turbo-instruct`는 "지시 받으면 한 번에 답하는 사람"으로 키워졌다** — 그래서 입출력 형식부터 지원 기능까지 전부 다릅니다.

---

## 2. Instruct Fine-tuning 개념

### 2.1 Instruct Fine-tuning이란?

**Instruct Fine-tuning**은 기본 언어 모델을 "명령을 이해하고 수행하는 대화형 모델"로 만드는 학습 기법입니다.

- **목적**: 명령(instruction)에 반응하여 정답형 응답을 하도록 튜닝
- **데이터 형식 (Alpaca 스타일)**:
    ```json
    {
      "instruction": "Translate to French.",
      "input": "Hello, world.",
      "output": "Bonjour, le monde."
    }
    ```
- **효과**:
  - 명령형 프롬프트에 잘 반응함 ("Summarize", "List", "Explain" 등)
  - 일반 LLM 대비 명확하고 목적 지향적인 응답 생성

### 2.2 "Instruct"의 진짜 의미 (자주 헷갈리는 부분)

> "Instruct 모델은 뭘 학습시키는 용도 아니었어?" 라는 질문이 흔히 나옵니다.

"Instruct"는 **instruction-tuning(지시를 따르도록 SFT/RLHF로 후처리)된 결과물**을 가리키는 말입니다.
즉 학습의 **산출물**이지, "이걸로 학습시키는 베이스 모델"이 아닙니다. ChatGPT 계열(gpt-3.5-turbo, gpt-4o 등)도 모두 내부적으로 instruction-tuned 상태입니다.

### 2.3 왜 "Completion 모델 = 파인튜닝용"이라는 인상이 남았을까?

초창기 OpenAI 파인튜닝은 `davinci`, `curie`, `babbage`, `ada` 같은 **base completion 모델**을 대상으로 했기 때문입니다. 그래서 "파인튜닝 = completion 모델로 한다"는 인상이 굳어졌습니다.

### 2.4 옛날 vs 지금의 파인튜닝

| 항목 | 과거 | 현재 (2026) |
|------|------|-------------|
| 대상 모델 | `davinci`, `curie` 등 base completion | `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo` 등 **Chat 모델** |
| 엔드포인트 | (legacy) | `POST /v1/fine_tuning/jobs` |
| 데이터 형식 | `{prompt, completion}` | Chat 메시지 형식 jsonl (`{"messages": [...]}`) |
| `gpt-3.5-turbo-instruct` | — | 파인튜닝 **불가** (legacy completion 계열은 대상에서 빠짐) |

요약: **옛날엔 base completion 모델을 파인튜닝했지만, 지금은 Chat 모델을 파인튜닝합니다.**

### 2.5 Instruct 튜닝된 대표 모델

- `text-davinci-003` *(⚠️ 2024년 1월 deprecation, 현재 사용 불가)*
- `gpt-3.5-turbo-instruct` — 현재 OpenAI에서 유일하게 살아있는 instruct(완성형) 모델
- `Mistral-7B-Instruct-v0.3` — 오픈소스 기반 instruct 모델
- `LLaMA2-Chat`, `Alpaca`, `OpenAssistant` — 커뮤니티 기반 instruct 모델
- *(최신 오픈소스 트렌드: Llama 3.x-Instruct, Qwen2.5-Instruct, Mixtral-Instruct 등)*

---

## 3. 오픈소스 LLM 모델 비교

이 절은 OpenAI API가 아닌 **로컬/오픈소스 모델**로 실험할 때 참고용입니다.

### 3.1 대표 모델 비교

| 항목 | GPT-2 | GPT-Neo-2.7B | Mistral-7B-Instruct-v0.3 |
|------|-------|---------------|---------------------------|
| 출시 시기 | 2019 | 2021 | 2024 (v0.3 기준) |
| 파라미터 수 | 1.5B | 2.7B | 7.3B |
| 구조 | GPT-2 (Decoder-only) | GPT-3 유사 구조 | 효율적인 GQA 구조 |
| 주요 기술 | 기본 Attention | GPT-3 모사 | GQA (v0.1은 Sliding Window 포함) |
| 학습 데이터 | OpenWebText | Pile (800GB+) | 비공개 (고품질 정제) |
| Instruct 튜닝 | ❌ 없음 | ❌ 없음 | ✅ 있음 |
| 명령 이해 | 매우 낮음 | 낮음 | 매우 높음 |
| 생성 품질 | 낮음 | 중간 | 매우 우수 |
| 지원 컨텍스트 | 1024 | 2048 | 32K |
| 메모리 요구 | 낮음 | 높음 (10GB+) | 높음 (8~12GB VRAM) |
| 라이선스 | MIT | Apache 2.0 | Apache 2.0 |

### 3.2 용도별 추천

| 목적 | 추천 모델 |
|------|----------|
| 빠른 테스트 / 데모 | GPT-2 |
| 무료 LLM 연구용 | GPT-Neo-2.7B |
| 실제 챗봇/요약/코딩 | Mistral-7B-Instruct-v0.3 (또는 최신 Llama 3.x-Instruct, Qwen2.5-Instruct) |

### 3.3 Instruct 튜닝 확인용 테스트 프롬프트

명령 수행 능력을 테스트하려면 아래 프롬프트를 각 모델에 넣고 응답을 비교해보세요.

| 테스트 목적 | 프롬프트 예시 |
|------------|--------------|
| SQL 생성 | `Write a SQL query to get top 5 customers by purchase amount in 2023.` |
| 요약 | `Summarize the following article: [본문]` |
| 번역 | `Translate this to Korean: "The product was well-received by customers."` |
| 이메일 작성 | `Write a formal email to request a meeting with the marketing team.` |
| 코드 작성 | `Write a Python function to calculate factorial recursively.` |
| JSON 변환 | `Convert the following data into JSON format: name: Alice, age: 30, city: Paris` |

> **비교 팁:** 같은 프롬프트를 GPT-2, GPT-Neo-2.7B, Mistral-7B-Instruct 등에 동일하게 입력해보면, Instruct 튜닝 여부에 따라 얼마나 다른 결과를 내는지 명확히 알 수 있습니다.

---

## 4. 실무 가이드 (2026년 기준)

- **새 프로젝트의 기본 선택** → Chat Completions API + `ChatOpenAI` (`gpt-4o`, `gpt-4o-mini` 등)
- **Legacy Completions API**와 instruct 전용 모델(`gpt-3.5-turbo-instruct`)은 **특수 케이스에서만** 사용
- **파인튜닝**도 이제는 **Chat 모델 기반**이 표준
- 이 튜토리얼의 LangChain 예제는 모두 `ChatOpenAI` 기준으로 진행됩니다.
  `langchain_openai.OpenAI`(legacy completion 래퍼)는 "이런 게 있었다" 정도의 학습용 참조로 보면 됩니다.
- 오픈소스 모델은 GPU 리소스가 받쳐주는 경우 Mistral / Llama 3.x / Qwen 계열의 Instruct 버전이 일반적인 선택.
