# curl -X POST http://localhost:5000/api/name -H "Content-Type: application/json" -d '{"product": "educational toys"}'
# curl -X POST http://localhost:5000/api/name -H "Content-Type: application/json" -d "{\"product\": \"educational toys\"}"

import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ============================================================
# 환경 변수 로드 (.env 파일 → os.environ 에 반영)
# ============================================================
load_dotenv(dotenv_path='../.env')

# ------------------------------------------------------------
# [참고] 환경변수에서 값 읽는 4가지 방법
# ------------------------------------------------------------
# (1) os.environ.get("KEY")           → 없으면 None 반환 (가장 안전, 많이 씀)
# (2) os.environ.get("KEY", "기본값")  → 없을 때 기본값 지정 가능
# (3) os.environ["KEY"]               → 없으면 KeyError 발생 (반드시 있어야 할 키일 때)
# (4) os.getenv("KEY")                → (1)과 동일. os.getenv("KEY", "기본값") 도 가능
#
# 즉, os.environ.get(...) 과 os.getenv(...) 는 거의 같은 동작이고
# 미리 보장된 키라면 os.environ["KEY"] 가 가장 깔끔합니다.
# ------------------------------------------------------------
openai_api_key = os.environ.get("OPENAI_API_KEY")
# openai_api_key = os.getenv("OPENAI_API_KEY")          # 동일
# openai_api_key = os.environ["OPENAI_API_KEY"]         # 없으면 즉시 KeyError

# Flask 앱 초기화
app = Flask(__name__)

# ============================================================
# LLM 초기화 - API 키를 넘기는 3가지 방법
# ============================================================
# (A) api_key=... (★ 현재 권장)
#     - OpenAI 공식 SDK 와 동일한 파라미터 이름. 짧고 직관적.
# (B) openai_api_key=...
#     - LangChain 의 legacy alias. 여전히 동작하지만 옛 스타일.
# (C) 아무것도 안 넘김
#     - 환경변수 OPENAI_API_KEY 를 자동으로 읽어감 (가장 깔끔)
#     - 단, 환경변수가 반드시 잡혀 있어야 함
# ============================================================

# (A) 현재 권장 방식 — `api_key`
llm1 = OpenAI(
    temperature=0.9,
    api_key=openai_api_key
)

# (B) Legacy alias 방식 — `openai_api_key` (옛날 코드/문서에서 자주 보임)
# llm1 = OpenAI(
#     temperature=0.9,
#     openai_api_key=openai_api_key
# )

# (C) 환경변수 자동 사용 — OPENAI_API_KEY 가 잡혀 있으면 키를 안 넘겨도 됨
# llm1 = OpenAI(temperature=0.9)


# ChatOpenAI 도 동일한 3가지 방식 적용 가능
llm2 = ChatOpenAI(
    temperature=0.9,
    api_key=openai_api_key       # (A) 권장
    # openai_api_key=openai_api_key  # (B) legacy
)
# llm2 = ChatOpenAI(temperature=0.9)  # (C) 환경변수 자동

# /api/name  : Completion 모델(llm1) + invoke 로 회사 이름 1개 생성 (단일 호출)
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

# /api/names : Completion 모델(llm1) + generate 로 같은 prompt 를 5번 배치 호출해 후보 5개 생성
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

# /api/name2 : Chat 모델(llm2) + SystemMessage 로 페르소나 부여 후 회사 이름 1개 생성
@app.route("/api/name2", methods=["POST"])
def generate_company_name2():
    data = request.get_json()
    product = data.get("product", "arcade games")

    prompt = f"What's a good company name that makes {product}?"

    # 시스템 메시지 + 사용자 프롬프트 하나만 전달
    messages = [
        SystemMessage(content="You are a creative branding expert for game companies."),
        HumanMessage(content=prompt)
    ]

    result = llm2.invoke(messages)

    return jsonify({
        "product": product,
        "company_name": result.content.strip().strip('"')
    })

# /api/names2 : Chat 모델(llm2) + SystemMessage 포함 메시지 리스트를 5번 배치 호출해 후보 5개 생성
@app.route("/api/names2", methods=["POST"])
def generate_company_names2():
    data = request.get_json()
    product = data.get("product", "arcade games")

    prompt = f"What's a good company name that makes {product}?"
    
    # 시스템 메시지 포함한 메시지 리스트 5개 생성
    prompts = [[
        SystemMessage(content="You are a creative branding expert for game companies."),
        HumanMessage(content=prompt)
    ] for _ in range(5)]

    result = llm2.generate(prompts)

    # result.generations 는 [prompt별][응답별] 2중 리스트. n=1 이므로 각 prompt 의 0번째 응답만 꺼냄.
    # .strip('"') : LLM이 가끔 응답을 "FunnyCompany" 처럼 따옴표로 감싸서 주므로 양옆 따옴표 제거.
    names = [gen[0].message.content.strip().strip('"') for gen in result.generations]

    return jsonify({
        "product": product,
        "company_names": names
    })


# /api/names3 : Chat 모델 + `n` 파라미터로 한 번의 API 호출에서 후보 n개 생성 (input 토큰 1배, output 토큰만 n배)
# 예) curl -X POST http://localhost:5000/api/names3 -H "Content-Type: application/json" -d "{\"product\": \"educational toys\", \"n\": 3}"
@app.route("/api/names3", methods=["POST"])
def generate_company_names3():
    data = request.get_json()
    product = data.get("product", "arcade games")
    n = int(data.get("n", 5))            # 기본 5개
    n = max(1, min(n, 10))               # 1 ~ 10 사이로 안전하게 clamp

    # 요청마다 n 값이 달라지므로 매 요청마다 인스턴스 생성
    llm_n = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.9,
        n=n,                             # ★ 핵심: 한 번 호출에서 n개 응답
        api_key=openai_api_key
    )

    messages = [
        SystemMessage(content="You are a creative branding expert for game companies."),
        HumanMessage(content=f"What's a good company name that makes {product}?")
    ]

    # 단 1번의 API 호출 → generations[0] 에 n개의 응답이 들어 있음
    result = llm_n.generate([messages])

    names = [
        gen.message.content.strip().strip('"')
        for gen in result.generations[0]
    ]

    return jsonify({
        "product": product,
        "n": n,
        "company_names": names
    })


if __name__ == "__main__":
    app.run(debug=True)
