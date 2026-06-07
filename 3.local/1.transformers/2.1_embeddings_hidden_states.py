# (2단계) 임베딩 & hidden state — 토큰을 모델에 넣으면 나오는 '벡터'
# pip install transformers torch
#
# 1단계(토큰화) 다음: 토큰 ID 를 모델에 통과(forward)시키면, 각 토큰이
#   '문맥이 반영된 벡터(hidden state)' 로 바뀐다. 이게 트랜스포머의 핵심 출력이다.
#   (이 벡터가 분류·검색·임베딩 등 모든 다운스트림 작업의 재료)

import torch
from transformers import AutoTokenizer, AutoModel

# AutoModel = 분류/생성 헤드가 없는 '본체' 만 → 출력이 곧 hidden state
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")
model.eval()

text = "The cat sat on the mat."
inputs = tokenizer(text, return_tensors="pt")

# [관전 포인트 1] forward 패스 — 추론만 할 땐 no_grad 로 (기울기 계산 끔)
with torch.no_grad():
    outputs = model(**inputs)

# [관전 포인트 2] last_hidden_state 모양 = [배치, 토큰수, 은닉차원]
#   토큰 하나하나가 768차원 벡터로 표현된다 (BERT-base 기준).
hidden = outputs.last_hidden_state
tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
print(f"입력 토큰 ({len(tokens)}개): {tokens}")
print(f"last_hidden_state shape: {tuple(hidden.shape)}  ← [batch, tokens, hidden_dim]")

# [관전 포인트 3] 토큰 하나의 벡터 들여다보기 (앞 8개 값만)
print(f"\n'cat' 토큰 벡터 앞부분: {hidden[0, tokens.index('cat')][:8].tolist()}")

# [관전 포인트 4] 문장 1개를 대표하는 벡터로 만들기 (mean pooling)
#   토큰 벡터들을 평균 → 문장 임베딩. 문장 유사도/검색(RAG) 의 출발점.
sentence_vec = hidden[0].mean(dim=0)
print(f"문장 임베딩 차원: {sentence_vec.shape[0]}  (토큰 벡터 평균)")

# 정리:
#   - 텍스트 → 토큰 → (forward) → 토큰별 벡터(hidden state) = '특징 추출(feature extraction)'
#   - 이 벡터 위에 '헤드' 를 얹으면 용도가 갈린다:
#       분류 헤드 → 감정분석,  MLM 헤드 → 빈칸채우기(3.1),  LM 헤드 → 다음 토큰 예측(2.2)
#   - 다음(2.2): 생성 모델(GPT-2)에 헤드를 얹어 '다음 토큰 확률' 까지 가본다
