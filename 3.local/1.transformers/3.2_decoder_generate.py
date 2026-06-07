# (3단계) 디코더 모델 — GPT-2 로 텍스트 생성
# pip install transformers torch
#
# 3.1(인코더/빈칸채우기) 짝꿍: 이 파일은 '디코더(생성형)' GPT-2 를 본다.
#   디코더는 2.2 에서 본 '다음 토큰 뽑기' 를 끝까지 반복해 문장을 잇는다.
#   여기선 generate() 로 그 반복을 한 번에 돌린다. (전략 비교는 다음 4.1)

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# [관전 포인트 1] text-generation 파이프라인 = 토큰화 + generate + 디코딩을 한 번에
#   GPT-2 는 pad_token 이 없어 pad_token_id 를 eos 로 지정해 경고/오류를 막는다(1.2 참고).
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=60,                    # '생성할' 토큰 수 (입력 길이와 별개)
    pad_token_id=tokenizer.eos_token_id,
)

prompt = "What are good fitness tips?"

# [관전 포인트 2] greedy(기본) vs 샘플링 — 같은 프롬프트, 다른 성격의 출력
print("=== greedy (do_sample=False) — 항상 같은 결과, 보수적 ===")
print(generator(prompt, do_sample=False)[0]["generated_text"])

print("\n=== sampling (do_sample=True, temperature=0.8) — 매번 다르고 창의적 ===")
print(generator(prompt, do_sample=True, temperature=0.8)[0]["generated_text"])

# 정리:
#   - 디코더 생성 = 다음 토큰을 골라 붙이기를 max_new_tokens 만큼 반복
#   - do_sample / temperature / top_k / top_p 가 '어떻게 고르냐' 를 바꾼다
#   - 다음(4.1): 이 디코딩 전략들을 나란히 비교한다
