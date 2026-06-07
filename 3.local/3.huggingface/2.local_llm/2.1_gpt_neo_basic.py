# GPT-Neo-2.7B 모델 크기: 약 10GB
# GPT-Neo-2.7B는 27억 개의 매개변수를 갖고 있습니다. 이는 매우 큰 모델로, 다양한 언어 이해 및 생성 작업에서 뛰어난 성능을 발휘할 수 있습니다.
# 이 모델은 다양한 웹 텍스트 데이터로 훈련되었습니다. 여기에는 Wikipedia, Common Crawl, Reddit 및 기타 대규모 데이터셋이 포함됩니다.

# pip install transformers torch

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# 모델 이름 지정 (27억 파라미터 모델)
model_name = "EleutherAI/gpt-neo-2.7B"

# 토크나이저와 모델 로드
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")  # GPU 자동 할당

# 텍스트 생성 파이프라인 생성
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=256,             # 응답 길이
    temperature=0.7,                # 창의성 제어
    do_sample=True,                 # 샘플링 활성화
    pad_token_id=tokenizer.eos_token_id  # 중간 경고 방지용 padding 설정
)

# 프롬프트 정의 (명확한 역할 설정 포함)
prompt = """You are a fitness expert. Provide detailed and actionable fitness tips in response to the following question:

What are good fitness tips?

Fitness Tips:"""

# 응답 생성
result = generator(prompt)[0]["generated_text"]

# 결과 출력
print(f"Prompt:\n{prompt}\n")
print(f"Answer:\n{result}")
