# 1.pipelines — NLP 태스크 (pipeline 한 줄로)

`transformers.pipeline()` 로 작은 NLP 모델을 불러 **여러 태스크**를 체험합니다.
전부 CPU 로 돌아가는 작은 모델이라 가장 쉬운 입문 코스입니다.

파일은 **출력 유형별로 묶고**(분류 → 추출 → 생성), 이름에 카테고리 prefix 를 붙였습니다:
`cla_`(classification) · `ext_`(extraction) · `gen_`(generation).

## 학습 순서

| 파일 | 태스크 | 모델 (만든 곳) |
|---|---|---|
| `0.model_cache.py` | 모델 캐시 위치 확인 (유틸) | — |
| **[분류] 출력 = 라벨** | | |
| `1.1_cla_sentiment.py` | 감정 분석 (긍/부정) | distilbert-sst-2 (HuggingFace) |
| `1.2_cla_multilingual_sentiment.py` | 다국어 감정(별점 1~5) | nlptown multilingual BERT |
| `1.3_cla_zero_shot.py` | 제로샷 분류 (학습 없이 임의 라벨) | facebook/bart-large-mnli (Meta) |
| **[추출] 입력에서 뽑기** | | |
| `1.4_ext_ner.py` | 개체명 인식 (사람/조직/장소) | dslim/bert-base-NER |
| `1.5_ext_qa.py` | 질의응답 (문서 안에서 답 span) | distilbert-squad |
| **[생성] 새 텍스트(seq2seq/causal)** | | |
| `1.6_gen_text_generation.py` | 텍스트 이어쓰기 | gpt2 (OpenAI) |
| `1.7_gen_summarization.py` | 요약 | distilbart-cnn (BART 기반, Meta) |
| `1.8_gen_translation.py` | 번역 | Helsinki-NLP opus-mt (MarianMT) |
| **[응용]** | | |
| `2.1_local_only.py` | 캐시된 모델 오프라인 로드 (`local_files_only`) | distilbert |
| `2.2_config_labels.py` | `model.config.id2label` 로 라벨 해석 | distilbert |
| `3.1_qa_langchain.py` | QA 파이프라인을 LangChain 체인에 연결 | distilbert-squad |

## 핵심
- **분류 → 추출 → 생성** 순서로, 출력 형태가 단순한 것부터 복잡한 것으로 발전합니다.
- **태스크마다 전용(파인튜닝된) 모델** 이 필요하다 — base 모델로는 안 된다(특히 NER/QA).
- `pipeline("태스크", model="...")` 한 줄이면 토큰화+모델+후처리를 알아서 해준다.
- 모델 선택/이름 규칙·만든 곳은 상위 [README](../README.md) 와 [2.local_llm/README](../2.local_llm/README.md) 참고.

## 실행
```bash
pip install transformers torch sentencepiece
python 1.1_cla_sentiment.py
```
> 첫 실행 시 모델 자동 다운로드(각 수백 MB~1.6GB). 전부 CPU 동작.
