# pip install python-dotenv pillow requests

import requests
import base64
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 주소 구성
host = os.getenv("SD_API_HOST")
port = os.getenv("SD_API_PORT", "7860")
API_URL = f"{host}:{port}/sdapi/v1/txt2img"

# 프롬프트 설정
prompts = {
    # 1. 풍경 (Landscape)
    "landscape": "a vast mountain range with a river flowing through it, sunrise, misty, cinematic lighting, ultra detailed",
    # 2. 사이버펑크 도시 (Cyberpunk)
    "cyberpunk": "a cyberpunk city street at night, neon lights, rain, reflections on the ground, cinematic atmosphere, ultra detailed",
    # 3. 애니메이션/미소녀 스타일 (Anime Girl)
    "anime": "a beautiful anime girl with silver hair and blue eyes, wearing a futuristic school uniform, standing under cherry blossoms, 4k anime style, soft lighting",
    # 4. 스팀펑크 로봇 (Steampunk)
    "steampunk": "a steampunk mechanical robot with brass gears and steam vents, standing in a foggy Victorian city, detailed concept art",
    # 5. 중세 판타지 기사 (Fantasy Knight)
    "fantasy_knight": "a fantasy knight in golden armor holding a glowing sword, standing in a battlefield, dramatic lighting, cinematic composition",
    # 6. 우주/은하 배경 (Sci-fi Space)
    "space": "a futuristic spaceship flying through a nebula, stars and galaxies in the background, science fiction art, highly detailed",
    # 7. 3D 캐릭터 컨셉 (3D Character Render)
    "cartoon_3d": "3D render of a stylized cartoon cat character, Pixar style, high poly, detailed fur, studio lighting",
    # 8. 로고/심볼 스타일 (Minimal Logo)
    "minimal_logo": "minimal logo of a fox with geometric lines and bold shapes, black and orange color, white background",
    # 9. 고전 미술풍 인물화 (Renaissance Style Portrait)
    "portrait": "a renaissance style oil painting of a noble woman, detailed face, rich textures, baroque lighting, realistic skin",
    # 10. 테스트용 가벼운 프롬프트 (Low VRAM 테스트용)
    "simple_cat": "a cat sitting on a windowsill, sunny day, cartoon style"
}

payload = {
    "prompt": prompts["space"],
    "negative_prompt": "low quality, blurry, deformed, bad anatomy, watermark, text, cropped, worst quality",
    "steps": 30,
    "cfg_scale": 8,
    "width": 512,
    "height": 512,
}

# API 요청
response = requests.post(API_URL, json=payload)
response.raise_for_status()

# 결과 이미지 디코딩
image_data = response.json()["images"][0]
image = Image.open(BytesIO(base64.b64decode(image_data)))

# 이미지 보기 및 저장
image.show()
image.save("output.png")
