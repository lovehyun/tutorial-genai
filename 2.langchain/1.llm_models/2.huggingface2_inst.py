from dotenv import load_dotenv
from huggingface_hub import InferenceClient
load_dotenv(dotenv_path='../.env')

client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.3")

# Mistral 형식의 프롬프트 템플릿 사용
formatted_prompt = """<s>[INST] What are good fitness tips? [/INST]"""

# text_generation 대신 text_generation_stream 사용
response_stream = client.text_generation(
    formatted_prompt,
    max_new_tokens=128,
    temperature=0.5,
    do_sample=True,
    repetition_penalty=1.1,
    stream=False  # 스트리밍 비활성화
)

# 결과 출력
print(response_stream)
