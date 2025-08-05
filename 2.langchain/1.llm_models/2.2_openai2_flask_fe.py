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
llm1 = OpenAI(
    temperature=0.9,
    openai_api_key=openai_api_key  # 명시적으로 넘겨주는 방식
)

llm2 = OpenAI(
    temperature=0.9,
    openai_api_key=openai_api_key,
    n=5  # 한 번의 호출로 5개 생성
)

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

# 하나의 프롬프트를 5번 복제해서 5번 호출
@app.route("/api/names", methods=["POST"])
def generate_company_names():
    data = request.get_json()
    product = data.get("product", "arcade games")

    prompt = f"What's a good company name that makes {product}?"
    result = llm1.generate([prompt] * 5) # 5번 반복 호출

    names = [gen[0].text.strip().strip('"') for gen in result.generations]
    return jsonify({
        "product": product,
        "company_names": names
    })

# 하나의 프롬프트로 5개의 응답을 주도록 설정한 모델에 1번 호출
@app.route("/api/names2", methods=["POST"])
def generate_company_names_once():
    data = request.get_json()
    product = data.get("product", "arcade games")

    prompt = f"What's a good company name that makes {product}?"

    # llm2는 n=5로 설정되어 있으므로 한 번의 호출로 5개 생성
    result = llm2.invoke(prompt)

    # invoke()는 직접적으로 list를 반환하지 않으므로, `result`는 str 타입
    # 예상 포맷: "Name1, Name2, Name3, Name4, Name5"
    # → 콤마로 분리하여 리스트로 변환
    names = [name.strip().strip('"') for name in result.split(",") if name.strip()]

    return jsonify({
        "product": product,
        "company_names": names
    })

if __name__ == "__main__":
    app.run(debug=True)
