# (1단계) 특수 토큰 & attention_mask — 모델이 토큰 외에 함께 받는 것들
# pip install transformers torch
#
# 1.1 대비 새로 배우는 것:
#   토크나이저는 단어 토큰만 주는 게 아니라, 모델이 필요로 하는 부가 정보도 같이 만든다.
#   ① 특수 토큰([CLS]/[SEP] 등)  ② attention_mask  ③ 배치 패딩(padding)

from transformers import AutoTokenizer

bert_tok = AutoTokenizer.from_pretrained("bert-base-uncased")

# [관전 포인트 1] 토크나이저 호출 결과 = 단순 ID 목록이 아니라 '딕셔너리'
enc = bert_tok("Hello world")
print("=== bert_tok('Hello world') ===")
for k, v in enc.items():
    print(f"  {k}: {v}")

# [관전 포인트 2] 앞뒤에 특수 토큰이 자동으로 붙는다 ([CLS] ... [SEP])
#   문장 시작/끝을 모델에게 알려주는 표식 — BERT 계열이 학습 때 본 형식이다.
print("\n특수 토큰 포함 복원:", bert_tok.decode(enc["input_ids"]))
print(f"  CLS={bert_tok.cls_token}  SEP={bert_tok.sep_token}  "
      f"PAD={bert_tok.pad_token}  MASK={bert_tok.mask_token}")

# [관전 포인트 3] 길이가 다른 문장을 '배치' 로 넣으려면 짧은 쪽을 PAD 로 채운다
#   attention_mask = 1(진짜 토큰) / 0(패딩) → 모델이 패딩을 무시하게 해주는 표식.
batch = bert_tok(
    ["short text", "a noticeably longer sentence here"],
    padding=True,
    return_tensors="pt",
)
print("\n=== 배치 패딩 ===")
print("input_ids:\n", batch["input_ids"])
print("attention_mask:\n", batch["attention_mask"])
print("→ 짧은 문장 뒤쪽 0 = 패딩 자리, 모델은 이 자리를 계산에서 무시한다")

# [관전 포인트 4] GPT-2 는 pad_token 이 없다 (생성 전용이라 배치 패딩을 거의 안 씀)
gpt2_tok = AutoTokenizer.from_pretrained("gpt2")
print(f"\nGPT-2 pad_token: {gpt2_tok.pad_token}  (None → 보통 eos_token 으로 대체해 사용)")

# 정리:
#   - 모델 입력 = input_ids + attention_mask (+ 모델에 따라 token_type_ids 등)
#   - 특수 토큰/패딩은 '모델이 학습 때 본 형식' 을 맞춰주는 장치
#   - 다음(2.1): 이 입력을 모델에 넣으면 나오는 첫 출력 = 토큰별 '벡터(hidden state)'
