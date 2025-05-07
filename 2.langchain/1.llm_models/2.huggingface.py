# https://python.langchain.com/docs/integrations/llms/huggingface_endpoint

# pip install -U huggingface_hub langchain_huggingface

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


load_dotenv(dotenv_path='../.env')

# Hugging Face Inference API 클라이언트 생성 - HF에 API로 연동해서 추론
client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.3")

# 프롬프트 실행
prompt = "What are good fitness tips?"
response = client.text_generation(prompt, max_new_tokens=128, temperature=0.5)

# 결과 출력
print(response)
