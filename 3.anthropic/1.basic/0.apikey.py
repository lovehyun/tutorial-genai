import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# 환경변수에서 API 키 가져오기
api_key = os.getenv("ANTHROPIC_API_KEY")

# API 키 확인
if api_key:
    print("API 키가 성공적으로 로드되었습니다!")
    # API 키의 첫 20자만 표시 (보안)
    print(f"API 키: {api_key[:20]}...")
else:
    print("API 키를 설정해주세요!")
