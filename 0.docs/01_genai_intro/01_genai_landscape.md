# 생성형 AI 전체 지형도

> 텍스트, 이미지, 음악, 영상, 코드 — 생성형 AI가 만들 수 있는 모든 것

---

## 1. 생성형 AI 분류 체계

```mermaid
flowchart LR
    GenAI["생성형 AI<br/>(Generative AI)"]

    GenAI --> T["📝 텍스트 생성"]
    GenAI --> I["🖼️ 이미지 생성"]
    GenAI --> A["🎵 음악/오디오 생성"]
    GenAI --> V["🎬 영상/비디오 생성"]
    GenAI --> C["💻 코드 생성"]
    GenAI --> D["🗣️ 음성/TTS"]
    GenAI --> P["📊 프레젠테이션"]
    GenAI --> M["🧬 기타 (3D, 분자, 게임 등)"]

    T --> T1["ChatGPT · Claude · Gemini"]
    I --> I1["Midjourney · DALL-E · Stable Diffusion"]
    A --> A1["Suno · Udio · AIVA"]
    V --> V1["Sora · Runway · Veo · Kling"]
    C --> C1["Cursor · Claude Code · Copilot"]
    D --> D1["ElevenLabs · VITS · Bark"]
    P --> P1["Gamma · Beautiful.ai · Tome"]
    M --> M1["Meshy(3D) · AlphaFold(단백질)"]

    style GenAI fill:#e17055,stroke:#d63031,color:#fff
    style T fill:#74b9ff,stroke:#0984e3,color:#fff
    style I fill:#fd79a8,stroke:#e84393,color:#fff
    style A fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style V fill:#a29bfe,stroke:#6c5ce7,color:#fff
    style C fill:#55efc4,stroke:#00b894,color:#2d3436
    style D fill:#fab1a0,stroke:#e17055,color:#2d3436
    style P fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

---

## 2. 텍스트 생성 AI (LLM 챗봇)

### 일상에서 쓰는 AI 챗봇

| 서비스 | 회사 | 무료 | 유료 | 특징 |
|--------|------|------|------|------|
| **ChatGPT** | OpenAI | O | $20/월~ | 가장 범용적, 도구 생태계 최대 |
| **Claude** | Anthropic | O | $20/월~ | 글쓰기 최강, 긴 문서 처리, 코딩 |
| **Gemini** | Google | O | $20/월~ | Google 연동, 초대형 컨텍스트(1M+) |
| **Grok** | xAI (Elon Musk) | O | X 프리미엄 | X(트위터) 실시간 데이터 연동 |
| **Perplexity** | Perplexity AI | O | $20/월 | AI 검색 엔진 (출처 표시 특화) |
| **Copilot** | Microsoft | O | $20/월 | Bing 검색 + Office 연동 |

### 텍스트 AI로 할 수 있는 일

```
- 글쓰기: 이메일, 보고서, 블로그, 소설
- 요약: 긴 문서/논문을 핵심만 추출
- 번역: 다국어 번역 (뉘앙스까지 반영)
- 분석: 데이터 해석, 비교 분석
- 코딩: 프로그램 작성, 디버깅, 설명
- 학습: 개념 설명, 퀴즈 출제, 과외
- 브레인스토밍: 아이디어 발상, 기획
```

---

## 3. 이미지 생성 AI

### 주요 도구

```mermaid
flowchart LR
    subgraph 유료 ["유료/프리미엄"]
        MJ["Midjourney<br/>──────<br/>최고 품질 이미지<br/>예술적 스타일<br/>Discord 기반<br/>$10/월~"]
        DE["DALL-E 3<br/>(ChatGPT 내장)<br/>──────<br/>텍스트 이해력 최고<br/>ChatGPT와 통합<br/>사용 편의성"]
    end

    subgraph 무료 ["무료/오픈소스"]
        SD["Stable Diffusion<br/>──────<br/>오픈소스/무료<br/>로컬 실행 가능<br/>커스터마이징 자유"]
        FL["Flux<br/>──────<br/>Black Forest Labs<br/>고품질 오픈소스<br/>빠른 생성 속도"]
    end

    subgraph 특화 ["특화 도구"]
        CN["Canva AI<br/>──────<br/>디자인 특화<br/>템플릿 + AI 생성<br/>비디자이너 친화"]
        ID["Ideogram<br/>──────<br/>텍스트 렌더링 특화<br/>로고/포스터에 강함"]
    end

    style MJ fill:#fd79a8,stroke:#e84393,color:#fff
    style DE fill:#74b9ff,stroke:#0984e3,color:#fff
    style SD fill:#55efc4,stroke:#00b894,color:#2d3436
    style FL fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

