# 최신 한국어 로컬 LLM

저사양 PC(8GB RAM, GPU 없음)에서 실행 가능한 최신 한국어 지원 소형 언어모델 비교 및 실습 예제입니다.
모든 예제는 **Ollama**를 사용하여 한 줄로 모델을 설치하고 Python에서 바로 호출합니다.

## 모델 비교표

| 모델 | 개발사 | 파라미터 | GGUF Q4 크기 | RAM | 한국어 품질 | 라이선스 | Ollama |
|------|--------|---------|-------------|-----|-----------|---------|--------|
| **EXAONE 3.5** | LG AI Research | 2.4B | ~1.5 GB | ~3 GB | ★★★★★ | 비상업 | `exaone3.5:2.4b` |
| **EXAONE Deep** | LG AI Research | 2.4B | ~1.5 GB | ~3 GB | ★★★★★ | 비상업 | `exaone-deep:2.4b` |
| **Kanana Nano** | 카카오 | 2.1B | ~1.3 GB | ~2.5 GB | ★★★★★ | CC-BY-NC | 커뮤니티 |
| **Qwen3** | Alibaba | 4B | ~2.5 GB | ~4 GB | ★★★★☆ | Apache 2.0 | `qwen3:4b` |
| **Qwen3** | Alibaba | 1.7B | ~1.2 GB | ~2.5 GB | ★★★☆☆ | Apache 2.0 | `qwen3:1.7b` |
| **Gemma 3** | Google | 4B | ~2.5 GB | ~4 GB | ★★★★☆ | Gemma License | `gemma3:4b` |
| **Bllossom 3B** | MLP Lab | 3B | ~2.0 GB | ~3.5 GB | ★★★★☆ | Llama CL | 커뮤니티 |
| **Phi-4-mini** | Microsoft | 3.8B | ~2.3 GB | ~4 GB | ★★★☆☆ | MIT | `phi4-mini` |

## 모델별 특징

### EXAONE 3.5 2.4B (LG AI Research) — 한국어 최강
- **아키텍처**: Decoder-only Transformer, 32K 컨텍스트
- **특징**: 한국어+영어 이중언어 네이티브 지원, LG가 한국어 데이터로 직접 학습
- **강점**: 한국어 대화, 요약, 번역, Q&A 모두 최고 수준
- **Deep 변형**: 추론 강화 버전 (`<thought>` 토큰으로 Chain-of-Thought)
- **제한**: 비상업 라이선스 (연구/교육용)

### Qwen3 4B (Alibaba) — 오픈 라이선스 최강
- **아키텍처**: Decoder-only, 32K 컨텍스트, 119+ 언어
- **특징**: Apache 2.0 라이선스로 상업 사용 자유
- **강점**: 한국어 포함 다국어 균형 잡힌 성능, 코딩 능력 우수
- **1.7B 변형**: 더 가벼운 옵션 (Qwen3-1.7B ≈ Qwen2.5-3B 성능)

### Kanana Nano 2.1B (카카오) — 한국어 네이티브
- **아키텍처**: Depth Up-scaling + Pruning + Distillation
- **특징**: 카카오가 한국어 우선으로 설계, 임베딩/RAG/함수호출 전용 모델도 별도 제공
- **강점**: 2.1B로 한국어 최고 수준, 매우 가벼움
- **제한**: CC-BY-NC (비상업)

### Gemma 3 4B (Google) — 멀티모달 지원
- **아키텍처**: 128K 컨텍스트, 140+ 언어
- **특징**: 이미지+텍스트 멀티모달 (4B), PPO 학습으로 한국어 벤치마크 GPT-4o 수준
- **강점**: 긴 컨텍스트(128K), 다양한 언어 지원

### Bllossom 3B (MLP Lab) — 한국어 특화 Llama
- **아키텍처**: Llama 3.2 3B 기반 한국어 파인튜닝
- **특징**: 150GB 한국어 텍스트로 추가 학습
- **강점**: 한국어-영어 이중언어 대화, 번역

## 설치

```bash
# Ollama 설치
curl -fsSL https://ollama.ai/install.sh | sh

# 추천 모델 다운로드 (택 1~2개)
ollama pull exaone3.5:2.4b    # 한국어 최강 (1.5GB)
ollama pull qwen3:4b           # 오픈 라이선스 최강 (2.5GB)
ollama pull qwen3:1.7b         # 초경량 (1.2GB)
ollama pull gemma3:4b          # Google 대안 (2.5GB)
```

## 예제 목록

| 파일 | 태스크 | 설명 |
|------|--------|------|
| `1.chat.py` | 대화 생성 | 한국어 챗봇 + 모델 비교 |
| `2.sentiment.py` | 감성 분석 | 리뷰 긍정/부정/중립 판별 (JSON 출력) |
| `3.classification.py` | 텍스트 분류 | 뉴스 기사 카테고리 분류 |
| `4.ner.py` | 개체명 인식 | 인물/조직/장소/날짜 추출 |
| `5.summarization.py` | 텍스트 요약 | 뉴스 기사 3문장 요약 |
| `6.translation.py` | 번역 | 한국어 ↔ 영어 양방향 번역 |

## 태스크별 추천 모델

| 태스크 | 1순위 | 2순위 | 비고 |
|--------|-------|-------|------|
| 한국어 대화 | EXAONE 3.5 | Qwen3 4B | EXAONE이 자연스러움 |
| 감성 분석 | Qwen3 4B | EXAONE 3.5 | JSON 구조화 출력 안정적 |
| 텍스트 분류 | Qwen3 4B | Gemma 3 4B | 지시 따르기 우수 |
| 개체명 인식 | Qwen3 4B | EXAONE 3.5 | 4B 이상 권장 |
| 요약 | EXAONE 3.5 | Qwen3 4B | 한국어 문장력 우수 |
| 번역 | Qwen3 4B | Bllossom 3B | 다국어 학습량 많음 |

## BERT 파인튜닝 vs LLM 프롬프트 방식 비교

| 항목 | BERT 파인튜닝 (9.nlp/2.bert/) | LLM 프롬프트 (여기) |
|------|------------------------------|-------------------|
| 준비 | 학습 데이터 + GPU 학습 필요 | 프롬프트 작성만 |
| 정확도 | 특정 태스크에서 매우 높음 | 범용적이나 불안정할 수 있음 |
| 유연성 | 학습한 태스크만 가능 | 프롬프트만 바꾸면 어떤 태스크든 |
| 비용 | 학습 시간/GPU 비용 | 추론 비용만 |
| 적합한 상황 | 대량 데이터 반복 처리 | 프로토타이핑, 소량 처리 |
