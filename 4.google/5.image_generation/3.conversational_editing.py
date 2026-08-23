# pip install google-genai python-dotenv
#
# 대화형 이미지 편집 — 같은 이미지를 여러 턴에 걸쳐 "말로" 고쳐나간다.
#
# 2.image_gen.py는 한 번 생성하고 끝났다. 여기서는 previous_interaction_id로 직전 결과를
# 이어받아서, "배경만 바꿔줘" 같은 후속 지시로 그림을 계속 수정한다 — ChatGPT에게 이미지를
# 만들게 한 뒤 "여기서 이것만 바꿔줘"라고 대화하듯 요청하는 것과 같은 경험이다.
#
# 핵심: previous_interaction_id를 넘기면 모델이 이전 이미지의 '내용'을 기억한 채로
#       이번 지시(배경만/색만 등)만 반영한다 — 나머지 요소(로봇·의자·책 등)는 그대로 유지된다.

import os
import base64
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def save_image(interaction, filename):
    if not interaction.output_image:
        print(f"[{filename}] 이미지 없음:", interaction.output_text)
        return
    with open(filename, "wb") as f:
        f.write(base64.b64decode(interaction.output_image.data))
    print(f"이미지 저장: {filename}")


# 1) 첫 생성
turn1 = client.interactions.create(
    model="gemini-2.5-flash-image",
    input="아늑한 도서관에서 책을 읽는 귀여운 로봇, 디지털 아트 스타일",
)
save_image(turn1, "edit_1_original.png")

# [관전 포인트] previous_interaction_id로 turn1을 가리킨다 — "이 그림에서"라는 맥락이 이어진다.
turn2 = client.interactions.create(
    model="gemini-2.5-flash-image",
    input="배경을 노을 지는 하늘로 바꿔줘. 로봇과 의자, 책은 그대로 둬.",
    previous_interaction_id=turn1.id,
)
save_image(turn2, "edit_2_sunset.png")

# 체인을 계속 이어갈 수도 있다 — 이번엔 turn2를 가리킨다.
turn3 = client.interactions.create(
    model="gemini-2.5-flash-image",
    input="로봇 옆에 작은 고양이도 한 마리 앉혀줘.",
    previous_interaction_id=turn2.id,
)
save_image(turn3, "edit_3_with_cat.png")

print("\n👉 세 이미지를 나란히 놓고 비교해볼 것 — 매번 지시한 부분만 바뀌고 나머지는 유지된다.")
