# pip install google-genai python-dotenv Pillow

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pathlib import Path

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# ─────────────────────────────────────────────
# 1. URL 이미지 분석
# ─────────────────────────────────────────────
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_uri(
            file_uri="https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png",
            mime_type="image/png",
        ),
        "이 이미지에 무엇이 보이나요? 한국어로 설명해주세요.",
    ],
)
print("URL 이미지 분석:")
print(response.text)

# ─────────────────────────────────────────────
# 2. 로컬 이미지 분석 (파일이 있을 경우)
# ─────────────────────────────────────────────
local_image = Path("sample.png")
if local_image.exists():
    with open(local_image, "rb") as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            "이 이미지를 분석해주세요.",
        ],
    )
    print("\n로컬 이미지 분석:")
    print(response.text)
else:
    print(f"\n로컬 이미지 ({local_image})가 없어 건너뜁니다.")
