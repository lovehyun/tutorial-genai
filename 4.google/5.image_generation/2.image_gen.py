# pip install google-genai python-dotenv
#
# 이미지 생성 — Interactions API + gemini-2.5-flash-image.
#
# 1.image_gen(deprecated).py 가 쓰던 Imagen 3(`imagen-3.0-generate-002`,
# `client.models.generate_images()`)는 **2026-08-17부로 서비스 종료**됐다. 지금은 Gemini가
# 이미지 생성까지 하나로 통합했다 — 별도 이미지 전용 모델(Imagen)이 아니라
# **일반 Gemini 모델이 이미지도 낸다.** 두 파일을 나란히 비교해보면 뭐가 바뀌었는지 바로 보인다.
#
# API도 함께 바뀌었다: 예전엔 client.models.generate_images(...) 였는데, 지금은
# 2025-12에 나온 새 통합 인터페이스 client.interactions.create(...) 를 쓰는 게 현재 권장 방식이다
# (대화 이어가기가 필요한 3.conversational_editing.py 에서 왜 이게 더 나은지 바로 이어진다).

import os
import base64
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# [관전 포인트] input에 텍스트 프롬프트만 넣으면 된다 — 이미지 생성 여부는 모델이 알아서 판단한다.
interaction = client.interactions.create(
    model="gemini-2.5-flash-image",
    input="아늑한 도서관에서 책을 읽는 귀여운 로봇, 디지털 아트 스타일",
)

if interaction.output_image:
    image_bytes = base64.b64decode(interaction.output_image.data)
    with open("generated_1.png", "wb") as f:
        f.write(image_bytes)
    print(f"이미지 저장: generated_1.png ({len(image_bytes)} bytes)")
else:
    # 모델이 이미지 대신 텍스트로만 답했을 수도 있다(예: 정책상 생성 불가한 요청)
    print("이미지가 생성되지 않았습니다. 텍스트 응답:", interaction.output_text)
