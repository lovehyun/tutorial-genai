# LLM 회사와 모델 총정리

> 주요 AI 회사들의 역사, 모델 라인업, 그리고 차이점

---

## 1. LLM 회사 전체 지형도 (2026년 기준)

```mermaid
flowchart TB
    subgraph 빅테크 ["빅테크 (Big Tech)"]
        direction LR
        OAI["OpenAI<br/>🇺🇸 미국<br/>GPT 시리즈<br/>$157B 가치"]
        ANT["Anthropic<br/>🇺🇸 미국<br/>Claude 시리즈<br/>$61.5B 가치"]
        GOO["Google DeepMind<br/>🇺🇸 미국<br/>Gemini 시리즈<br/>Alphabet 자회사"]
        META["Meta AI<br/>🇺🇸 미국<br/>Llama 시리즈<br/>오픈소스 리더"]
    end

    subgraph 도전자 ["도전자 (Challengers)"]
        direction LR
        XAI["xAI<br/>🇺🇸 미국<br/>Grok 시리즈<br/>Elon Musk"]
        MIS["Mistral AI<br/>🇫🇷 프랑스<br/>Mistral/Mixtral<br/>유럽 대표"]
        DS["DeepSeek<br/>🇨🇳 중국<br/>DeepSeek V3/R1<br/>초저가 혁신"]
    end

    subgraph 국내 ["국내/아시아"]
        direction LR
        NV["NAVER<br/>🇰🇷 한국<br/>HyperCLOVA X"]
        KT["KT<br/>🇰🇷 한국<br/>Mi:dm"]
        SK["SK텔레콤<br/>🇰🇷 한국<br/>A.(에이닷)"]
    end

    빅테크 ~~~ 도전자 ~~~ 국내

    style OAI fill:#74b9ff,stroke:#0984e3,color:#fff
    style ANT fill:#a29bfe,stroke:#6c5ce7,color:#fff
    style GOO fill:#55efc4,stroke:#00b894,color:#2d3436
    style META fill:#74b9ff,stroke:#0984e3,color:#fff
    style XAI fill:#2d3436,stroke:#636e72,color:#fff
    style MIS fill:#ff6b6b,stroke:#c0392b,color:#fff
    style DS fill:#fd79a8,stroke:#e84393,color:#fff
```

---

## 2. 주요 회사별 상세 프로필

### OpenAI — 생성형 AI의 선구자

```mermaid
timeline
    title OpenAI 주요 연혁
    2015 : 설립 (Elon Musk, Sam Altman 등)
    2018 : GPT-1 공개
    2019 : GPT-2 공개 (위험성 이유로 비공개 후 공개)
    2020 : GPT-3 공개 (175B 파라미터)
    2022.11 : ChatGPT 출시 (5일 만에 100만 유저)
    2023.03 : GPT-4 출시 (멀티모달)
    2023.11 : GPT-4 Turbo + GPTs 스토어
    2024.05 : GPT-4o 출시 (옴니모델)
    2024.09 : o1 출시 (추론 모델)
    2024.12 : Sora 영상 생성 공개
    2025 : GPT-5, o3 시리즈
    2026 : GPT-5.2 (400K 컨텍스트)
```

| 항목 | 내용 |
|------|------|
| **설립** | 2015년, 미국 샌프란시스코 |
| **창업자** | Sam Altman, Elon Musk(이후 이탈), Ilya Sutskever 등 |
| **기업 가치** | $157B (약 200조원, 2025년 기준) |
| **직원 수** | ~3,000명 |
| **주요 투자자** | Microsoft ($13B+) |
| **엔터프라이즈 점유율** | 27% (2026년, 과거 50%에서 하락) |

#### OpenAI 모델 라인업 (2026년 기준)

| 모델 | 용도 | 특징 | API 가격 (1M 토큰) |
|------|------|------|-------------------|
| **GPT-5.2** | 플래그십 | 400K 컨텍스트, 최강 범용 | 입력 $1.75 / 출력 $14 |
| **GPT-4o** | 범용 멀티모달 | 텍스트+이미지+음성 통합 | 입력 $2.50 / 출력 $10 |
| **GPT-4o mini** | 경량/저가 | 빠르고 저렴 | 입력 $0.15 / 출력 $0.60 |
| **o3 / o4-mini** | 추론 특화 | 수학, 코딩, 복잡한 추론 | 입력 $10 / 출력 $40 |
| **DALL-E 3** | 이미지 생성 | 텍스트 이해력 최고 | 이미지당 $0.04~ |
| **Sora** | 영상 생성 | 물리 법칙 이해 | Plus 요금에 포함 |
| **Whisper** | 음성→텍스트 | 다국어 음성 인식 | 분당 $0.006 |
| **TTS** | 텍스트→음성 | 자연스러운 음성 합성 | 1M 문자 $15 |

