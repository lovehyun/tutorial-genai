# 이미지 분석(Vision) 앱 - 2단계: API 분리 + UI 디자인 개선
# pip install flask openai python-dotenv
#
# 1단계 대비 새로 추가된 것:
#   - 페이지 제공(/)과 이미지 처리(/generate)를 별도 라우트로 분리한다.
#   - 결과를 페이지 통째로 다시 그리지 않고 JSON으로 반환 → 프론트가 fetch로 받아 표시.
#   - UI 디자인 개선은 프론트엔드(static/)에 있다.

import os
import base64
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# [관전 포인트] '/'는 페이지만 제공한다 (1단계처럼 POST를 겸하지 않는다)
@app.route("/")
def index():
    return render_template("index.html")

# [관전 포인트] 이미지 처리는 별도 API 엔드포인트로 — 결과를 JSON으로 반환한다
@app.route("/generate", methods=["POST"])
def generate():
    image_file = request.files.get("image")
    if not image_file:
        return jsonify({"error": "No image provided"}), 400

    # base64 Data URL로 변환 (mimetype을 실제 파일 형식으로 지정)
    mime_type = image_file.mimetype or "image/jpeg"
    image_bytes = image_file.read()
    base64_data = base64.b64encode(image_bytes).decode()
    data_url = f"data:{mime_type};base64,{base64_data}"

    # GPT-4o Vision 요청
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "이 이미지를 설명해줘"},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
            }
        ],
        max_tokens=300
    )

    answer = response.choices[0].message.content
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
