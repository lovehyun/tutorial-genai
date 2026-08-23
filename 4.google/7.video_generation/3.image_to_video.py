# pip install google-genai python-dotenv
# 공식 문서: https://ai.google.dev/gemini-api/docs/veo
#
# 이미지 → 영상 — 정지 이미지 한 장을 첫 프레임으로 주고, "그 다음에 무슨 일이 일어날지"만
# 프롬프트로 지시한다. 5.image_generation에서 만든 이미지를 그대로 이어받을 수 있다 —
# 이미지 생성과 영상 생성이 한 파이프라인으로 연결되는 지점이다.
#
# 먼저 실행: ../5.image_generation/2.image_gen.py (generated_1.png를 만들어둬야 한다)

import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

image_path = "../5.image_generation/generated_1.png"
if not os.path.exists(image_path):
    raise FileNotFoundError(
        f"{image_path} 없음 — 먼저 ../5.image_generation/2.image_gen.py를 실행해서 이미지를 만들어라."
    )

with open(image_path, "rb") as f:
    image_bytes = f.read()

# [관전 포인트 1] image= 로 첫 프레임을 고정한다 — 로봇/도서관 구도가 그대로 시작점이 된다.
start_image = types.Image(image_bytes=image_bytes, mime_type="image/png")

# 가격 출처: https://ai.google.dev/gemini-api/docs/pricing (Veo 3.1 Standard 표, 2026-08 확인)
PRICE_PER_SECOND = 0.40  # 720p/1080p, 오디오 포함가 (2026-08 기준)
duration_seconds = 8

start_time = time.time()
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    source=types.GenerateVideosSource(
        prompt="로봇이 책장을 천천히 넘기고, 카메라가 로봇 얼굴로 서서히 줌인한다",
        image=start_image,  # [관전 포인트 2] 텍스트만으로 생성할 때와 달리 구도/캐릭터가 고정된다
    ),
    config=types.GenerateVideosConfig(duration_seconds=str(duration_seconds)),
)

while not operation.done:
    print("영상 생성 중...")
    time.sleep(10)
    operation = client.operations.get(operation)
elapsed = time.time() - start_time

# [관전 포인트 3] API 응답엔 소요 시간·비용 필드가 없다 — 우리가 요청한 duration_seconds로 직접
# 계산하고, 실제 소요 시간은 time.time()으로 직접 잰다.
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("generated_from_image.mp4")

cost = duration_seconds * PRICE_PER_SECOND
print("영상 저장: generated_from_image.mp4")
print(f"소요 시간: {elapsed:.1f}초 | 예상 비용: ${cost:.2f} ({duration_seconds}초 x ${PRICE_PER_SECOND}/초)")
