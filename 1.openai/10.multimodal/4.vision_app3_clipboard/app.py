# 이미지 분석(Vision) 앱 - 3단계: 질문 입력 + 클립보드 붙여넣기
# pip install flask openai python-dotenv
#
# 2단계 대비 새로 추가된 것:
#   - 이미지뿐 아니라 '사용자 질문'을 함께 받는다 (/ask 엔드포인트).
#     → "이 이미지를 설명해줘" 고정이 아니라, 사용자가 원하는 것을 물을 수 있다.
#   - 클립보드 이미지 붙여넣기(Ctrl+V)는 프론트엔드(static/)에 구현돼 있다.

import os, base64
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    # [관전 포인트] 2단계와 달리 question(폼 텍스트)도 함께 받는다
    question = request.form.get("question", "").strip()
    image_file = request.files.get("image")

    if not question or not image_file:
        return jsonify({"error":"질문과 이미지를 모두 보내야 합니다."}), 400

    mime = image_file.mimetype or "image/jpeg"
    b64 = base64.b64encode(image_file.read()).decode()
    data_url = f"data:{mime};base64,{b64}"

    # [관전 포인트] messages를 둘로 — ① 사용자 질문  ② 그 질문을 이미지와 함께 전달
    resp = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"user","content":question},
            {"role":"user","content":[
                {"type":"text","text":"위 질문을 이 이미지로 답해줘"},
                {"type":"image_url","image_url":{"url":data_url}}
            ]}
        ],
        max_tokens=400
    )
    answer = resp.choices[0].message.content
    return jsonify({"answer":answer})

if __name__=="__main__":
    app.run(debug=True)