### 이미지 AI 활용 사례

```
- 블로그/SNS 썸네일 제작
- 프레젠테이션 삽화
- 캐릭터/로고 디자인 초안
- 제품 목업(Mockup) 생성
- 웹툰/만화 소재
- 인테리어/패션 시뮬레이션
```

---

## 4. 음악/오디오 생성 AI

### 주요 도구

| 서비스 | 특징 | 가격 | 사용 예 |
|--------|------|------|---------|
| **Suno** | 가사+멜로디+보컬 자동 생성, v5 최신 | 무료(제한)/유료 $10/월~ | "신나는 K-pop 스타일 노래 만들어줘" |
| **Udio** | 고품질 음악 생성, 장르 다양 | 무료(제한)/유료 | 배경음악, 광고 음악 |
| **AIVA** | AI 작곡가, 클래식/영화음악 특화 | 무료/유료 | 게임 BGM, 영화 OST |
| **Boomy** | 초간단 음악 생성, 스트리밍 배포 가능 | 무료 | Spotify에 AI 음악 업로드 |
| **ElevenLabs** | 음성 합성/복제 최강 | 무료(제한)/유료 | 나레이션, 더빙, TTS |
| **Bark** | 오픈소스 음성 생성 | 무료 | 다국어 음성, 효과음 |

### 음악 AI로 할 수 있는 일

```
- 유튜브 배경음악 (저작권 걱정 없음)
- 팟캐스트 인트로/아웃트로
- 프레젠테이션 배경음악
- 개인 노래 작곡 (가사 포함)
- 오디오북 나레이션 (TTS)
- 다국어 더빙
```

---

## 5. 영상/비디오 생성 AI

### 주요 도구

```mermaid
flowchart LR
    subgraph 텍스트투비디오 ["텍스트 → 비디오"]
        direction TB
        S["Sora (OpenAI)<br/>──────<br/>최고 품질<br/>물리 법칙 이해<br/>$20/월 (Plus)"]
        VEO["Veo 2/3 (Google)<br/>──────<br/>8K 지원<br/>카메라 워크 이해<br/>Gemini 통합"]
        KL["Kling (Kuaishou)<br/>──────<br/>중국 AI<br/>5분 이상 영상<br/>무료 사용 가능"]
    end

    subgraph 편집특화 ["영상 편집 + AI"]
        RW["Runway Gen-3<br/>──────<br/>프로 영상 편집<br/>AI + 기존 편집 통합<br/>영화 제작에 사용"]
        PI["Pika<br/>──────<br/>간편한 영상 생성<br/>이미지→영상 변환<br/>쉬운 UI"]
    end

    subgraph 아바타 ["AI 아바타"]
        SY["Synthesia<br/>──────<br/>AI 발표자 영상<br/>다국어 지원<br/>기업 교육/광고"]
        HG["HeyGen<br/>──────<br/>아바타 + 음성<br/>얼굴 교체<br/>마케팅 영상"]
    end

    style S fill:#a29bfe,stroke:#6c5ce7,color:#fff
    style VEO fill:#55efc4,stroke:#00b894,color:#2d3436
    style RW fill:#fdcb6e,stroke:#f39c12,color:#2d3436
```

