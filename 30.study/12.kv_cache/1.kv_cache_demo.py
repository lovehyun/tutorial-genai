"""
KV 캐시 — 왜 생성할 때마다 처음부터 다시 계산하지 않는가
- 설치: pip install transformers torch matplotlib numpy

GPT류 모델은 토큰을 하나씩 이어붙이며 생성한다("The" → "The cat" → "The cat sat" → ...).
순진하게 하면 매 스텝마다 지금까지의 전체 문장을 처음부터 다시 attention 계산해야 한다 —
그런데 이전 스텝에서 이미 계산한 Key/Value는 앞부분 토큰에 대해서는 **똑같은 값**이다(이미 확정된
과거 토큰이니까). 그래서 그 Key/Value를 "캐시"해두고, 새로 추가된 토큰에 대해서만 계산하면 된다.
이게 KV 캐시다 — 실전 LLM 서빙(vLLM 등)에서 메모리 관리의 핵심이 되는 그 개념이다.
"""
import os
import time
import warnings
import torch
import matplotlib
import matplotlib.pyplot as plt
from transformers import AutoTokenizer, AutoModelForCausalLM

warnings.filterwarnings('ignore', message='Glyph .* missing from font')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Malgun Gothic', 'NanumGothic', 'AppleGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

MODEL_NAME = "gpt2"


def generate_without_cache(model, tokenizer, prompt, num_new_tokens):
    """[관전 포인트 1] 캐시 없이: 매 스텝마다 '지금까지 전체 문장'을 처음부터 다시 forward.
    스텝이 늘어날수록 forward에 들어가는 시퀀스 길이가 계속 길어진다."""
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    step_times = []
    for _ in range(num_new_tokens):
        t0 = time.perf_counter()
        with torch.no_grad():
            # use_cache=False → past_key_values 를 안 쓰고 매번 input_ids 전체를 다시 계산
            outputs = model(input_ids, use_cache=False)
        next_token = outputs.logits[0, -1, :].argmax().unsqueeze(0).unsqueeze(0)
        input_ids = torch.cat([input_ids, next_token], dim=1)
        step_times.append(time.perf_counter() - t0)
    return input_ids, step_times


def generate_with_cache(model, tokenizer, prompt, num_new_tokens):
    """[관전 포인트 2] 캐시 사용: 매 스텝마다 '새로 추가된 토큰 1개'만 forward하고,
    이전 스텝의 Key/Value(past_key_values)를 재사용한다."""
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    past_key_values = None
    step_times = []
    next_input = input_ids
    all_ids = input_ids
    for _ in range(num_new_tokens):
        t0 = time.perf_counter()
        with torch.no_grad():
            outputs = model(next_input, past_key_values=past_key_values, use_cache=True)
        past_key_values = outputs.past_key_values  # 이번 스텝까지의 Key/Value를 캐시에 누적
        next_token = outputs.logits[0, -1, :].argmax().unsqueeze(0).unsqueeze(0)
        all_ids = torch.cat([all_ids, next_token], dim=1)
        next_input = next_token  # [관전 포인트 3] 다음 스텝엔 새 토큰 '1개'만 넣는다 — 문장 전체가 아니라
        step_times.append(time.perf_counter() - t0)
    return all_ids, step_times


def plot_comparison(times_no_cache, times_cache, filename="results/1.kv_cache_timing.png"):
    plt.figure(figsize=(10, 6))
    steps = list(range(1, len(times_no_cache) + 1))
    plt.plot(steps, [t * 1000 for t in times_no_cache], marker="o", label="캐시 없음 (매번 전체 재계산)", color="#c0392b")
    plt.plot(steps, [t * 1000 for t in times_cache], marker="o", label="KV 캐시 사용 (새 토큰만 계산)", color="#27ae60")
    plt.xlabel("생성 스텝 (토큰 번호)")
    plt.ylabel("스텝당 소요 시간 (ms)")
    plt.title("토큰을 생성할수록 문장이 길어질 때 — 스텝당 소요 시간 변화\n"
               "캐시 없음: 스텝이 늘수록 계산량↑ (우상향 경향) / 캐시 사용: 거의 평평")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  저장: {filename}")