---

### Anthropic — 안전한 AI의 추구자

```mermaid
timeline
    title Anthropic 연혁
    2021 : 설립 (OpenAI 출신 Amodei 형제)
    2023 : Claude 1, Claude 2 (100K 컨텍스트)
    2024 : Claude 3 시리즈, Claude 3.5 Sonnet, MCP 공개
    2025 : Claude 3.7/4 시리즈, Claude Code 출시
    2026 : Claude 4.5 시리즈 (엔터프라이즈 1위)
```

| 항목 | 내용 |
|------|------|
| **설립** | 2021년, 미국 샌프란시스코 |
| **창업자** | Dario Amodei, Daniela Amodei (전 OpenAI VP) |
| **기업 가치** | $61.5B (약 80조원) |
| **철학** | "Constitutional AI" — AI 안전성을 최우선 |
| **엔터프라이즈 점유율** | 40% (2026년, 업계 1위) |
| **코딩 시장 점유율** | 54% (AI 코딩 분야 1위) |

#### Anthropic 모델 라인업

| 모델 | 용도 | 특징 | API 가격 (1M 토큰) |
|------|------|------|-------------------|
| **Claude 4.5 Opus** | 플래그십 | 최고 성능, 복잡한 작업 | 입력 $15 / 출력 $75 |
| **Claude 4.5 Sonnet** | 균형 | 성능과 비용의 최적 균형 | 입력 $3 / 출력 $15 |
| **Claude 4.5 Haiku** | 경량/저가 | 빠른 응답, 대량 처리 | 입력 $0.80 / 출력 $4 |

#### Anthropic의 차별점

```
1. Constitutional AI: 헌법적 AI - 스스로 윤리적 판단
2. 200K 컨텍스트: 약 15만 단어 = 500페이지 책 한 번에 처리
3. Claude Code: 터미널 기반 AI 코딩 도구 (100만 토큰)
4. MCP (Model Context Protocol): AI가 외부 도구를 사용하는 표준 프로토콜
5. 글쓰기 품질: 자연스러운 톤, 지시 따르기 최강
```

---

### Google DeepMind — 검색 거인의 AI

```mermaid
timeline
    title Google AI 연혁
    2017~2018 : Transformer 논문, BERT 공개
    2023~2024 : Gemini 1.0/1.5 Pro/Flash, 2.0 Flash
    2025 : Gemini 3 Pro/Flash
    2026 : Gemini 3 Ultra, Veo 3, Antigravity
```

| 항목 | 내용 |
|------|------|
| **조직** | Google DeepMind (Google Brain + DeepMind 합병) |
| **모회사** | Alphabet Inc. (시가총액 $2T+) |
| **강점** | 초대형 컨텍스트(1M+), Google 서비스 통합, 인프라 |
| **Transformer** | 트랜스포머 아키텍처의 원조 (2017년 논문) |

#### Google 모델 라인업

| 모델 | 용도 | 특징 | API 가격 (1M 토큰) |
|------|------|------|-------------------|
| **Gemini 3 Ultra** | 플래그십 | 최고 성능, 멀티모달 | 고가 |
| **Gemini 3 Pro** | 범용 | 균형 잡힌 성능 | 입력 $1.25 / 출력 $5 |
| **Gemini 3 Flash** | 경량/저가 | Pro급 성능에 4배 저렴 | 입력 $0.50 / 출력 $3 |

---

### Meta AI — 오픈소스의 챔피언

| 항목 | 내용 |
|------|------|
| **모델** | Llama 시리즈 (Llama 4 최신) |
| **철학** | 완전 오픈소스 — 누구나 무료로 사용/수정 가능 |
| **영향력** | 오픈소스 LLM 생태계의 사실상 표준 |
| **Llama 4** | 10M 컨텍스트, 무료, Mixture of Experts |
| **활용** | 기업 내부 배포, 커스텀 모델 학습의 베이스 |

### xAI — 일론 머스크의 AI

| 항목 | 내용 |
|------|------|
| **설립** | 2023년, Elon Musk |
| **모델** | Grok 시리즈 (Grok 4.1 최신) |
| **차별점** | X(트위터) 실시간 데이터 연동 |
| **특징** | 유머러스한 답변 스타일, 검열이 적음 |

### Mistral AI — 유럽의 희망

| 항목 | 내용 |
|------|------|
| **설립** | 2023년, 프랑스 파리 |
| **창업자** | 전 Meta/Google AI 연구자들 |
| **모델** | Mistral Large, Mixtral (MoE) |
| **차별점** | Mixture of Experts — 효율적 연산, 유럽 데이터 규제 준수 |

### DeepSeek — 중국의 파괴적 혁신

