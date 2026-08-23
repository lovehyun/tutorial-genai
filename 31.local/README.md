# 31.local — 로컬에서 생성형 AI 모델 실행/커스터마이즈

API 키 없이 **내 컴퓨터에서** 모델을 돌린다 — 구조 이해(transformers) → 직접 파인튜닝/경량화 →
HuggingFace 생태계 활용 → 특정 모델 계열(Mistral/Llama) → GPT4All(대안 런타임) →
Ollama(지금 시대의 사실상 표준 로컬 런타임, 그래서 번호도 맨 뒤) 순으로 쌓는다.

## 디렉토리 구조

| 폴더 | 내용 |
|---|---|
| [`1.transformers/`](1.transformers/) | 토큰화→hidden state→인코더/디코더→디코딩전략→어텐션까지 내부 구조 단계별 실행 |
| [`2.mymodel/`](2.mymodel/) | `1.finetune/`(직접 분류기 파인튜닝) · `2.compression/`(양자화·레이어축소·프루닝·어휘축소·증류) · `3.lora/`(LoRA) |
| [`3.huggingface/`](3.huggingface/) | `1.pipelines/`(태스크별 `pipeline()`) · `2.local_llm/`(GPT-Neo 로컬 서빙) · `3.image_gen/`(Stable Diffusion) |
| [`4.mistral/`](4.mistral/) | Mistral 7B Instruct 로드·LangChain 연동·Flask 서빙 |
| [`5.llama/`](5.llama/) | Llama 아키텍처(TinyLlama) 로드·생성 |
| [`6.gpt4all/`](6.gpt4all/) | GGUF 기반 대안 로컬 런타임 |
| `7~9` | *(예약)* |
| [`10.ollama/`](10.ollama/) | **사실상 표준 로컬 런타임** — REST→SDK→LangChain(호출 방식) + Modelfile 커스터마이즈 + Qwen/EXAONE(모델별 한국어 태스크) + OpenAI 호환 엔드포인트 |

## 로컬 모델 선택 가이드 (2026-08 기준)

| 모델 계열 | 크기 | 요구 VRAM(GPU 기준) | 이 저장소에서 |
|---|---|---|---|
| **Llama** | 1B~405B(버전별 상이) | 1B급은 CPU도 가능, 8B+는 GPU 8GB+ 권장 | `5.llama/`(TinyLlama, CPU 실습용) |
| **Mistral 7B** | 7B | GPU 8GB+ 권장, CPU는 매우 느림 | `4.mistral/` |
| **Qwen 2.5** | 0.5B~72B(버전별) | 1.5B~7B는 CPU도 실용적 | `10.ollama/5.qwen/` |
| **EXAONE 3.5** | 2.4B~32B(버전별) | 2.4B~7.8B는 CPU도 가능 | `10.ollama/6.exaone/` |
| **GPT-Neo** | 125M~2.7B | CPU 가능(작은 버전 기준) | `3.huggingface/2.local_llm/` |

> **VRAM/속도가 걱정되면 Ollama부터**(`10.ollama/`) — GGUF로 양자화된 모델을 CPU에서도 합리적인
> 속도로 돌린다. `4.mistral/`·`5.llama/`처럼 `transformers`로 직접 로드하는 예제는 원본 가중치라
> 용량·속도 부담이 더 크다(단, "내부에서 무슨 일이 일어나는지" 보기엔 이쪽이 낫다).

## 환경 세팅
```bash
pip install torch transformers accelerate sentencepiece
```
GPU가 없어도(이 저장소 개발 환경도 CPU-only) `1.transformers/`, `5.llama/`(TinyLlama), `10.ollama/`
전체는 실습 가능하다. `4.mistral/`(7B), `3.huggingface/3.image_gen/`(Stable Diffusion)은 GPU가
있어야 실용적인 속도가 나온다.

## 결론: 어떤 걸 먼저 볼까
- **원리부터 이해하고 싶다면** → `1.transformers/`
- **내 모델을 직접 학습/경량화하고 싶다면** → `2.mymodel/`
- **일단 뭔가를 로컬에서 빨리 돌려보고 싶다면(CPU도 OK)** → `10.ollama/`
- **파인튜닝 없이 프롬프트만으로 한국어 태스크를 처리하고 싶다면** → `10.ollama/5.qwen/` 또는 `10.ollama/6.exaone/`
