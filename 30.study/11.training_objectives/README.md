# 11.training_objectives — GPT와 BERT는 "다른 문제"를 풀도록 학습됐다

`31.local/1.transformers/3.1_encoder_fillmask.py`(BERT 빈칸 채우기)와 `3.2_decoder_generate.py`
(GPT 생성)가 두 모델이 **학습이 끝난 뒤** 어떻게 다르게 동작하는지 보여줬다. 여기서는 한 단계
더 들어가 **애초에 학습할 때 무엇을 맞히도록 시켰는지**(loss가 어디서 계산되는지)를 직접
계산해서 확인한다 — 이 차이가 두 모델의 성격 차이(생성 vs 이해)를 만든 근본 원인이다.

## 파일

| 파일 | 내용 |
|---|---|
| `1.objectives_compare.py` | Causal LM(GPT, 다음 토큰 예측) vs Masked LM(BERT, 빈칸 채우기)의 실제 loss를 계산하고, 어느 위치가 학습 신호를 만드는지 시각화 |

## 실행
```bash
pip install transformers torch matplotlib numpy
python 1.objectives_compare.py
```

## 실행 결과 (실측, 문장: "The cat sat on the mat")
```
Causal LM  loss = 4.850   ← 거의 모든 위치가 "바로 다음 토큰"을 맞혀야 함
Masked LM  loss = 6.350   ← [MASK]로 가려진 위치만 맞히면 됨
```

## 관전 포인트
- **loss가 계산되는 위치 자체가 다르다** — Causal LM은 (마지막 제외) 거의 전체 위치가 "다음
  토큰"을 맞혀야 하고, Masked LM은 인위적으로 가린 자리만 맞히면 된다. 이 차이가 "왼쪽만 보고
  잇는 연습"(생성에 강함) vs "양쪽을 다 보고 채우는 연습"(이해에 강함)을 만든다.
- **`label = -100`**은 HuggingFace의 관례다 — 이 값이 있는 위치는 loss 계산에서 제외된다.
  Masked LM은 안 가려진 위치를 전부 -100으로 채워서 "가려진 곳만" 학습 신호를 만든다.
- **BERT가 문장을 못 쓰고 GPT가 빈칸을 못 채우는 이유**는 능력 부족이 아니라 애초에 그런 연습을
  한 적이 없어서다 — BERT는 "왼쪽만 보고 잇기"를 해본 적이 없고(항상 양쪽을 다 봄), GPT는
  causal mask 때문에 애초에 뒤쪽을 볼 수 없게 학습됐다.
- **실전 연결**: `1.openai`/`3.anthropic`의 모든 챗 모델은 Causal LM 계열(다음 토큰 예측의
  연장)이고, `30.study/2.bert`에서 파인튜닝한 분류기는 Masked LM으로 사전학습된 모델 위에
  분류 헤드를 얹은 것이다 — "왜 GPT는 대화형이고 BERT는 분류/검색에 쓰이는가"의 답이 이것.

## 다음 단계
- 학습이 끝난 두 모델이 실제로 어떻게 다르게 동작하는지 → [`../../31.local/1.transformers/3.1_encoder_fillmask.py`](../../31.local/1.transformers/3.1_encoder_fillmask.py), [`3.2_decoder_generate.py`](../../31.local/1.transformers/3.2_decoder_generate.py)
- Causal LM이 다음 토큰을 고르는 방식(디코딩 전략) → [`../9.decoding_strategies/`](../9.decoding_strategies/)
- BERT를 실제로 파인튜닝해보기 → [`../2.bert/`](../2.bert/)
