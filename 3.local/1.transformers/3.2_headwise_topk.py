# filename: headwise_topk.py
import re, math
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

MODEL_NAME = "gpt2"  # "gpt2" 또는 "bert-base-uncased"
SENTS = [
    "The homework was redone.",
    "The car is a red one."
]
TARGETS = ["redone", "red one"]  # 각 문장에서 관심 표현
TOPK = 5
SANITIZE = True  # 자기 자신/문장 시작 토큰 가중치 제거

use_decoder = MODEL_NAME.startswith("gpt2")
tok = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
if use_decoder:
    mdl = AutoModelForCausalLM.from_pretrained(MODEL_NAME, output_attentions=True, attn_implementation="eager")
else:
    mdl = AutoModel.from_pretrained(MODEL_NAME, output_attentions=True)
device = "cuda" if torch.cuda.is_available() else "cpu"
mdl.to(device).eval()

def find_char_span(text, phrase):
    m = re.search(re.escape(phrase.lower()), text.lower())
    return (m.start(), m.end()) if m else None

def char_span_to_token_span(offset_mapping, char_span):
    if not char_span: return []
    s_c, e_c = char_span
    ids = []
    for i, (s, e) in enumerate(offset_mapping[0].tolist()):
        if s == e:  # 특수 토큰
            continue
        if not (e <= s_c or e_c <= s):
            ids.append(i)
    return ids

def head_entropy(vec):
    # 정보량(분포 날카로움): 낮을수록 특정 위치에 집중
    v = vec.clone()
    v[v < 1e-12] = 1e-12
    p = v / v.sum()
    return float(-(p * p.log()).sum())

def get_headwise(sentence, phrase):
    enc = tok(sentence, return_tensors="pt", return_offsets_mapping=True, add_special_tokens=True)
    enc = {k: (v.to(device) if hasattr(v, "to") else v) for k, v in enc.items()}
    tokens = tok.convert_ids_to_tokens(enc["input_ids"][0])
    span = char_span_to_token_span(enc["offset_mapping"], find_char_span(sentence, phrase))

    # 모델에는 offset_mapping 제외
    inputs = {"input_ids": enc["input_ids"], "attention_mask": enc.get("attention_mask")}
    if "token_type_ids" in enc:
        inputs["token_type_ids"] = enc["token_type_ids"]

    with torch.no_grad():
        out = mdl(**inputs)

    # attentions: list[L] of (batch, heads, seq, seq)
    A_last = out.attentions[-1][0]  # (heads, seq, seq)
    heads, seq, _ = A_last.shape
    results = []

    for h in range(heads):
        W = A_last[h]  # (seq, seq)
        if not span:
            results.append({"head": h, "topk": [], "entropy": None, "left_mass": None, "right_mass": None})
            continue
        focus = W[span, :].mean(dim=0)  # span을 query로, 어디를 보는지 평균 (seq,)
        if SANITIZE:
            # 문장 시작/자기 자신 제거 후 재정규화
            focus = focus.clone()
            if seq > 0: focus[0] = 0.0
            for i in span: focus[i] = 0.0
            s = float(focus.sum())
            if s > 0: focus /= s

        # 통계: 엔트로피(집중도), 좌/우 시야(인덱스 기준)
        ent = head_entropy(focus) if float(focus.sum()) > 0 else None
        left_mass = float(focus[:span[0]].sum()) if len(span) > 0 else None
        right_mass = float(focus[span[-1]+1:].sum()) if len(span) > 0 else None

        # Top-K
        k = min(TOPK, seq)
        topv, topi = torch.topk(focus, k)
        top = [(int(i), tokens[int(i)], float(v)) for i, v in zip(topi, topv)]
        results.append({"head": h, "topk": top, "entropy": ent, "left_mass": left_mass, "right_mass": right_mass})

    return tokens, span, results

if __name__ == "__main__":
    for sent, phrase in zip(SENTS, TARGETS):
        print("\n"+"="*90)
        print(f"[문장] {sent}")
        print(f"[표현] '{phrase}'")
        tokens, span, heads = get_headwise(sent, phrase)
        print("토큰:", tokens)
        print("대상 토큰 인덱스:", span)
        for item in heads:
            h = item["head"]
            top = item["topk"]
            ent = item["entropy"]
            lm, rm = item["left_mass"], item["right_mass"]
            print(f"\n[Head {h:02d}] entropy={ent:.4f}  left_mass={lm:.3f}  right_mass={rm:.3f}")
            for idx, tokstr, val in top:
                print(f"  - idx={idx:>2}  tok={tokstr:<12}  attn={val:.6f}")
