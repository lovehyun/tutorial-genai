# 2.local_llm — 생성형 LLM (API 호출 → 로컬 실행 → 서빙)

큰 생성 모델을 두 갈래로 다룹니다: **(1) HF 서버에 요청(API)** vs **(2) 내 머신에서 직접 실행**.
그리고 로컬 모델을 **웹 API 로 서빙**하는 단계까지 발전합니다.

## 학습 순서

| 파일 | 내용 | 비용/자원 |
|---|---|---|
| `1.1_inference_api.py` | HF Inference API 로 gpt2/Mistral 호출 (HTTP) | 💳 크레딧 차감, 토큰 필요 |
| `1.2_inference_client.py` | `InferenceClient` 로 Mistral 호출 | 💳 크레딧 차감 |
| `2.1_gpt_neo_basic.py` | GPT-Neo 2.7B **로컬** 텍스트 생성 | ✅ 무료, ⚠️ ~10GB·GPU 권장 |
| `2.2_langchain.py` | GPT-Neo 를 LangChain 파이프라인으로 | ✅ 무료 |
| `2.3_prompt.py` | 프롬프트 템플릿 + 생성 파라미터(top_k/p 등) | ✅ 무료 |
| `2.4_flask.py` | GPT-Neo 생성을 Flask REST API 로 서빙 | ✅ 무료 |
| `2.5_fastapi.py` | 같은 서빙을 FastAPI(async)로 | ✅ 무료 |

## 핵심
- **1.x = API(서버가 추론, 크레딧 차감)** vs **2.x = 로컬(내 GPU, 무료)** — 차이를 먼저 이해.
  (비용/정책은 상위 [README](../README.md) "유료/무료 정책" 참고)
- GPT-Neo 2.7B 는 다운로드 ~10GB + 추론에 GPU 가 사실상 필요. CPU 는 매우 느림.
- 2.4/2.5 는 같은 모델을 Flask vs FastAPI 로 서빙 — 프레임워크만 다른 비교.

## 주요 오픈 LLM 계보 (누가 / 무엇 기반으로 만들었나)

대부분 **트랜스포머 '디코더'** 구조를 공유하고, 차이는 학습 데이터·크기·라이선스·튜닝에 있습니다.
(이 레포 곳곳에서 쓰는 모델들 — `4.mistral`, `5.llama`, `8.korean_llm`, `2.langchain/.../local_model` 참고)

| 모델 패밀리 | 만든 곳 | 구조/베이스 · 특징 | 라이선스 | 레포 내 예제 |
|---|---|---|---|---|
| **Llama 2 / 3 / 3.1 / 3.2** | Meta | 디코더, 오픈 가중치의 사실상 표준·생태계 최대 | 커뮤니티(제약) · gated | `5.llama` |
| **Mistral 7B / Mixtral 8x7B** | Mistral AI (프랑스) | Mixtral은 **MoE**(전문가 혼합), 효율↑ | Apache-2.0 | `4.mistral` |
| **Gemma / Gemma 2** | Google DeepMind | Gemini 기술 기반 경량 오픈모델(`-it`) | Gemma 라이선스 · gated | (언급만) |
| **Qwen 2.5 / Qwen3** | Alibaba (중국) | 다국어(한국어 포함) 강함 | Apache-2.0 | `8.korean_llm`, `2.langchain` |
| **Phi-2 / Phi-3 / Phi-3.5** | Microsoft | 소형 고품질("SLM"), 영어 강함 | MIT | `2.langchain` |
| **GPT-Neo / GPT-J / GPT-NeoX** | EleutherAI | GPT-3 오픈 재현(초기 오픈 LLM) | 오픈 | **이 폴더 2.x** |
| **DeepSeek V2/V3 / R1** | DeepSeek (중국) | MoE, **R1은 추론(reasoning) 특화** | 오픈(MIT 등) | (없음 — 추가 후보) |
| **Falcon 7B / 40B** | TII (UAE) | 한때 상위권 오픈모델 | Apache-2.0 | (옛 README 언급) |
| **Command R / R+** | Cohere | RAG·도구사용 특화 | 연구용 | (없음) |
| **EXAONE 3.5** | LG AI Research (한국) | 한국어 강함 | 비상업 · gated | `8.korean_llm` |
| **GPT-2 / BERT / DistilBERT** | OpenAI / Google / HuggingFace | (생성/이해 기초 모델) | 오픈 | `1.pipelines`, `1.transformers` |

> **well-known 중 레포에 빠진 것**: **DeepSeek**(2025~2026 화제, 특히 R1 추론), **Gemma**(언급만 있고 예제 없음),
> **Command R**(RAG 특화), Falcon(옛 README에만). 필요하면 예제로 추가 가능.

## 실행
```bash
pip install transformers torch accelerate
# API 예제: HUGGINGFACEHUB_API_TOKEN 을 .env 에 (HF_CLI.md 참고)
# 서빙 예제: pip install flask fastapi uvicorn
```
