# BERT — 사전학습 언어 모델 파인튜닝

BERT(Masked LM으로 사전학습된 인코더)를 감성분류/토픽분류 태스크로 직접 파인튜닝한다. "왜
BERT가 이해/분류에 강한가"의 원리는 [`../11.training_objectives/`](../11.training_objectives/)
참고 — 여기는 그 원리를 실제로 써먹는 실습이다.

## 파일

| 파일 | 내용 |
|---|---|
| `1.intro_bert.py` | 사전학습된 다국어 감정분석 BERT로 바로 추론(파인튜닝 없이) |
| `2.finetune_agnews_category.py` | AG News 데이터셋으로 토픽 분류 파인튜닝 |
| `2.finetune_imdb_sentiment.py` | IMDB 데이터셋으로 감성분류 파인튜닝 |
| `3.finetune_agnews_load.py` | 2번이 저장한 AG News 모델을 불러와 추론 |
| `3.finetune_imdb_load.py` | 2번이 저장한 IMDB 모델을 불러와 추론 |
| `4.restapi_agnews.py` | AG News 분류 모델을 REST API로 서빙 |
| `4.restapi_imdb.py` | IMDB 감성분류 모델을 REST API로 서빙 |

두 갈래(AG News/IMDB)는 같은 흐름(파인튜닝 → 저장 → 로드 → 서빙)을 서로 다른 태스크로
반복한다 — 하나를 끝까지 따라간 뒤 다른 하나와 비교하면서 보는 걸 권장한다.

## 실행 순서
```bash
pip install transformers torch datasets

python 1.intro_bert.py                    # 파인튜닝 없이 바로 사용
python 2.finetune_imdb_sentiment.py        # 파인튜닝 → 모델 저장
python 3.finetune_imdb_load.py             # 저장한 모델로 추론
python 4.restapi_imdb.py                   # REST API로 서빙
```

## 다음 단계
- 전체 파라미터 대신 LoRA로 가볍게 파인튜닝하고 싶다면 → [`../../31.local/2.mymodel/3.lora/`](../../31.local/2.mymodel/3.lora/)
- 왜 BERT는 이해에 강하고 GPT는 생성에 강한지(학습 목적함수 차이) → [`../11.training_objectives/`](../11.training_objectives/)
