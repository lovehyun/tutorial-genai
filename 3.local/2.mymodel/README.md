# 2.mymodel — 나만의 모델 만들기 & 경량화

사전학습 모델을 **내 데이터로 학습(파인튜닝)** 하고, 그 모델을 **작고 빠르게 경량화** 하는
두 흐름을 각각 기초부터 단계별로 다룹니다.

```
1.finetune/     ← 내 데이터로 '나만의 모델' 학습
2.compression/  ← 학습한(혹은 기존) 모델을 작게 만들기
```

## 1.finetune — 파인튜닝 (내 모델 학습)

> **파인튜닝이란?** 밑바닥부터 학습하는 게 아니라, 이미 언어를 아는 사전학습 모델
> (distilbert 등) 위에 **작은 분류 헤드를 얹어 내 데이터로만 추가 학습** 하는 것.
> 데이터·시간이 훨씬 적게 들면서 '나만의 분류기' 가 만들어진다.

| 파일 | 배우는 것 |
|---|---|
| `1.1_train.py` | 데이터 → 토큰화 → 학습 → 평가(정확도) → 저장 (distilbert 감성분류기) |
| `1.2_predict.py` | 1.1 이 저장한 `./my_local_model` 을 불러와 예측 |
| `1.3_train_korean.py` | 같은 흐름, 모델/데이터만 한국어로(KcBERT) — 모델 교체만으로 언어 전환 |

> 핵심: **학습 → 저장 → 로드 → 예측** 이 완결된 한 흐름. (데이터는 구조 학습용 소량이라
> 정확도 수치 자체보다 '흐름' 에 집중하세요. 실전은 수백~수천 건 + train/val/test 분리)

## 2.compression — 경량화 (쉬운 것부터)

| 파일 | 기법 | 줄이는 대상 |
|---|---|---|
| `2.1_quantization.py` | 동적 양자화 (float32→int8) | 가중치 **정밀도** — 크기↓ 속도↑ |
| `2.2_layer_reduction.py` | 층 제거 (12→6) | 모델 **구조(층 수)** |
| `2.3_pruning.py` | L1 프루닝 (50%) | 개별 **가중치**(0으로) |
| `2.4_vocab_reduction.py` | 어휘 재학습 | **어휘(vocab)** = 임베딩 크기 |
| `2.5_distillation.py` | 지식 증류 (교사→학생) | 큰 모델 → **작은 모델** 로 지식 이전 |

> 각 예제는 경량화 **효과를 직접 측정** 합니다 (크기 MB / 파라미터 수 / 0 비율 / 손실 감소).
> 2.1~2.4 는 "그냥 줄이면 성능은 떨어질 수 있다" → 보통 재학습이나 2.5 증류로 회복합니다.

## 설치 & 실행

```bash
pip install transformers torch datasets tokenizers

cd "3.local/2.mymodel/1.finetune"
python 1.1_train.py        # → ./my_local_model 생성
python 1.2_predict.py      # 저장한 모델로 예측

cd "../2.compression"
python 2.1_quantization.py
python 2.5_distillation.py
```

> 첫 실행 시 모델 다운로드: distilbert ~268MB, bert-base ~420MB, KcBERT ~400MB.
> 모두 CPU 로 동작합니다 (소량 데이터라 학습도 수십 초). GPU 가 있으면 더 빠릅니다.
