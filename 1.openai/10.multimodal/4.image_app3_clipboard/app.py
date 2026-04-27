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
    question = request.form.get("question", "").strip()
    image_file = request.files.get("image")

    if not question or not image_file:
        return jsonify({"error":"질문과 이미지를 모두 보내야 합니다."}), 400

    mime = image_file.mimetype or "image/jpeg"
    b64 = base64.b64encode(image_file.read()).decode()
    data_url = f"data:{mime};base64,{b64}"

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
