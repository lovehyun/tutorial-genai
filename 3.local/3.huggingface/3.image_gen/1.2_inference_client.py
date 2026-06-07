from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

# .env 파일에서 API 토큰 로드
load_dotenv()
api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Inference 클라이언트 초기화 (모델명은 반드시 지원되는 것 사용)
client = InferenceClient(
    model="black-forest-labs/FLUX.1-dev",
    token=api_token
)

def generate_image(prompt, output_path="output.png"):
    # 이미지 생성
    image_bytes = client.text_to_image(
        prompt=prompt,
        guidance_scale=7.5,
        negative_prompt="low quality, blurry"  # 선택사항
    )
    
    # 이미지 저장
    # image_bytes가 이미 PIL.Image 객체일 가능성이 있음
    if isinstance(image_bytes, Image.Image):
        image = image_bytes
    else:
        image = Image.open(BytesIO(image_bytes))
    image.save(output_path)
    print(f"이미지가 '{output_path}'에 저장되었습니다.")

# 테스트 실행
generate_image("A robot reading a book under a cherry blossom tree")
