# 모델 최적화 & MLOps

## 과정 정보
- **기간**: 2일 (총 16시간)
- **난이도**: 고급
- **대상**: 로컬 LLM 실행 경험이 있고 모델 내부 구조와 경량화 기법을 학습하려는 개발자
- **선수 과목**: 입문 5. 로컬 LLM 빠르게 시작하기

## 학습 목표
1. Transformer 내부 구조(토큰화, 어텐션, BERT)를 시각화하며 이해할 수 있다
2. 양자화, 가지치기, 어휘 축소, 지식증류 등 모델 경량화 기법을 실습할 수 있다
3. 경량화된 모델을 학습시키고 Flask/FastAPI로 배포할 수 있다

## 커리큘럼

### Day 1: Transformer 내부 구조 심화

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | 모델 최적화의 필요성, 과정 개요 |
| 09:30-10:00 | Transformer 모델 로드 | `30.study/1.transformer/1.model_load.py` | Transformer 모델 구조 탐색 |
| 10:00-10:30 | Transformer 질의 | `30.study/1.transformer/2.model_query.py` | 모델에 질의하며 내부 동작 확인 |
| 10:45-11:15 | 토큰화 이론 | `31.local/1.transformers/1.1_tokenizer_basics.py`, `31.local/1.transformers/1.2_special_tokens.py` | 토큰화 과정, 특수 토큰/attention_mask |
| 11:15-12:00 | 토크나이저 비교 | `30.study/5.tokenizer/1.tokenizer_compare.py`, `30.study/5.tokenizer/2.korean_tokenizer.py` | 다양한 토크나이저 성능 비교, 한국어 토크나이저 |
| 13:00-13:30 | 어텐션 시각화 | `31.local/1.transformers/5.1_attention.py`, `31.local/1.transformers/5.2_headwise_attention.py` | Self-Attention 메커니즘 시각화 |
| 13:30-14:00 | 어텐션 심화 시각화 | `30.study/7.attention/1.attention_visualize.py`, `30.study/7.attention/2.qkv_visualize.py` | Q, K, V 벡터 시각화 |
| 14:00-14:30 | BERT 기초 | `30.study/2.bert/1.intro_bert.py` | BERT 모델 구조 이해 |
| 14:45-15:15 | BERT 파인튜닝 (감성분석) | `30.study/2.bert/2.finetune_imdb_sentiment.py`, `30.study/2.bert/3.finetune_imdb_load.py` | IMDB 감성분석 파인튜닝 |
| 15:15-15:45 | BERT 파인튜닝 (뉴스분류) | `30.study/2.bert/2.finetune_agnews_category.py`, `30.study/2.bert/3.finetune_agnews_load.py` | AG News 카테고리 분류 |
| 15:45-16:15 | BERT REST API | `30.study/2.bert/4.restapi_agnews.py`, `30.study/2.bert/4.restapi_imdb.py` | 파인튜닝 모델 API 서빙 |
| 16:15-17:00 | 한국어 NLP 기초 | `30.study/4.korean_nlp/1.morpheme.py`, `30.study/4.korean_nlp/2.preprocessing.py` | 형태소 분석, 전처리, Day 1 정리 |

### Day 2: 모델 경량화와 배포

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 1 복습 | — | Transformer 내부 구조 복습 |
| 09:30-10:00 | 모델 학습 (기초) | `31.local/2.mymodel/1.finetune/1.1_train.py` | 커스텀 모델 학습 기초 |
| 10:00-10:30 | 모델 학습 (한국어 · 실전) | `31.local/2.mymodel/1.finetune/1.3_train_korean.py`, `31.local/2.mymodel/1.finetune/1.4_train_nsmc.py` | 한국어 모델 학습(KcBERT), 실전 데이터셋(NSMC)으로 확장 |
| 10:45-11:15 | 모델 추론 & LoRA | `31.local/2.mymodel/1.finetune/1.2_predict.py`, `31.local/2.mymodel/3.lora/1.lora_vs_full.py` | 학습된 모델로 추론, 전체 파인튜닝 대신 LoRA로 가볍게 |
| 11:15-12:00 | 양자화 | `31.local/2.mymodel/2.compression/2.1_quantization.py` | 모델 동적 양자화, 크기 비교 |
| 13:00-13:30 | 레이어 축소 | `31.local/2.mymodel/2.compression/2.2_layer_reduction.py` | 레이어 수 줄이기로 경량화 |
| 13:30-14:00 | 가지치기 (Pruning) | `31.local/2.mymodel/2.compression/2.3_pruning.py` | 불필요한 가중치 제거 |
| 14:00-14:30 | 어휘 축소 & 지식증류 | `31.local/2.mymodel/2.compression/2.4_vocab_reduction.py`, `31.local/2.mymodel/2.compression/2.5_distillation.py` | 어휘 크기 줄이기, 큰 모델의 지식을 작은 모델로 |
| 14:45-15:15 | HuggingFace Hub 배포 | `31.local/3.huggingface/HF_CLI.md` | CLI 로그인, 모델 업로드, 캐시 관리 |
| 15:15-15:45 | Flask/FastAPI 서빙 | `31.local/3.huggingface/2.local_llm/2.4_flask.py`, `31.local/3.huggingface/2.local_llm/2.5_fastapi.py` | Flask/FastAPI 모델 서빙 |
| 15:45-17:00 | 종합 프로젝트 & 발표 | — | 모델 경량화 → 배포 파이프라인 구축, 결과 발표 |

## 환경 설정

```bash
pip install transformers torch datasets flask fastapi uvicorn matplotlib
```

## 이론 교안

| 교안 | 내용 |
|------|------|
| `0.docs/05_genai_advanced/15_model_optimization.md` | 모델 최적화 (양자화, 가지치기, 지식증류) |
| `0.docs/05_genai_advanced/13_huggingface_local.md` | 로컬 LLM 활용 (양자화, GGUF 포맷) |
| `0.docs/05_genai_advanced/14_finetuning_lora.md` | LoRA 파인튜닝 |
| `0.docs/05_genai_advanced/17_inference_serving.md` | 추론 프레임워크와 모델 서빙 |

## 참고 자료
- `31.local/1.transformers/` — Transformer 기초
- `31.local/2.mymodel/` — 모델 학습/경량화
- `31.local/3.huggingface/` — HuggingFace 파이프라인
- `30.study/1.transformer/` — Transformer 내부 구조
- `30.study/2.bert/` — BERT 파인튜닝
- `30.study/4.korean_nlp/` — 한국어 NLP
- `30.study/5.tokenizer/` — 토크나이저
- `30.study/6.embedding/` — 임베딩
- `30.study/7.attention/` — 어텐션 메커니즘
