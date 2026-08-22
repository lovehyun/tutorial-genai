# (1단계) 토큰화 — 트랜스포머의 가장 처음: 글자를 '토큰'으로 쪼개기
# pip install transformers torch
#
# 트랜스포머 모델은 글자를 직접 못 본다. 먼저 '토큰(subword) ID' 로 바꿔야 한다.
# 이 예제: 모델마다 '자기 토크나이저' 가 있고, 같은 단어도 다르게 쪼갠다는 걸 본다.
#   (※ OpenAI 의 tiktoken 이 아니라, 이 모델이 실제로 쓰는 토크나이저로 학습한다)

from transformers import AutoTokenizer

# [관전 포인트 1] 모델마다 토크나이저가 다르다
#   GPT-2 = BPE (공백을 'Ġ' 로 표시)  /  BERT = WordPiece (이어붙인 조각에 '##' 접두)
gpt2_tok = AutoTokenizer.from_pretrained("gpt2")
bert_tok = AutoTokenizer.from_pretrained("bert-base-uncased")

print(f"GPT-2 어휘 수: {gpt2_tok.vocab_size:,}   BERT 어휘 수: {bert_tok.vocab_size:,}\n")

# [관전 포인트 2] 같은 단어가 토크나이저에 따라 다르게 쪼개진다
words = ["redone", "walking", "walker", "tokenization", "unbelievable"]

print(f"{'단어':14} | {'GPT-2 (BPE)':40} | BERT (WordPiece)")
print("-" * 90)
for w in words:
    gpt2_pieces = gpt2_tok.convert_ids_to_tokens(gpt2_tok.encode(w))
    bert_pieces = bert_tok.tokenize(w)   # BERT 는 special token 빼고 순수 조각만
    print(f"{w:14} | {str(gpt2_pieces):40} | {bert_pieces}")

# [관전 포인트 3] encode(글자→ID) ↔ decode(ID→글자) 는 역연산
print("\n--- encode / decode 왕복 ---")
text = "Transformers are powerful."
ids = gpt2_tok.encode(text)
print(f"원문 : {text}")
print(f"토큰 ID : {ids}")
print(f"복원 : {gpt2_tok.decode(ids)}")

# 정리:
#   - 흔한 단어는 토큰 1개, 드문 단어(tokenization 등)는 여러 조각으로 쪼개진다 = subword
#   - 그래서 모델 입력 길이는 '글자 수' 가 아니라 '토큰 수' 로 센다 (비용/길이제한의 기준)
#   - 다음(1.2): 토큰 외에 모델이 함께 받는 special token / attention_mask 를 본다