### 영상 AI 활용 사례

```
- 유튜브 쇼츠/릴스 콘텐츠 제작
- 제품 소개 영상
- 교육/강의 영상 (AI 아바타)
- 마케팅/광고 영상
- 뮤직비디오
- 소셜 미디어 콘텐츠
```

---

## 6. 프레젠테이션/문서 AI

| 서비스 | 특징 | 활용 |
|--------|------|------|
| **Gamma** | 텍스트만 입력하면 PPT 자동 생성 | 발표 자료, 보고서 |
| **Beautiful.ai** | 디자인 자동 조정, 템플릿 풍부 | 비즈니스 프레젠테이션 |
| **Tome** | AI 스토리텔링 특화 | 기획서, 제안서 |
| **Canva AI** | 디자인+AI 통합 | 포스터, SNS, PPT |
| **Notion AI** | 문서 작성/요약/번역 AI | 업무 문서, 위키 |
| **Napkin AI** | 텍스트를 다이어그램으로 변환 | 개념 설명, 프로세스 도식화 |

---

## 7. 일상에서 쓸 수 있는 AI 도구 총정리

```mermaid
flowchart LR
    subgraph 업무 ["💼 업무 생산성"]
        direction TB
        W1["이메일 작성 → ChatGPT/Claude"]
        W2["회의록 요약 → Claude/Gemini"]
        W3["번역 → DeepL/Claude"]
        W4["PPT 제작 → Gamma"]
        W5["엑셀 수식 → ChatGPT"]
    end

    subgraph 창작 ["🎨 콘텐츠 창작"]
        direction TB
        C1["블로그 글 → ChatGPT/Claude"]
        C2["썸네일 → Midjourney/DALL-E"]
        C3["배경음악 → Suno"]
        C4["영상 제작 → Runway/Sora"]
        C5["SNS 콘텐츠 → Canva AI"]
    end

    subgraph 학습 ["📚 학습/연구"]
        direction TB
        L1["개념 설명 → ChatGPT/Claude"]
        L2["논문 요약 → Perplexity"]
        L3["언어 학습 → ChatGPT Voice"]
        L4["코딩 학습 → Claude Code"]
    end

    subgraph 생활 ["🏠 일상 생활"]
        direction TB
        H1["요리 레시피 → ChatGPT"]
        H2["여행 계획 → Gemini"]
        H3["운동 루틴 → ChatGPT"]
        H4["이미지 편집 → Canva AI"]
    end

    style 업무 fill:#74b9ff11,stroke:#0984e3
    style 창작 fill:#fd79a811,stroke:#e84393
    style 학습 fill:#55efc411,stroke:#00b894
    style 생활 fill:#fdcb6e11,stroke:#f39c12
```

---

## 8. 생성형 AI 시장 규모

```
2024년: 약 670억 달러
2025년: 약 1,036억 달러 (전년 대비 +55%)
2026년: 약 1,610억 달러 (전망)
2030년: 약 1조 달러 (전망)
```

생성형 AI는 인터넷, 스마트폰에 이어 **제3의 기술 혁명** 으로 불리며, 모든 산업에 걸쳐 변화를 가속화하고 있습니다.

---

## 참고 자료

- [2025년 주목해야 할 생성형 AI 사이트 총정리 (링커리어)](https://community.linkareer.com/jayuu/4168236)
- [프롬프트 생성을 위한 최고의 AI - 2026 (Jenova)](https://www.jenova.ai/ko/resources/best-ai-for-prompt-generation)
- [Suno AI (나무위키)](https://namu.wiki/w/Suno)
- [Ranking the Top LLMs in 2026 (Whistler Billboards)](https://www.whistlerbillboards.com/friday-feature/top-llms-2026/)
- [10 Best LLMs of April 2026 (Azumo)](https://azumo.com/artificial-intelligence/ai-insights/top-10-llms-0625)
