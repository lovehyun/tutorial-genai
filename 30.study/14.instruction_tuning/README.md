# 14.instruction_tuning — 왜 base 모델은 질문에 답을 안 할까

`11.training_objectives`에서 본 사전학습은 "다음 토큰 맞히기"만 반복한다. 그 결과물(base 모델)은
"그럴듯하게 이어쓰기"는 잘하지만 "질문에 답하기"를 배운 적이 없다. Instruction tuning은 그 위에
(지시, 좋은 응답) 쌍을 추가로 학습시켜 "질문하면 답한다"는 대화 형식 자체를 가르친다. 같은
아키텍처·크기의 base/instruct 모델을 나란히 돌려서 그 차이를 직접 눈으로 확인한다.

## 파일

| 파일 | 내용 |
|---|---|
| `1.base_vs_instruct.py` | TinyLlama base(사전학습만) vs TinyLlama-Chat(instruction tuning 적용) — 같은 질문에 대한 응답 비교 |

## 실행 (실측 결과)
```bash
pip install transformers torch
python 1.base_vs_instruct.py
```
```
같은 질문: "List three benefits of regular exercise."

[ 1. Base 모델 (TinyLlama_v1.1, instruction tuning 이전) ]
The 2018 edition of the annual report of the International Monetary Fund (IMF) has been
released. The report, which is the IMF's flagship publication, is a comprehensive analysis
of the global economy.
The report, which was released on T

[ 2. Instruct 모델 (TinyLlama-1.1B-Chat, instruction tuning 이후) ]
1. Improved cardiovascular health: Regular exercise helps to improve blood flow and reduce
   the risk of heart disease.
2. Increased energy levels: Exercise releases endorphins, which are natural mood boosters,
   and helps to increase energy levels.
3. Reduced risk of chronic diseases: Regular exercise has been
```

## 관전 포인트
- **같은 모델, 다른 학습이 만든 극단적 차이**: 두 모델은 아키텍처·파라미터 수가 완전히 같다
  (둘 다 TinyLlama 1.1B). 그런데도 base 모델은 질문을 완전히 무시하고 IMF 보고서 얘기로
  새버린다 — "멍청해서"가 아니라 "질문엔 답해야 한다"는 규칙 자체를 배운 적이 없어서다.
- **채팅 템플릿은 형식 자체가 학습된 결과물**: instruct 모델도 `tokenizer.apply_chat_template()`로
  올바른 `<|user|>...<|assistant|>` 형식을 갖춰 넣어야 제대로 동작한다 — 이 형식 자체가
  instruction tuning 단계에서 "약속"으로 학습된 것이라, 안 지키면 base처럼 동작할 수 있다.
- **RLHF는 그다음 단계**: instruction tuning까지는 "정답 예시를 그대로 따라 하기"(지도학습)다.
  RLHF는 여러 후보 응답 중 "더 선호되는 답"을 사람 피드백(또는 보상모델)으로 골라내 강화학습으로
  추가 조정하는 것 — 이 저장소에서 그 강화학습 루프까지 재현하지는 않지만, 그 앞단계의 효과만으로도
  위처럼 극적인 차이가 생긴다는 걸 확인했다.

## 다음 단계
- 사전학습이 무엇을 최적화하는지(그래서 base 모델이 왜 저렇게 되는지) → [`../11.training_objectives/`](../11.training_objectives/)
- 학습된 모델의 응답 품질을 숫자로 비교하는 법(perplexity) → [`../../31.local/1.transformers/7.1_perplexity_eval.py`](../../31.local/1.transformers/7.1_perplexity_eval.py)
- 실전에서 instruct 모델을 더 파고드는 예시 → [`../../31.local/5.llama/`](../../31.local/5.llama/)
