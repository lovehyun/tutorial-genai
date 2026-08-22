# pip install anthropic python-dotenv
#
# 고급 5: Files API (beta) — 파일을 한 번 업로드하고 file_id 로 여러 번 재사용.
# 같은 문서에 질문을 여러 번 할 때 매번 업로드 안 해도 된다.
# (실행하려면 같은 폴더에 doc.pdf 를 두거나 경로를 바꾸세요)

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 1) 업로드 (beta 기능). 한 번만 올린다.
uploaded = client.beta.files.upload(
    file=("doc.pdf", open("doc.pdf", "rb"), "application/pdf"),
)
print("업로드됨:", uploaded.id)

# 2) file_id 로 참조해서 질문 (재업로드 없이 여러 번)
for q in ["핵심을 3줄로 요약", "결론만 한 문장으로"]:
    resp = client.beta.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": q},
                {"type": "document", "source": {"type": "file", "file_id": uploaded.id}},
            ],
        }],
        betas=["files-api-2025-04-14"],
    )
    print(f"\nQ: {q}")
    print(next((b.text for b in resp.content if b.type == "text"), ""))

# 3) 정리 (필요 시)
# client.beta.files.delete(uploaded.id)
