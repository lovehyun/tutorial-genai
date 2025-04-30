import requests

OLLAMA_HOST = "http://192.168.0.7:11434"
TAGS_ENDPOINT = f"{OLLAMA_HOST}/api/tags"

def check_server_and_list_models():
    try:
        # 서버 상태 확인
        response = requests.get(OLLAMA_HOST)
        if response.status_code == 200:
            print("✅ Ollama is running.")
        else:
            print(f"⚠️ Ollama 서버 응답 코드: {response.status_code}")
            return

        # 모델 목록 조회
        tag_response = requests.get(TAGS_ENDPOINT)
        tag_response.raise_for_status()
        models = tag_response.json().get("models", [])

        if models:
            print("🔍 설치된 모델 목록:")
            for model in models:
                print(f"- {model['name']}")
        else:
            print("⚠️ 설치된 모델이 없습니다.")

    except requests.exceptions.RequestException as e:
        print("❌ Ollama 서버에 접속하거나 모델 정보를 가져오는 데 실패했습니다.")
        print("에러:", e)

# 실행
check_server_and_list_models()
