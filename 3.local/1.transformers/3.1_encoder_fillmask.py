# (3단계) 인코더 모델 — BERT 의 빈칸 채우기(Masked LM)
# pip install transformers torch
#
# 트랜스포머는 크게 두 갈래다. 이 파일은 그 중 '인코더(이해형)' 를 본다.
#   - 인코더(BERT): 문장 전체를 양방향으로 보고 [MASK] 자리를 맞힌다 = '이해'
#   - 디코더(GPT, 3.2): 왼→오 한 방향으로 다음 단어를 잇는다 = '생성'
# 이 예제: BERT 가 문맥을 보고 [MASK] 에 들어갈 단어를 확률순으로 예측한다.

from transformers import pipeline

# fill-mask 파이프라인 = 토큰화 + 모델 + MLM 헤드 해석을 한 번에
fill = pipeline("fill-mask", model="bert-base-uncased")

sentences = [
    "The capital of France is [MASK].",
    "I love [MASK] because it is fun.",
    "Transformers are a type of neural [MASK].",
]

for s in sentences:
    print(f"\n문장: {s}")
    for r in fill(s, top_k=3):          # 상위 3개 후보
        print(f"  {r['token_str']!r:12} 확률 {r['score']:.3f}")

# [관전 포인트] 인코더는 [MASK] '양쪽' 문맥을 다 본다
#   "The capital of France is [MASK]." → 앞부분 전체를 근거로 'paris' 를 높게 준다.
#   디코더(GPT)는 뒤를 못 보므로 이런 빈칸 채우기엔 안 맞는다.

# 정리:
#   - 인코더(BERT) = 분류/개체명/검색 임베딩 등 '이해' 작업에 강함
#   - 다음(3.2): 디코더(GPT-2) 로 '생성' 을 직접 — 2.2 의 다음-토큰-뽑기를 반복하는 모습
