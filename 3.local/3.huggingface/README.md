# 3.huggingface — HuggingFace 모델 활용

HuggingFace 생태계로 **세 가지 영역**의 모델을 다룹니다. 영역별로 하위 폴더가 나뉘며,
각 폴더는 기초 → 응용 순서입니다.

```
3.huggingface/
├── 1.pipelines/    NLP 태스크 — pipeline() 한 줄로 감정/QA/NER/생성
├── 2.local_llm/    큰 생성 모델 — Inference API + GPT-Neo 로컬 실행·서빙
├── 3.image_gen/    이미지 생성 — Stable Diffusion (API / 로컬 / 서버)
└── HF_CLI.md       (참고) huggingface-cli 로그인·업로드·캐시 관리
```

## 영역별 요약

| 폴더 | 무엇을 | 모델 크기 | 실행 환경 |
|---|---|---|---|
| [1.pipelines](1.pipelines/) | NLP 태스크 입문 (감정/QA/NER/생성/다국어) | 작음(수백 MB) | CPU 가능 |
| [2.local_llm](2.local_llm/) | 생성형 LLM — API 호출 → GPT-Neo 로컬 → Flask/FastAPI 서빙 | 큼(GPT-Neo ~10GB) | GPU 권장 |
| [3.image_gen](3.image_gen/) | Stable Diffusion 이미지 생성 | 큼(수 GB) | GPU 강력 권장 |

## 학습 순서 제안

```
1.pipelines (가장 쉬움, CPU) → 2.local_llm (생성 LLM) → 3.image_gen (이미지, GPU)
```

- 처음이면 **1.pipelines** 부터 — 작은 모델로 NLP 태스크 감을 잡습니다.
- 모델 캐시 위치/다운로드, CLI 로그인은 `HF_CLI.md` 참고.
- 각 하위 폴더의 `README.md` 에 파일별 설명이 있습니다.

## HuggingFace 모델 찾기 & 고르기

### 1) 어디서, 어떻게 찾나
- **모델 허브**: <https://huggingface.co/models> — 왼쪽 필터로 좁힌다.
  - **Task**(태스크): `Text Classification`, `Question Answering`, `Token Classification`,
    `Text Generation`, `Text-to-Image` … 내가 할 일에 맞는 태그를 먼저 고른다.
  - **Languages**: `korean` 등 — 한국어 데이터면 한국어/다국어 모델로 좁힌다.
  - **Libraries**: `Transformers`, `Diffusers`, `sentence-transformers` …
  - **License**: 상업적 사용이 필요하면 `apache-2.0` / `mit` 등으로 필터.
- **정렬**: `Trending`(요즘 뜨는) / `Most downloads`(검증된) / `Most likes`. 처음엔 다운로드 많은 걸 고르면 안전.

### 2) 모델 카드(Model Card)에서 꼭 볼 것
모델 페이지의 설명 = 모델 카드. 다음을 확인:
- **용도(intended use)** 와 **학습 데이터** — 내 도메인/언어와 맞는가
- **라이선스** — 상업적 사용 가능? 비상업(연구용)? (예: 일부 한국어 모델은 비상업)
- **크기/파라미터 수** 와 **요구 VRAM** — 내 GPU(또는 CPU)로 돌아가는가
- **Files and versions** 탭 — 실제 가중치 파일 포맷(`.safetensors`/`.bin`/`.gguf`)과 용량
- **사용 예시 코드** — `from_pretrained` 한 줄로 되는지, `trust_remote_code` 필요한지

### 3) 모델 이름 규칙 (이름만 봐도 성격이 보인다)
- `-base` / `-large` : 모델 크기(작음/큼). 클수록 성능↑ 자원↑
- `-instruct` / `-chat` / `-it` : 지시·대화로 파인튜닝된 모델 (그냥 base 는 이어쓰기 전용)
- `-uncased` / `-cased` : 대소문자 구분 여부 (BERT 계열)
- 양자화 표기 `GGUF` / `GPTQ` / `AWQ` / `Q4_K_M` / `fp16` : 경량/저VRAM 버전 (llama.cpp·ollama 등에서 사용)
- 언어 접두 `ko-`, `multilingual`, `KR-` : 언어 특화/다국어

