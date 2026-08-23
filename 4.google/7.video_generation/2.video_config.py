# pip install google-genai python-dotenv
# 공식 문서: https://ai.google.dev/gemini-api/docs/veo
#
# 분량 조정 · 디테일 제어 — GenerateVideosConfig로 길이/화면비/해상도/제외할 요소까지 지정한다.
#
# 1.video_generation.py는 기본값(프롬프트만)으로 생성했다. "몇 초짜리로", "세로로 찍어줘",
# "이런 건 나오면 안 돼" 같은 정량적 제어는 config로 한다. 카메라 워크·씬 전환 같은 "디테일"은
# 여전히 프롬프트 텍스트로 지시한다 — 이미지 생성과 마찬가지로 자연어가 곧 컨트롤이다.
#
# ⚠️ 비용 주의: duration_seconds가 길수록, resolution이 높을수록 비용이 커진다(1.video_generation.py
# README 참고). 1080p/4k는 8초 고정이다.
#
# [관전 포인트 0] API 응답엔 비용·소요 시간 필드가 없다 — 우리가 요청한 duration_seconds로
# 직접 계산하고, 소요 시간은 time.time()으로 직접 잰다(1.video_generation.py와 동일한 이유).

import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 가격 출처: https://ai.google.dev/gemini-api/docs/pricing (Veo 3.1 Standard 표, 2026-08 확인)
PRICE_PER_SECOND = 0.40  # 720p/1080p, 오디오 포함가 (2026-08 기준)
duration_seconds = 8

start_time = time.time()
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    source=types.GenerateVideosSource(
        prompt=(
            "붐비는 서울 야시장, 카메라가 포장마차를 따라 천천히 옆으로 이동(트래킹 샷), "
            "네온사인 불빛, 사람들의 웃음소리와 시장 소음, 저녁 시간대"
        ),
    ),
    config=types.GenerateVideosConfig(
        duration_seconds=str(duration_seconds),  # [관전 포인트 1] 4 / 6 / 8초 중 선택 — 분량 조정은 여기서
        aspect_ratio="9:16",    # 세로 영상(쇼츠/릴스용). 기본은 16:9
        negative_prompt="텍스트, 자막, 워터마크, 흐릿한 화면",  # [관전 포인트 2] 안 나왔으면 하는 요소
        seed=42,                # 같은 seed → 비슷한 결과 재현(완전 동일 보장은 아님)
    ),
)

while not operation.done:
    print("영상 생성 중...")
    time.sleep(10)
    operation = client.operations.get(operation)
elapsed = time.time() - start_time

video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("generated_market.mp4")

cost = duration_seconds * PRICE_PER_SECOND
print("영상 저장: generated_market.mp4")
print(f"소요 시간: {elapsed:.1f}초 | 예상 비용: ${cost:.2f} ({duration_seconds}초 x ${PRICE_PER_SECOND}/초)")
