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