### 4) 반드시 알아야 할 것
- **Task ↔ AutoModel 클래스 짝**: 태스크마다 로드 클래스가 다르다.

  | 태스크 | 클래스 | pipeline task |
  |---|---|---|
  | 텍스트 생성 | `AutoModelForCausalLM` | `text-generation` |
  | 문장 분류/감정 | `AutoModelForSequenceClassification` | `text-classification` |
  | 개체명(NER) | `AutoModelForTokenClassification` | `ner` |
  | 질의응답 | `AutoModelForQuestionAnswering` | `question-answering` |
  | 빈칸채우기 | `AutoModelForMaskedLM` | `fill-mask` |
  | 번역/요약 | `AutoModelForSeq2SeqLM` | `translation`/`summarization` |
  | 임베딩(본체만) | `AutoModel` | `feature-extraction` |

- **토크나이저와 모델은 같은 이름으로 짝** 지어 로드한다 (`AutoTokenizer`/`AutoModel*` 같은 `model_id`).
- **Gated(접근 제한) 모델**: Llama·Mistral·Gemma 등은 페이지에서 **라이선스 동의 + 로그인** 필요.
  → `huggingface-cli login` (자세히는 [HF_CLI.md](HF_CLI.md)).
- **다운로드/캐시**: `from_pretrained` 가 처음 호출 시 `~/.cache/huggingface` 에 자동 저장.
  재실행은 캐시 사용(오프라인은 `local_files_only=True`). 특정 버전은 `revision="..."`.
- **NER/QA 등은 '파인튜닝된' 모델을 써야 한다** — 분류 헤드 없는 base 모델은 결과가 무의미
  (이 폴더 `1.pipelines/1.3_ner.py` 가 그 예: 전용 NER 모델 사용).

## HuggingFace 유료 / 무료 정책

핵심 한 줄: **모델을 받아 "내 컴퓨터에서 돌리는 것"은 무료**, **HF 서버가 "대신 추론해 주는 것"은 과금**.

### ✅ 무료 (이 폴더의 로컬 예제 대부분)
- **모델·데이터셋 다운로드 + 로컬 실행**: `from_pretrained` 로 받아 내 CPU/GPU 에서 돌리는 건 무료.
  드는 비용은 **내 하드웨어/전기**뿐. → `1.pipelines/*`, `2.local_llm/2.*`(GPT-Neo), `3.image_gen/2.*`(로컬 SD)
- **Hub 계정 / 공개·비공개 저장소**: 개인은 무료로 모델·데이터셋 호스팅.
- **라이브러리**(transformers·diffusers·datasets 등): 전부 오픈소스, 무료.

### 💳 유료 / 한도 (HF 서버가 추론을 대신해 줄 때)
- **Inference Providers (구 Serverless Inference API)**: HF 서버에 요청해 결과만 받는 방식.
  **월 무료 크레딧** 이 있고 초과하면 과금/구독 필요. → `2.local_llm/1.1_inference_api.py`,
  `2.local_llm/1.2_inference_client.py`, `3.image_gen/1.1_api.py`, `1.2_inference_client.py` 가 이 방식
  (호출할 때마다 **크레딧 차감**).
- **PRO 구독**(개인 월정액): inference 크레딧 확대, ZeroGPU, 빠른 다운로드 등.
- **Inference Endpoints**(전용 배포): 프로덕션용 전용 인스턴스를 **시간당 과금**.
- **Spaces**: CPU 는 무료, **GPU 하드웨어는 시간당 유료**.
- **Enterprise Hub**: 조직/팀용 유료 플랜.

> ⚠️ 정확한 금액·무료 크레딧 한도는 자주 바뀝니다 → 공식 <https://huggingface.co/pricing> 확인.
> 비용 걱정 없이 배우려면 **로컬 실행 예제(2.\*)** 위주로, API 예제(1.\*)는 토큰·크레딧을 확인하고 사용하세요.

### gated(접근 제한) 모델은 '유료'가 아니다
Llama·Mistral·Gemma 등은 **무료지만** 라이선스 동의 + 로그인이 필요할 뿐. 동의하면 무료로 다운로드·로컬 실행 가능.

## 설치

```bash
pip install transformers torch                 # 공통
pip install langchain langchain-huggingface     # 일부 예제(langchain 통합)
pip install diffusers flask fastapi uvicorn     # 이미지/서빙 예제
```
