# curl -X POST http://localhost:5000/api/name -H "Content-Type: application/json" -d '{"product": "educational toys"}'
# curl -X POST http://localhost:5000/api/name -H "Content-Type: application/json" -d "{\"product\": \"educational toys\"}"

import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

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

llm2 = ChatOpenAI(
    temperature=0.9,
    openai_api_key=openai_api_key  # 명시적으로 넘겨주는 방식
)

@app.route("/api/name", methods=["POST"])
def generate_company_name():
    data = request.get_json()
    product = data.get("product", "arcade games")

    prompt = f"What's a good company name that makes {product}?"
    result = llm1.invoke(prompt)
    names = result.strip()
    
    return jsonify({
        "product": product,
        "company_names": names
    })

@app.route("/api/names", methods=["POST"])
def generate_company_names():
    data = request.get_json()
    product = data.get("product", "arcade games")

    prompt = f"What's a good company name that makes {product}?"
    result = llm1.generate([prompt] * 5)
    
    names = [gen[0].text.strip().strip('"') for gen in result.generations]

    return jsonify({
        "product": product,
        "company_names": names
    })

@app.route("/api/names2", methods=["POST"])
def generate_company_names2():
    data = request.get_json()
    product = data.get("product", "arcade games")

    prompt = f"What's a good company name that makes {product}?"
    prompts = [[HumanMessage(content=prompt)] for _ in range(5)]

    result = llm2.generate(prompts)
    
    names = [
        gen[0].message.content.strip().strip('"') 
        for gen in result.generations
    ]
    
    return jsonify({
        "product": product,
        "company_names": names
    })
    
if __name__ == "__main__":
    app.run(debug=True)
