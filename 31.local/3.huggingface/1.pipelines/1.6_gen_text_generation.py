from transformers import pipeline

# 텍스트 생성 모델 (GPT-2 사용)
model_name = "gpt2"

text_generator = pipeline("text-generation", model=model_name)

# 문장 생성 실행
result = text_generator("Once upon a time,", max_length=50)[0]
# result = text_generator("Once upon a time,", max_length=50, truncation=True)[0]

# 결과 출력
print(result["generated_text"])


# from transformers import AutoTokenizer

# tokenizer = AutoTokenizer.from_pretrained(model_name)
# result = text_generator(
#     "Once upon a time,",
#     max_length=50,
#     truncation=True,
#     pad_token_id=tokenizer.eos_token_id
# )[0]

# print(result["generated_text"])