def main():
    os.makedirs("results", exist_ok=True)
    print("=" * 60)
    print("  KV 캐시 — 있을 때와 없을 때")
    print("=" * 60)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.eval()

    # [관전 포인트 0] 워밍업 — 첫 forward는 내부 초기화 비용 때문에 유독 느리다(측정과 무관한 잡음).
    #   벤치마크에서 흔히 하는 것처럼, 측정 시작 전에 한 번 버려서 순수 계산 시간만 비교한다.
    _ = model(tokenizer("warmup", return_tensors="pt").input_ids)

    prompt = "The history of artificial intelligence began with early philosophical questions about"
    num_new_tokens = 80

    print(f"\n  모델: {MODEL_NAME}, 프롬프트: '{prompt}', 생성 토큰 수: {num_new_tokens}")

    print("\n[ 1. 캐시 없이 생성 ]")
    print("-" * 40)
    ids_no_cache, times_no_cache = generate_without_cache(model, tokenizer, prompt, num_new_tokens)
    text_no_cache = tokenizer.decode(ids_no_cache[0], skip_special_tokens=True)
    print(f"  총 소요 시간: {sum(times_no_cache):.3f}초")
    print(f"  마지막 스텝: {times_no_cache[-1]*1000:.1f}ms  (첫 스텝: {times_no_cache[0]*1000:.1f}ms)")

    print("\n[ 2. KV 캐시로 생성 ]")
    print("-" * 40)
    ids_cache, times_cache = generate_with_cache(model, tokenizer, prompt, num_new_tokens)
    text_cache = tokenizer.decode(ids_cache[0], skip_special_tokens=True)
    print(f"  총 소요 시간: {sum(times_cache):.3f}초")
    print(f"  마지막 스텝: {times_cache[-1]*1000:.1f}ms  (첫 스텝: {times_cache[0]*1000:.1f}ms)")

    print("\n[ 3. 결과가 똑같은가? ]")
    print("-" * 40)
    same = text_no_cache == text_cache
    print(f"  캐시 없음: {text_no_cache!r}")
    print(f"  캐시 사용: {text_cache!r}")
    print(f"  → 완전히 동일한 문장인가? {same}  (캐시는 '계산을 아끼는 것'이지 '다른 답을 내는 것'이 아니다)")
    speedup = sum(times_no_cache) / sum(times_cache)
    print(f"  → 속도 차이: {speedup:.2f}배 (짧은 문장·작은 모델이라 차이가 작다 — 문장이 길어지고")
    print(f"     모델이 커질수록 이 차이는 극적으로 벌어진다)")

    print("\n[ 4. 시각화 ]")
    print("-" * 40)
    plot_comparison(times_no_cache, times_cache)

    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. KV 캐시가 아끼는 건 "Key/Value 재계산"이지 "Query 재계산"이 아니다:
   - 새 토큰의 Query는 매번 새로 계산해야 한다(당연히 — 새 토큰이니까)
   - 하지만 과거 토큰들의 Key/Value는 한 번 계산되면 절대 안 바뀐다(causal mask 때문에
     과거 토큰은 미래를 못 보므로, 미래 토큰이 추가돼도 과거의 K/V는 영향받지 않는다)
   - 그래서 과거분은 캐시에 저장해두고 재사용, 새 토큰분만 계산하면 된다

2. 캐시 없이는 스텝마다 계산량이 늘어난다(시퀀스가 매번 길어지므로),
   캐시가 있으면 스텝당 계산량이 거의 일정하다(새 토큰 1개분만 계산) — 위 그래프의 우상향 vs 평평선이 그 증거.

3. 결과는 수학적으로 100% 동일하다 — KV 캐시는 "같은 계산을 다른 순서/방식으로 하는 최적화"이지
   근사치나 지름길이 아니다. 그래서 캐시를 켜고 꺼도 생성 결과가 안 바뀐다(위 3번 실험).

4. 실전 연결:
   - 모델이 커지고(수십억 파라미터) 문장이 길어질수록(긴 대화, 긴 문서) 이 캐시가 GPU 메모리를
     대부분 차지한다 — vLLM 같은 고성능 서빙 엔진의 핵심 기술(PagedAttention 등)이 바로 이
     "KV 캐시를 얼마나 효율적으로 관리하는가"의 문제다.
   - `4.langchain/1.quickstart`처럼 매 대화 턴마다 전체 히스토리를 다시 넣는 게 아니라, 실제
     서빙 엔진은 이전 턴의 KV 캐시를 재사용해서 응답 속도를 크게 높인다.
""")


if __name__ == "__main__":
    main()
