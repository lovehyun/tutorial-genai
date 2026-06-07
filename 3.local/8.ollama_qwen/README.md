# 8.ollama_qwen — Qwen 으로 한국어 NLP 태스크 (Ollama)

**Qwen**(Alibaba) 한 모델로 한국어 NLP 태스크들을 프롬프트만으로 처리합니다.
전부 **Ollama** 로 로컬 실행하며, 예제는 따라하기 쉽게 짧게 구성했습니다.

> Qwen 은 **Apache 2.0**(상업 사용 자유) + 다국어(한국어 포함) 균형이 장점입니다.
> 한국어 자연스러움이 더 필요하면 EXAONE → [`../9.ollama_exaone`](../9.ollama_exaone) 참고.

## 준비

```bash
# Ollama 설치 후 모델 받기 (택1)
ollama pull qwen2.5:1.5b    # 가볍고 빠름 (예제 기본)
ollama pull qwen2.5:7b      # 한국어 품질 ↑
ollama pull qwen3:4b        # 최신
pip install ollama          # 파이썬 SDK
```
> 각 파일 상단 `MODEL = "qwen2.5:1.5b"` 를 받은 태그로 바꾸면 됩니다.
> Ollama 데몬이 떠 있어야 합니다 (보통 자동, 아니면 `ollama serve`).

## 예제 (분류·추출·생성)

| 파일 | 태스크 | 핵심 |
|---|---|---|
| `1.chat.py` | 대화 | 단일/멀티 턴, messages 누적 |
| `2.sentiment.py` | 감성 분석 | `format="json"` 으로 구조화 출력 |
| `3.classification.py` | 분류 | 카테고리 리스트만 바꾸면 zero-shot |
| `4.ner.py` | 개체명 인식 | PER/ORG/LOC/DATE 추출 (JSON) |
| `5.summarization.py` | 요약 | N문장 / 불릿, 형식 프롬프트로 제어 |
| `6.translation.py` | 번역 | 한↔영 + 문체(존댓말/반말) 지정 |

## 핵심 정리
- **학습 데이터 없이** 프롬프트만으로 분류/감성/NER 등이 된다 (zero-shot).
- 정확도 중요한 태스크(감성/분류/번역)는 **temperature 낮게**, 구조화는 **`format="json"`**.
- 호출은 **ollama 파이썬 SDK**(`ollama.chat`/`ollama.generate`) — REST 보다 간단. (REST vs SDK 비교는 [`../6.ollama1_restapi`](../6.ollama1_restapi) ↔ [`../6.ollama2_sdk`](../6.ollama2_sdk))
- 더 높은 품질은 큰 모델(`qwen2.5:7b`/`qwen3`)로 교체 — 코드는 그대로.

> 참고: 학습 기반 분류(BERT 파인튜닝)는 [`../2.mymodel`](../2.mymodel), 본격 RAG 는 [`../../2.langchain/7.RAG`](../../2.langchain/7.RAG).