| 항목 | 내용 |
|------|------|
| **설립** | 2023년, 중국 항저우 |
| **모델** | DeepSeek V3, DeepSeek R1 |
| **충격** | GPT-4급 성능을 극소 비용으로 달성 (학습 비용 $5.6M) |
| **영향** | AI 칩 독점 구조에 의문 제기, 주가 충격 발생 |

---

## 3. 모델 성능 비교 (2026년 기준)

### 분야별 최강자

```mermaid
flowchart LR
    subgraph 분야별 ["분야별 최강 모델 (2026.04)"]
        direction TB
        A["코딩"] --> A1["Claude 4.5 Opus"]
        B["글쓰기"] --> B1["Claude 4.5 Opus"]
        C["수학/추론"] --> C1["o3 (OpenAI)"]
        D["범용 대화"] --> D1["GPT-5.2"]
        E["긴 문서"] --> E1["Gemini 3 (1M 컨텍스트)"]
        F["가성비"] --> F1["DeepSeek V3"]
        G["오픈소스"] --> G1["Llama 4"]
    end

    style A1 fill:#a29bfe,stroke:#6c5ce7,color:#fff
    style B1 fill:#a29bfe,stroke:#6c5ce7,color:#fff
    style C1 fill:#74b9ff,stroke:#0984e3,color:#fff
    style D1 fill:#74b9ff,stroke:#0984e3,color:#fff
    style E1 fill:#55efc4,stroke:#00b894,color:#2d3436
    style F1 fill:#fd79a8,stroke:#e84393,color:#fff
    style G1 fill:#74b9ff,stroke:#0984e3,color:#fff
```

### 가격 비교 (API, 1M 토큰 기준)

| 모델 | 입력 가격 | 출력 가격 | 비고 |
|------|----------|----------|------|
| GPT-4o mini | $0.15 | $0.60 | 가장 저렴한 프리미엄 |
| Gemini 3 Flash | $0.50 | $3.00 | 가성비 좋음 |
| Claude 4.5 Haiku | $0.80 | $4.00 | 빠르고 경량 |
| GPT-5.2 | $1.75 | $14.00 | 플래그십 |
| Claude 4.5 Sonnet | $3.00 | $15.00 | 균형 |
| Claude 4.5 Opus | $15.00 | $75.00 | 최고 성능 |

### 구독 서비스 가격 비교

| 서비스 | 무료 | 기본 유료 | 프리미엄 |
|--------|------|----------|----------|
| **ChatGPT** | GPT-5.2 제한적 | Go $8/월 · Plus $20/월 | Pro $200/월 |
| **Claude** | 일일 제한 | Pro $20/월 | Max $100~200/월 |
| **Gemini** | 제한적 | AI Pro $20/월 | Ultra $250/월 |

---

## 4. 모델 선택 가이드

```mermaid
flowchart LR
    Q{"어떤 상황?"}

    Q -->|"처음 시작"| A["ChatGPT 무료<br/>→ 가장 범용적이고 쉬움"]
    Q -->|"글쓰기/보고서"| B["Claude Pro<br/>→ 자연스러운 톤, 긴 문서 처리"]
    Q -->|"코딩/개발"| C["Claude (Code)<br/>→ 코딩 분야 1위"]
    Q -->|"Google 연동"| D["Gemini<br/>→ Gmail, Docs, Drive 통합"]
    Q -->|"검색+답변"| E["Perplexity<br/>→ 출처 표시, 최신 정보"]
    Q -->|"예산 절약"| F["DeepSeek / Gemini Flash<br/>→ 가성비 최강"]
    Q -->|"자체 서버 운영"| G["Llama 4 (오픈소스)<br/>→ 무료, 커스터마이징 가능"]

    style A fill:#74b9ff,stroke:#0984e3,color:#fff
    style B fill:#a29bfe,stroke:#6c5ce7,color:#fff
    style C fill:#a29bfe,stroke:#6c5ce7,color:#fff
    style D fill:#55efc4,stroke:#00b894,color:#2d3436
```

---

## 참고 자료

- [Ranking the Top LLMs in 2026 (Whistler Billboards)](https://www.whistlerbillboards.com/friday-feature/top-llms-2026/)
- [10 Best LLMs of April 2026 (Azumo)](https://azumo.com/artificial-intelligence/ai-insights/top-10-llms-0625)
- [Top AI Models in 2026 (Bracai)](https://www.bracai.eu/post/top-ai-models-in-2026-which-is-the-best-llm)
- [LLM Model Evolution 2024-2026 — 244 Models (llm-evolution.com)](https://www.llm-evolution.com/)
- [AI Model Providers Landscape (Stackviv)](https://stackviv.ai/blog/ai-model-providers-landscape)
- [LLM Models 비교 (Mehmet Ozkaya, Medium)](https://mehmetozkaya.medium.com/llm-models-openai-chatgpt-meta-llama-anthropic-claude-google-gemini-mistral-ai-and-xai-grok-bd35779704c2)
