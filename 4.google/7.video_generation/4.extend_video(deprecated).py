# ⚠️ 이 파일은 실행하면 DeprecationWarning이 뜹니다 — 학습 히스토리로 보존합니다.
#
# generate_videos()에 prompt=/image=/video=를 직접 넘기는 방식(아래 코드)은 deprecated입니다:
#   DeprecationWarning: The generate_videos method with prompt/image/video arguments is
#   deprecated and will be removed in a future major release (not before 2026-07-31).
#   Please use the source argument instead.
#
# "not before 2026-07-31"이라고 적혀 있는데 오늘(2026-08-23 기준)은 이미 그 날짜를 지났다 —
# 즉 제거 가능 시점에 이미 들어섰다는 뜻이다. 지금 당장 못 쓰는 건 아니고(경고만 뜨고 실제로
# 실행은 된다 — generated_extended.mp4가 실제로 생성됨을 확인했다), 그래서 Imagen 3처럼
# 파일을 통째로 죽이지 않고 "동작하되 경고가 뜨는" 상태로 남겨둔다. 현재 권장 방식은 → 5.extend_video.py
#
# 무엇이 바뀌었는지 비교해보라:
#   - 예전: generate_videos(model=..., prompt=..., video=..., config=...)
#   - 지금: generate_videos(model=..., source=types.GenerateVideosSource(prompt=..., video=...), config=...)
#
# pip install google-genai python-dotenv
# 공식 문서: https://ai.google.dev/gemini-api/docs/veo
#
# 영상 이어붙이기(Extend) — 이미 만든 영상 뒤에 새 장면을 이어서 늘린다.
# 한 번에 최대 8초라 그 이상 필요한 이야기(장면 전환, 후속 액션)는 여러 번 나눠서 이어 만든다 —
# 5.image_generation의 previous_interaction_id로 같은 이미지를 계속 편집하던 것과 같은 발상을
# 영상에 적용한 것이다.
#
# ⚠️ 확장(extend)은 현재 720p로만 지원된다. ⚠️ 호출을 두 번 하므로 비용도 두 배로 든다.

import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def wait(operation):
    while not operation.done:
        print("생성 중...")
        time.sleep(10)
        operation = client.operations.get(operation)
    return operation


# 1) 첫 8초
op1 = wait(client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="로봇이 도서관 창밖을 바라본다, 저녁 노을이 지고 있다",
))
video1 = op1.response.generated_videos[0]

# [관전 포인트] video= 에 직전 결과를 넘기면, 그 마지막 장면에서 자연스럽게 이어지는 다음
# 장면을 생성한다 — 완전히 새로 만드는 게 아니라 "이어서" 만든다.
op2 = wait(client.models.generate_videos(
    model="veo-3.1-generate-preview",
    video=video1.video,
    prompt="로봇이 자리에서 일어나 창문을 닫는다",
    config=types.GenerateVideosConfig(resolution="720p"),  # 확장은 720p만 지원
))
video2 = op2.response.generated_videos[0]

client.files.download(file=video2.video)
video2.video.save("generated_extended.mp4")
print("영상 저장: generated_extended.mp4 (총 약 16초)")
