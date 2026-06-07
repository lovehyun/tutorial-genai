# https://python.langchain.com/docs/integrations/llms/huggingface_endpoint

# pip install -U huggingface_hub langchain_huggingface

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import os

load_dotenv(dotenv_path='../.env')
token = os.getenv('HUGGINGFACEHUB_API_TOKEN')
print(f"토큰 확인됨: {token[:10]}...")
        
def run_gpt2():
    """GPT-2 모델 실행 함수"""
    print("=== GPT-2 Results ===")
    # model = "gpt2"
    model = "distilgpt2"
    client = InferenceClient(model=model, token=token)
    
    # GPT-2는 text_generation 사용
    prompt = "What are good fitness tips? Here are some helpful suggestions:"
    
    try:
        response = client.text_generation(
            prompt=prompt,
            temperature=0.7,
            max_new_tokens=128,
            do_sample=True,
            return_full_text=False,  # 원본 프롬프트 제외하고 생성된 텍스트만 반환
            stream=False  # 명시적으로 스트리밍 비활성화
        )
        
        print("GPT-2 Response:")
        print(response)
        
    except Exception as e:
        # print(f"GPT-2 Error: {e}")
        print(f"GPT-2 상세 오류: {type(e).__name__}: {str(e)}")

def run_mistral():
    """Mistral 모델 실행 함수"""
    print("\n=== Mistral Results ===")
    model = "mistralai/Mistral-7B-Instruct-v0.3"
    client = InferenceClient(model=model)
    
    # Mistral은 chat_completion 사용
    messages = [
        {"role": "user", "content": "What are good fitness tips?"}
    ]
    
    try:
        response = client.chat_completion(
            messages=messages,
            temperature=0.5,
            max_tokens=128
        )
        
        answer_text = response.choices[0].message.content
        print("Mistral Response:")
        print(answer_text)
        
    except Exception as e:
        print(f"Mistral Error: {e}")

if __name__ == "__main__":
    # 두 모델 모두 실행
    run_gpt2()
    run_mistral()
    
    print("\n" + "="*50)
    print("Both models completed!")
