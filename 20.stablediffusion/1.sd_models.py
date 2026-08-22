import requests
import os
from dotenv import load_dotenv

# .env 파일에서 서버 주소 불러오기
load_dotenv()
host = os.getenv("SD_API_HOST")
port = os.getenv("SD_API_PORT", "7860")
API_URL = f"{host}:{port}/sdapi/v1/sd-models"

# API 요청
try:
    response = requests.get(API_URL)
    response.raise_for_status()
    models = response.json()

    print("사용 가능한 모델 목록:")
    for model in models:
        print(f"- model_name: {model['model_name']}")
        print(f"  title     : {model['title']}")
        print(f"  hash      : {model.get('hash', '-')}")
        print()

except requests.exceptions.RequestException as e:
    print("모델 목록을 불러오지 못했습니다:", e)
