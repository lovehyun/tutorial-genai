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
| 09:30-10:00 | Transformer 모델 로드 | `12.study/1.transformer/1.model_load.py` | Transformer 모델 구조 탐색 |
| 10:00-10:30 | Transformer 질의 | `12.study/1.transformer/2.model_query.py` | 모델에 질의하며 내부 동작 확인 |
| 10:45-11:15 | 토큰화 이론 | `3.local/1.transformers/2.1_token.py`, `3.local/1.transformers/2.2_token_dict.py` | 토큰화 과정, 토큰 사전 |
| 11:15-12:00 | 토크나이저 비교 | `12.study/5.tokenizer/1.tokenizer_compare.py`, `12.study/5.tokenizer/2.korean_tokenizer.py` | 다양한 토크나이저 성능 비교, 한국어 토크나이저 |
| 13:00-13:30 | 어텐션 시각화 | `3.local/1.transformers/3.1_attention.py`, `3.local/1.transformers/3.2_headwise_topk.py` | Self-Attention 메커니즘 시각화 |
| 13:30-14:00 | 어텐션 심화 시각화 | `12.study/7.attention/1.attention_visualize.py`, `12.study/7.attention/2.qkv_visualize.py` | Q, K, V 벡터 시각화 |
| 14:00-14:30 | BERT 기초 | `12.study/2.bert/1.intro_bert.py` | BERT 모델 구조 이해 |
| 14:45-15:15 | BERT 파인튜닝 (감성분석) | `12.study/2.bert/2.finetune_imdb_sentiment.py`, `12.study/2.bert/3.finetune_imdb_load.py` | IMDB 감성분석 파인튜닝 |
| 15:15-15:45 | BERT 파인튜닝 (뉴스분류) | `12.study/2.bert/2.finetune_agnews_category.py`, `12.study/2.bert/3.finetune_agnews_load.py` | AG News 카테고리 분류 |
| 15:45-16:15 | BERT REST API | `12.study/2.bert/4.restapi_agnews.py`, `12.study/2.bert/4.restapi_imdb.py` | 파인튜닝 모델 API 서빙 |
| 16:15-17:00 | 한국어 NLP 기초 | `12.study/4.korean_nlp/1.morpheme.py`, `12.study/4.korean_nlp/2.preprocessing.py` | 형태소 분석, 전처리, Day 1 정리 |

### Day 2: 모델 경량화와 배포

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 1 복습 | — | Transformer 내부 구조 복습 |
| 09:30-10:00 | 모델 학습 (기초) | `3.local/2.mymodel/1.mymodel_train.py` | 커스텀 모델 학습 기초 |
| 10:00-10:30 | 모델 학습 (한국어) | `3.local/2.mymodel/1.mymodel_train1kr.py`, `3.local/2.mymodel/1.mymodel_train2.py` | 한국어 모델 학습, 개선 버전 |
| 10:45-11:15 | 모델 추론 | `3.local/2.mymodel/2.mymodel_predict.py`, `3.local/2.mymodel/2.mymodel_predict1kr.py` | 학습된 모델로 추론 실행 |
| 11:15-12:00 | 양자화 | `3.local/2.mymodel/3.quantization_save.py`, `3.local/2.mymodel/3.quantization_load.py` | 모델 양자화 저장/로드, 크기 비교 |
| 13:00-13:30 | 레이어 축소 | `3.local/2.mymodel/4.layer_reduction.py` | 레이어 수 줄이기로 경량화 |
| 13:30-14:00 | 가지치기 (Pruning) | `3.local/2.mymodel/5.pruning.py` | 불필요한 가중치 제거 |
| 14:00-14:30 | 어휘 축소 & 지식증류 | `3.local/2.mymodel/6.vocab_reduction.py`, `3.local/2.mymodel/7.knowledge_distillation.py` | 어휘 크기 줄이기, 큰 모델의 지식을 작은 모델로 |
| 14:45-15:15 | HuggingFace 배포 | `3.local/3.huggingface/4.1_huggingface_ep.py`, `3.local/3.huggingface/4.2_huggingface2_inst.py` | HuggingFace Hub 배포 |
| 15:15-15:45 | Flask/FastAPI 서빙 | `3.local/3.huggingface/4.local4_neo27_flask.py`, `3.local/3.huggingface/4.local5_neo27_fastapi.py` | Flask/FastAPI 모델 서빙 |
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
- `3.local/1.transformers/` — Transformer 기초
- `3.local/2.mymodel/` — 모델 학습/경량화
- `3.local/3.huggingface/` — HuggingFace 파이프라인
- `12.study/1.transformer/` — Transformer 내부 구조
- `12.study/2.bert/` — BERT 파인튜닝
- `12.study/4.korean_nlp/` — 한국어 NLP
- `12.study/5.tokenizer/` — 토크나이저
- `12.study/6.embedding/` — 임베딩
- `12.study/7.attention/` — 어텐션 메커니즘
