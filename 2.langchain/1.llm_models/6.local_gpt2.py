# pip install transformers torch

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# 모델 이름 (로컬 캐시에 다운로드됨)
model_name = "gpt2"

# 토크나이저 및 모델 로드
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 텍스트 생성 파이프라인 생성
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=128, # 출력 토큰 수만 제한
    temperature=0.7,
    # repetition_penalty=1.2,        # 반복 억제
    # no_repeat_ngram_size=3,        # 3단어 이상 반복 금지
    pad_token_id=tokenizer.eos_token_id,  # gpt2는 pad_token 없음, 중간 오류 방지
    do_sample=True
)

# 질문 프롬프트
prompt = "What are good fitness tips?"

# 텍스트 생성
result = generator(prompt)[0]["generated_text"]

# 출력
print(f"Prompt: {prompt}")
print(f"Answer: {result}")
