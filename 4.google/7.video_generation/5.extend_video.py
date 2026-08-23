# pip install google-genai python-dotenv
# 공식 문서: https://ai.google.dev/gemini-api/docs/veo
#
# 영상 이어붙이기(Extend) — 4.extend_video(deprecated).py와 같은 기능이지만, generate_videos()의
# 현재 권장 인자 형태(source=types.GenerateVideosSource(...))를 쓴다. 예전 prompt=/image=/video=
# 직접 전달 방식은 deprecated 경고가 뜬다 — 자세한 사정은 4.extend_video(deprecated).py 헤더 참고.
#
# ⚠️ 확장(extend)은 현재 720p로만 지원된다. ⚠️ 호출을 두 번 하므로 비용도 두 배로 든다.
#
# [관전 포인트 0] API 응답엔 소요 시간·비용 필드가 없다 — 우리가 요청한 길이(각 세그먼트 8초)로
# 직접 계산하고, 소요 시간은 time.time()으로 직접 잰다.

import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 가격 출처: https://ai.google.dev/gemini-api/docs/pricing (Veo 3.1 Standard 표, 2026-08 확인)
PRICE_PER_SECOND = 0.40  # 720p/1080p, 오디오 포함가 (2026-08 기준)
SEGMENT_SECONDS = 8


def wait(operation):
    start = time.time()
    while not operation.done:
        print("생성 중...")
        time.sleep(10)
        operation = client.operations.get(operation)
    return operation, time.time() - start


# [관전 포인트 1] prompt=를 바로 넘기지 않고 source=GenerateVideosSource(prompt=...)로 감싼다.
op1, elapsed1 = wait(client.models.generate_videos(
    model="veo-3.1-generate-preview",
    source=types.GenerateVideosSource(
        prompt="로봇이 도서관 창밖을 바라본다, 저녁 노을이 지고 있다",
    ),
))
video1 = op1.response.generated_videos[0]

# [관전 포인트 2] 이어붙일 땐 source= 안에 prompt와 video를 함께 넣는다 — image-to-video에서
# image=를 함께 넣던 것과 같은 구조다(3.image_to_video.py 참고).
op2, elapsed2 = wait(client.models.generate_videos(
    model="veo-3.1-generate-preview",
    source=types.GenerateVideosSource(
        prompt="로봇이 자리에서 일어나 창문을 닫는다",
        video=video1.video,
    ),
    config=types.GenerateVideosConfig(resolution="720p"),  # 확장은 720p만 지원
))
video2 = op2.response.generated_videos[0]

client.files.download(file=video2.video)
video2.video.save("generated_extended.mp4")

total_seconds = SEGMENT_SECONDS * 2
cost = total_seconds * PRICE_PER_SECOND
print("영상 저장: generated_extended.mp4 (총 약 16초)")
print(f"소요 시간: 1차 {elapsed1:.1f}초 + 2차 {elapsed2:.1f}초 = {elapsed1 + elapsed2:.1f}초")
print(f"예상 비용: ${cost:.2f} ({total_seconds}초 x ${PRICE_PER_SECOND}/초, 호출 2회 합산)")
