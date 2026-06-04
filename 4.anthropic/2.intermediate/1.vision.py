# pip install anthropic python-dotenv
#
# 중급 1: 비전(vision) — 이미지를 입력으로 넣어 분석한다.
# content 리스트에 image 블록 + text 블록을 함께 넣는다.
# 이미지 주는 법 2가지: 로컬 파일 base64(권장, 안정적) 또는 URL.
# (실행하려면 같은 폴더에 image.png 를 두거나 경로를 바꾸세요)

import os
import base64
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# (A) 로컬 파일을 base64 로 인코딩 — 가장 안정적
with open("image.png", "rb") as f:
    img_data = base64.standard_b64encode(f.read()).decode("utf-8")

msg = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=500,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {
                "type": "base64", "media_type": "image/png", "data": img_data}},
            {"type": "text", "text": "이 이미지에 뭐가 있어? 한국어로 설명해줘."},
        ],
    }],
)
print(next((b.text for b in msg.content if b.type == "text"), ""))

# (B) 인터넷 URL 이미지 (서버가 그 URL 을 받아올 수 있어야 함)
# msg = client.messages.create(
#     model="claude-sonnet-4-6",
#     max_tokens=500,
#     messages=[{
#         "role": "user",
#         "content": [
#             {"type": "image", "source": {"type": "url", "url": "https://.../image.jpg"}},
#             {"type": "text", "text": "이 이미지를 설명해줘."},
#         ],
#     }],
# )
# print(msg.content[0].text)
