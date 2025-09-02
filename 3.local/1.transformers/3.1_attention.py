# filename: attention_numbers.py
import re
import torch
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM

# GPT-2 small은 num_layers = 12, num_attention_heads = 12.
# GPT-2 small의 hidden dimension은 768이고 head가 12개라면:
# - head당 차원 = 768 ÷ 12 = 64
# - 각 head는 64차원 공간에서 Query/Key/Value 연산
# - 레이어마다 12개 head × 12 레이어 = 총 144개의 attention head

# 모델	파라미터 수	레이어 수 (Transformer blocks)	hidden dim	어텐션 head 수
# GPT-3 Small	125M	12	768	12
# GPT-3 Medium	350M	24	1,024	16
# GPT-3 Large	760M	24	1,536	16
# GPT-3 XL	1.3B	24	2,048	32
# GPT-3 2.7B	2.7B	32	2,560	32
# GPT-3 6.7B	6.7B	32	4,096	32
# GPT-3 13B	13B	40	5,120	40
# GPT-3 175B	175B	96	12,288	96

# ===== 설정 =====
MODEL_NAME = "gpt2"   # "gpt2" 또는 "bert-base-uncased"
SENTS = [
    "The homework was redone.",
    "The car is a red one."
]
TARGETS = ["redone", "red one"]   # 각 문장에서 찾을 구절
LAYER = -1        # 마지막 레이어(0부터 시작). -1이면 마지막
HEADS = "mean"    # "mean" 또는 정수(특정 헤드 인덱스)
TOPK = 10         # 상위 k개 토큰 출력
SANITIZE = True   # 자기 자신/문장 시작 토큰 가중치 0 후 재정규화

# ===== 로드 =====
use_decoder = MODEL_NAME.startswith("gpt2")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)

if use_decoder:
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, output_attentions=True, attn_implementation="eager"
    )
else:
    model = AutoModel.from_pretrained(
        MODEL_NAME, output_attentions=True
    )

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device).eval()

def find_char_span(text: str, phrase: str):
    m = re.search(re.escape(phrase.lower()), text.lower())
    return (m.start(), m.end()) if m else None

def char_span_to_token_span(offset_mapping, char_span):
    if char_span is None:
        return []
    s_c, e_c = char_span
    spans = offset_mapping[0].tolist()
    ids = []
    for i, (s, e) in enumerate(spans):
        if s == e:  # 특수 토큰
            continue
        # 문자 범위와 겹치면 포함
        if not (e <= s_c or e_c <= s):
            ids.append(i)
    return ids

def get_attn_scores(sentence: str, phrase: str):
    enc = tokenizer(sentence, return_tensors="pt", return_offsets_mapping=True, add_special_tokens=True)
    enc = {k: (v.to(device) if hasattr(v, "to") else v) for k, v in enc.items()}
    tokens = tokenizer.convert_ids_to_tokens(enc["input_ids"][0])

    # 대상 구간(문자→토큰)
    char_span = find_char_span(sentence, phrase)
    tok_span = char_span_to_token_span(enc["offset_mapping"], char_span)

    # 모델 입력에는 offset_mapping 제외
    inputs = {"input_ids": enc["input_ids"], "attention_mask": enc.get("attention_mask")}
    if "token_type_ids" in enc:
        inputs["token_type_ids"] = enc["token_type_ids"]

    with torch.no_grad():
        out = model(**inputs)

    # attentions: list[L] of (batch, heads, seq, seq)
    attentions = out.attentions
    if LAYER == -1:
        A = attentions[-1][0]  # (heads, seq, seq)
    else:
        A = attentions[LAYER][0]

    if HEADS == "mean":
        A = A.mean(dim=0)      # (seq, seq) 헤드 평균
    else:
        A = A[HEADS]           # (seq, seq) 특정 헤드

    # 대상 구간 토큰들이 query일 때 → 어디를 보는지 평균
    if not tok_span:
        return tokens, tok_span, None

    focus = A[tok_span, :].mean(dim=0)  # (seq,)

    if SANITIZE:
        # 자기 자신/문장 시작(0번) 억제 후 재정규화
        focus = focus.clone()
        if len(tokens) > 0:
            focus[0] = 0.0
        for i in tok_span:
            focus[i] = 0.0
        s = float(focus.sum())
        if s > 0:
            focus = focus / s

    return tokens, tok_span, focus

def print_topk(tokens, tok_span, focus, k=10, title=""):
    print("\n" + "="*80)
    print(title)
    print("토큰:", tokens)
    print("대상 토큰 인덱스:", tok_span)
    if focus is None:
        print("※ 대상 표현을 토큰으로 찾지 못했습니다.")
        return
    # 상위 k개 인덱스
    topk = torch.topk(focus, min(k, focus.numel()))
    idxs = topk.indices.tolist()
    vals = topk.values.tolist()
    print(f"Top-{k} attention targets (token, score):")
    for i, v in zip(idxs, vals):
        print(f"{i:>3}  {tokens[i]:<12}  {v:.6f}")

if __name__ == "__main__":
    for sent, phrase in zip(SENTS, TARGETS):
        tokens, span, focus = get_attn_scores(sent, phrase)
        title = f"[문장] {sent}\n[표현] '{phrase}' → 레이어={LAYER}, 헤드={HEADS}, sanitize={SANITIZE}"
        print_topk(tokens, span, focus, k=TOPK, title=title)
