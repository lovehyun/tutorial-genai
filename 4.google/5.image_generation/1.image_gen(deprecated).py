# 🛑 이 파일은 더 이상 동작하지 않습니다 — 학습 히스토리로만 보존합니다.
#
# Imagen 3(`imagen-3.0-generate-002`)와 `client.models.generate_images()`는
# **2026-08-17부로 서비스 종료**됐습니다. 이 코드를 그대로 실행하면 404/model-not-found 에러가 납니다.
#
# 무엇이 바뀌었는지 비교해보세요:
#   - 모델: 이미지 전용 Imagen → 범용 Gemini 모델(`gemini-2.5-flash-image`)이 이미지까지 생성
#   - API : client.models.generate_images() → client.interactions.create()
#   - 응답: response.generated_images[i].image.image_bytes → interaction.output_image.data(base64)
#
# 현재 동작하는 버전은 → 2.image_gen.py

# pip install google-genai python-dotenv Pillow

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Imagen 3 모델로 이미지 생성
response = client.models.generate_images(
    model="imagen-3.0-generate-002",
    prompt="A cute robot reading a book in a cozy library, digital art style",
    config=types.GenerateImagesConfig(
        number_of_images=1,
        aspect_ratio="1:1",  # 1:1, 3:4, 4:3, 9:16, 16:9
    ),
)

# 생성된 이미지 저장
for i, image in enumerate(response.generated_images):
    img = Image.open(BytesIO(image.image.image_bytes))
    filename = f"generated_{i+1}.png"
    img.save(filename)
    print(f"이미지 저장: {filename} ({img.size[0]}x{img.size[1]})")
