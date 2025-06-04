import os
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv(dotenv_path='../.env')

# 토큰 여러 변수명으로 확인
token = (os.getenv('HUGGINGFACEHUB_API_TOKEN') or 
         os.getenv('HF_TOKEN') or 
         os.getenv('HUGGINGFACE_API_TOKEN'))

print(f"토큰 확인: {token[:10] if token else 'None'}...")

# 모델 0.1/0.2 는 서버에서 삭제 됨. 0.3은 text_generation 용도가 아니고 chat_completion 방식임
model = "mistralai/Mistral-7B-Instruct-v0.2"

# Mistral 형식의 프롬프트 템플릿 사용
formatted_prompt = "<s>[INST] What are good fitness tips? [/INST]"

def try_inference_client():
    """InferenceClient로 시도"""
    print("=== InferenceClient 시도 ===")
    
    try:
        client = InferenceClient(model=model, token=token)
        
        response = client.text_generation(
            formatted_prompt,
            max_new_tokens=128,
            temperature=0.5,
            do_sample=True,
            repetition_penalty=1.1,
            stream=False
        )
        
        print("✅ InferenceClient 성공:")
        print(response)
        return True
        
    except Exception as e:
        print(f"❌ InferenceClient 실패: {type(e).__name__}: {str(e)}")
        return False

def try_direct_api():
    """직접 HTTP API 호출"""
    print("\n=== 직접 HTTP API 시도 ===")
    
    if not token:
        print("❌ 토큰이 없습니다!")
        return False
    
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "inputs": formatted_prompt,
        "parameters": {
            "max_new_tokens": 128,
            "temperature": 0.5,
            "do_sample": True,
            "repetition_penalty": 1.1,
            "return_full_text": False
        }
    }
    
    try:
        print("HTTP API 요청 중...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', 'No text generated')
                print("✅ 직접 API 성공:")
                print(generated_text)
                return True
            else:
                print(f"예상치 못한 응답: {result}")
                return False
                
        elif response.status_code == 503:
            print("⏳ 모델 로딩 중. 잠시 후 다시 시도해주세요.")
            return False
            
        elif response.status_code == 429:
            print("⚠️ 요청 한도 초과")
            return False
            
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ HTTP API 오류: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("Mistral v0.2 [INST] 형식 테스트\n")
    
    # 방법 1: InferenceClient 시도
    if try_inference_client():
        print("\nInferenceClient로 성공!")
        return
    
    # 방법 2: 직접 HTTP API 시도
    if try_direct_api():
        print("\n직접 HTTP API로 성공!")
        return
    
    # 둘 다 실패한 경우
    print("\n❌ 모든 방법 실패")

if __name__ == "__main__":
    main()


# 참고 - 다양한 프롬프트 문법 스타일 비교
# 1. GPT-2 (형식 불필요)
prompt = "What are good fitness tips?"
# 2. ChatGPT/OpenAI 형식  
messages = [{"role": "user", "content": "What are good fitness tips?"}]
# 3. Mistral 형식
prompt = "<s>[INST] What are good fitness tips? [/INST]"
# 4. Claude 형식 (Anthropic)
prompt = "Human: What are good fitness tips?\n\nAssistant:"
