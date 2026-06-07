# https://huggingface.co/docs/inference-providers/en/tasks/text-to-image
# 실제로 크레딧 차감됨 (무료 크레딧 0.10 중에 0.01 씩)
import requests
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

# Hugging Face Access Token
# API_TOKEN = "hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "image/png"  # 이미지 포맷으로 받기
}

def generate_image(prompt: str, output_path="output.png"):
    payload = {
        "inputs": prompt,
        "parameters": {
            "guidance_scale": 7.5   # guidance_scale은 텍스트 프롬프트에 얼마나 "충실하게" 이미지를 생성할지를 조절하는 하이퍼파라미터
                                    # 1.0 ~ 4.0 : 매우 자유롭게 그림. 프롬프트와는 거리가 멀 수 있음.
                                    # 5.0 ~ 7.5 : 보통 권장값. 적절한 창의성과 텍스트 반영의 균형
                                    # 8.0 ~ 12.0 : 텍스트에 매우 충실하지만 때로는 너무 정형적일 수 있음
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print("Error:", response.status_code)
        print(response.text)
        return

    image = Image.open(BytesIO(response.content))
    image.save(output_path)
    print(f"이미지가 '{output_path}'에 저장되었습니다.")

# 테스트 실행
generate_image("A robot reading a book under a cherry blossom tree")
