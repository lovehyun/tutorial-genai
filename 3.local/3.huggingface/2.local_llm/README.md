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

## 실행
```bash
pip install transformers torch accelerate
# API 예제: HUGGINGFACEHUB_API_TOKEN 을 .env 에 (HF_CLI.md 참고)
# 서빙 예제: pip install flask fastapi uvicorn
```
