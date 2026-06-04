# pip install anthropic python-dotenv
#
# 중급 2: PDF/문서 입력 — document 블록으로 PDF 를 통째로 넣어 질문한다.
# source 는 base64(로컬 파일) / url / text 를 지원.
# (실행하려면 같은 폴더에 doc.pdf 를 두거나 경로를 바꾸세요)

import os
import base64
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 로컬 PDF 를 base64 로 인코딩
with open("doc.pdf", "rb") as f:
    pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

msg = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=800,
    messages=[{
        "role": "user",
        "content": [
            {"type": "document", "source": {
                "type": "base64", "media_type": "application/pdf", "data": pdf_data}},
            {"type": "text", "text": "이 문서의 핵심을 3줄로 요약해줘."},
        ],
    }],
)
print(next((b.text for b in msg.content if b.type == "text"), ""))

# 인터넷에 있는 PDF 라면 base64 대신 URL 로:
#   {"type": "document", "source": {"type": "url", "url": "https://.../doc.pdf"}}
