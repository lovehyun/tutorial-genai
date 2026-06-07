# 1.pipelines — NLP 태스크 (pipeline 한 줄로)

`transformers.pipeline()` 로 작은 NLP 모델을 불러 **여러 태스크**를 체험합니다.
전부 CPU 로 돌아가는 작은 모델이라 가장 쉬운 입문 코스입니다.

## 학습 순서

| 파일 | 태스크 | 모델 |
|---|---|---|
| `0.model_cache.py` | 모델 캐시 위치 확인 (유틸) | — |
| `1.1_sentiment.py` | 감정 분석 (긍/부정) | distilbert-sst-2 |
| `1.2_qa.py` | 질의응답 (문서 안에서 답 찾기) | distilbert-squad |
| `1.3_ner.py` | 개체명 인식 (사람/조직/장소) | dslim/bert-base-NER |
| `1.4_text_generation.py` | 텍스트 생성 | gpt2 |
| `1.5_multilingual_sentiment.py` | 다국어 감정(별점 1~5) | nlptown multilingual |
| `2.1_local_only.py` | 캐시된 모델 오프라인 로드 (`local_files_only`) | distilbert |
| `2.2_config_labels.py` | `model.config.id2label` 로 라벨 해석 | distilbert |
| `3.1_qa_langchain.py` | QA 파이프라인을 LangChain 체인에 연결 | distilbert-squad |

## 핵심
- **태스크마다 전용(파인튜닝된) 모델** 이 필요하다 — base 모델로는 안 된다(특히 NER/QA).
- `pipeline("태스크", model="...")` 한 줄이면 토큰화+모델+후처리를 알아서 해준다.
- 모델 선택/이름 규칙은 상위 [README](../README.md) 의 "모델 찾기 & 고르기" 참고.

## 실행
```bash
pip install transformers torch
python 1.1_sentiment.py
```
> 첫 실행 시 모델 자동 다운로드(각 수백 MB). 전부 CPU 동작.
