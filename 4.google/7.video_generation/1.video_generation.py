# pip install google-genai python-dotenv
# 공식 문서: https://ai.google.dev/gemini-api/docs/veo
#
# 동영상 생성(Text-to-Video) — Veo 3.1.
#
# 6.video_understanding이 "영상을 이해하기"였다면, 여기는 반대로 "영상을 만들기"다.
# generate_content()처럼 응답이 바로 오지 않는다 — 영상 생성은 시간이 걸리므로 API가 즉시
# operation(작업) 객체만 돌려주고, 완료될 때까지 폴링(polling)해서 상태를 확인해야 한다.
# 이 비동기 패턴 자체가 지금까지의 동기식 호출과 다른 부분이라 눈여겨볼 것.
#
# ⚠️ 비용 주의: 초당 $0.40(720p/1080p, 오디오 포함가, 2026-08 기준). 실행할 때마다 실제
# 과금이 발생한다 — 테스트는 프롬프트당 한 번만, 꼭 필요할 때만 돌릴 것.
# ⚠️ preview 모델이라 지역/계정에 따라 접근이 제한될 수 있다.
#
# [관전 포인트 0] generate_videos() 응답에는 소요 시간·토큰 수·비용 필드가 없다 — 텍스트 API의
# response.usage_metadata 같은 게 없다. Veo는 초 단위 정찰제라서, 우리가 요청한 길이(아래
# duration_seconds)와 해상도만 알면 비용은 코드에서 직접 계산할 수 있다. 실제 소요 시간은
# API가 알려주지 않으므로 time.time()으로 우리가 직접 잰다.

import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 가격 출처: https://ai.google.dev/gemini-api/docs/pricing (Veo 3.1 Standard 표, 2026-08 확인)
PRICE_PER_SECOND = 0.40  # 720p/1080p, 오디오 포함가 (veo-3.1-generate-preview, 2026-08 기준)
duration_seconds = 8

# [관전 포인트 1] generate_videos()는 결과가 아니라 "작업(operation)"을 즉시 반환한다.
# prompt=를 바로 넘기지 않고 source=GenerateVideosSource(prompt=...)로 감싼다 — 예전엔
# prompt=/image=/video=를 직접 넘겼는데 지금은 deprecated다(4.extend_video(deprecated).py 참고).
start_time = time.time()
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    source=types.GenerateVideosSource(
        prompt="아늑한 도서관에서 책을 읽는 귀여운 로봇, 카메라가 천천히 로봇을 향해 다가간다, 디지털 아트 스타일",
    ),
    config=types.GenerateVideosConfig(duration_seconds=str(duration_seconds)),
)

# [관전 포인트 2] operation.done이 True가 될 때까지 주기적으로 상태를 다시 조회한다.
#   이미지 생성(2.image_gen.py)은 몇 초면 끝나지만, 영상은 수십 초~몇 분씩 걸리기 때문에
#   이런 폴링 구조가 필요하다 — 배치 처리(1.openai/11.batch)와 비슷한 발상이다.
while not operation.done:
    print("영상 생성 중... (약 10초마다 상태 확인)")
    time.sleep(10)
    operation = client.operations.get(operation)
elapsed = time.time() - start_time

# [관전 포인트 3] Veo 3.1은 영상에 오디오까지 자동으로 함께 생성한다 — 별도 TTS/BGM 합성 불필요.
generated_video = operation.response.generated_videos[0]
client.files.download(file=generated_video.video)
generated_video.video.save("generated_video.mp4")

cost = duration_seconds * PRICE_PER_SECOND
print(f"영상 저장: generated_video.mp4 (오디오 포함)")
print(f"소요 시간: {elapsed:.1f}초 | 예상 비용: ${cost:.2f} ({duration_seconds}초 x ${PRICE_PER_SECOND}/초, 실제 청구액은 콘솔에서 확인)")
