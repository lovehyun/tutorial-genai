# https://python.langchain.com/docs/integrations/llms/huggingface_endpoint

# pip install -U huggingface_hub langchain_huggingface

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv(dotenv_path='../.env')

# Hugging Face Inference API client creation
client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.3")

# Create a conversational prompt with proper formatting for Mistral
messages = [
    {"role": "user", "content": "What are good fitness tips?"}
]

# Use the correct parameters for chat_completion
response = client.chat_completion(
    messages=messages,
    temperature=0.5,
    max_tokens=128  # Instead of max_new_tokens
)

# Output the result
# print(response)

answer_text = response.choices[0].message.content
print(answer_text)
