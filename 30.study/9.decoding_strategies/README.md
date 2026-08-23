# 9.decoding_strategies — 다음 토큰을 어떻게 고르는가

모델은 매 스텝 "다음 토큰일 확률"을 어휘 전체에 대해 하나씩 낸다(`31.local/1.transformers/
2.2_logits_next_token.py` 참고). **그 확률 분포에서 실제로 하나를 어떻게 골라내는지**가
디코딩(샘플링) 전략이다 — `temperature` 파라미터를 다들 쓰지만 그게 분포를 어떻게 바꾸는지
직접 본 적은 없을 것이다. 여기서 그림으로 확인한다.

## 이 폴더 vs `31.local/1.transformers/4.1_decoding_strategies.py`

같은 주제를 다른 각도로 본다 — **중복이 아니라 서로 보완**한다.

| | `31.local/1.transformers/4.1_decoding_strategies.py` | 여기(`1.decoding_visualize.py`) |
|---|---|---|
| 초점 | 실전 사용법 — greedy/beam/sampling 결과 **문장**을 비교 | 원리 — 확률 **분포 자체**가 어떻게 바뀌는지 시각화 |
| 출력 | 생성된 텍스트(문장) | 그래프(막대·누적확률 곡선) |
| 질문 | "이 전략을 쓰면 어떤 문장이 나오나?" | "왜 그런 문장이 나오나? 분포에 무슨 일이 일어난 건가?" |

먼저 `31.local` 쪽에서 "결과가 이렇게 다르구나"를 보고, 여기서 "왜 다른가"를 그림으로 확인하는
순서를 권장한다.

## 파일
| 파일 | 내용 |
|---|---|
| `1.decoding_visualize.py` | temperature가 분포를 재조정하는 과정 + top-k/top-p가 어디서 후보를 잘라내는지 시각화 |

## 실행
```bash
pip install transformers torch matplotlib numpy
python 1.decoding_visualize.py
```

## 관전 포인트
- **temperature는 분포를 "재조정"할 뿐 새 정보를 더하지 않는다** — `logits / temperature` 후
  softmax. 낮으면(0.5) 1등에 확률이 몰려 뾰족해지고, 높으면(2.0) 고르게 퍼져 평평해진다.
- **top-k는 순위로, top-p는 누적확률로 자른다** — top-k는 항상 같은 개수(k개)를 남기지만,
  top-p는 분포 모양에 따라 남는 후보 수가 달라진다(확신이 강한 분포는 적게, 애매한 분포는
  많이 남는다) — 이게 top-p가 실전에서 더 널리 쓰이는 이유다.
- **greedy는 결정적, sampling은 확률적** — greedy를 5번 반복하면 항상 같은 토큰이 나오고,
  sampling은 같은 확률 분포에서도 매번 다른 토큰이 뽑힐 수 있다(`torch.multinomial`).

## 다음 단계
- 실제 생성 문장으로 비교 → [`../../31.local/1.transformers/4.1_decoding_strategies.py`](../../31.local/1.transformers/4.1_decoding_strategies.py)
- 이 확률 분포가 애초에 어떻게 나오는지(다음 토큰 예측 vs 빈칸 채우기) → [`../11.training_objectives/`](../11.training_objectives/)
