# curl -X POST http://localhost:5000/api/name -H "Content-Type: application/json" -d '{"product": "educational toys"}'
# curl -X POST http://localhost:5000/api/name -H "Content-Type: application/json" -d "{\"product\": \"educational toys\"}"

import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

from langchain_openai import OpenAI

# 환경 변수 로드
load_dotenv(dotenv_path='../.env')

# OpenAI 키 확인
openai_api_key = os.environ.get("OPENAI_API_KEY")

# Flask 앱 초기화
app = Flask(__name__)

# LLM 초기화
llm = OpenAI(
    temperature=0.9,
    openai_api_key=openai_api_key  # 명시적으로 넘겨주는 방식
)

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

@app.route("/api/names", methods=["POST"])
def generate_company_names():
    data = request.get_json()
    product = data.get("product", "arcade games")

    prompt = f"What's a good company name that makes {product}?"
    result = llm.generate([prompt] * 5)

    names = [gen[0].text.strip().strip('"') for gen in result.generations]
    return jsonify({
        "product": product,
        "company_names": names
    })

if __name__ == "__main__":
    app.run(debug=True)
