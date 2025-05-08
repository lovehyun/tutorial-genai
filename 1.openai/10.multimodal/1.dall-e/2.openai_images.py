import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 다양한 스타일의 프롬프트 예시 배열
prompts = [
    # 장소, 시간, 스타일, 행동 등을 조합해 더 정교한 이미지 생성 가능
    # 예: "at night", "in watercolor style", "a dog running"

    # 1. 도시 풍경
    "A cyberpunk cityscape at night with neon lights and flying cars",

    # 2. 판타지 캐릭터
    "A wise old wizard with a long white beard casting a spell in a dark forest",

    # 3. 귀여운 동물
    "A cute corgi puppy wearing sunglasses and riding a skateboard",

    # 4. 미래 우주 풍경
    "An alien planet landscape with purple skies, two suns, and floating rocks",

    # 5. 자연 풍경
    "A peaceful mountain lake during sunrise with mist and pine trees",

    # 6. 미술 작품 스타일
    "A portrait of a woman in the style of Van Gogh",

    # 7. 건축 설계 이미지
    "Modern minimalistic house with glass walls surrounded by nature",

    # 8. 음식 사진
    "A delicious Korean bibimbap in a ceramic bowl with colorful vegetables",

    # 9. 기술 관련 아이콘 스타일
    "Flat vector illustration of cloud computing with servers and AI brain",

    # 10. 동화 삽화 스타일
    "A fairytale illustration of a little girl and a dragon in a magical forest"
]

# 이미지 저장 폴더 생성
save_dir = "DATA"
os.makedirs(save_dir, exist_ok=True)

# 이미지 생성 반복
for idx, prompt in enumerate(prompts):
    print(f"\n[{idx+1}] Generating image for prompt: {prompt}")
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",     # 정사각형 이미지
        quality="standard",   # 또는 "hd" (더 비쌈)
        style="vivid"         # "vivid" (선명하고 강렬함) 또는 "natural" (자연스러움)
    )

    image_url = response.data[0].url
    print(f"    → Image URL: {image_url}")

    # 이미지 다운로드 및 저장
    img_data = requests.get(image_url).content
    file_path = os.path.join(save_dir, f"image_{idx+1}.png")
    with open(file_path, "wb") as f:
        f.write(img_data)
    print(f"      Saved to: {file_path}")
    