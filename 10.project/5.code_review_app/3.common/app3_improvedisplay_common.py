import os
import re
import requests
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

# 환경변수 로드
load_dotenv()

app = Flask(__name__, static_folder='public', static_url_path='')

# API 클라이언트
openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def convert_github_url_to_raw(url):
    """
    GitHub 파일 URL (예: https://github.com/user/repo/blob/branch/path/to/file.py)
    을 raw 파일 URL (예: https://raw.githubusercontent.com/user/repo/branch/path/to/file.py)로 변환합니다.
    """
    # 예: https://github.com/user/repo/blob/branch/path/to/file.py
    # prefix = "https://github.com/"
    # if url.startswith(prefix):
    #     path = url[len(prefix):]  # 'user/repo/blob/branch/path/to/file.py'
    #     parts = path.split('/')
    #     if len(parts) >= 5 and parts[2] == "blob":
    #         user = parts[0]
    #         repo = parts[1]
    #         branch = parts[3]
    #         file_path = "/".join(parts[4:])
    #         return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"
    # return url  # 포맷이 맞지 않으면 원래 URL 반환

    # 정규표현식으로 처리
    pattern = r"https://github.com/(.+)/blob/(.+)"
    match = re.match(pattern, url)
    if match:
        return f"https://raw.githubusercontent.com/{match.group(1)}/{match.group(2)}"
    return url

def add_line_numbers(code):
    lines = code.splitlines()
    return "\n".join([f"{i+1:4d}: {line}" for i, line in enumerate(lines)])

@app.route("/")
def index():
    return send_from_directory(app.static_folder, 'index3.html')

@app.route("/api/check", methods=["POST"])
def check_code():
    data = request.get_json()
    github_url = data.get("github_url")
    provider = data.get("provider", "openai")  # 기본은 openai

    if not github_url:
        return jsonify({"error": "github_url 필드가 필요합니다."}), 400

    # 1. 주소 변환
    raw_url = convert_github_url_to_raw(github_url)

    # 2. 요청
    try:
        resp = requests.get(raw_url)
        resp.raise_for_status()
        code = resp.text
    except Exception as e:
        return jsonify({"error": f"파일을 가져오는 중 에러 발생: {e}"}), 500

    # 3. 소스코드에 줄번호 추가
    numbered_code = add_line_numbers(code)

    # 4. 분석
    prompt = (
        "다음 소스코드에서 보안 취약점을 분석해줘.\n"
        "각 취약점에 대해 해당 코드의 라인 번호, 코드 스니펫, 취약점 설명과 "
        "개선 방안을 마크다운 형식의 리스트로 출력해줘.\n"
        "단 '#' 으로 시작하는 주석코드는 무시해도 돼.\n\n"
        "소스코드:\n"
        "------------------------------\n"
        f"{numbered_code}\n"
        "------------------------------"
    )

    print("모델 요청: ", provider)
    
    try:
        if provider == "openai":
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 보안 코드 분석 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
            )
            analysis = response.choices[0].message.content
        elif provider == "anthropic":
            response = anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            analysis = response.content[0].text
        else:
            analysis = "아직 구현되지 않은 모델입니다."
            
    except Exception as e:
        return jsonify({"error": f"{provider.upper()} API 호출 중 에러 발생: {e}"}), 500

    return jsonify({
        "code": code,
        "analysis": analysis
    })

if __name__ == "__main__":
    app.run(debug=True)
