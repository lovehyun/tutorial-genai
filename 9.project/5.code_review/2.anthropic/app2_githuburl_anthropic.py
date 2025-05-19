import os
import re
import requests
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from anthropic import Anthropic

# .env 파일에서 환경변수 로드
load_dotenv()

app = Flask(__name__, static_folder='public', static_url_path='')

# Anthropic API 클라이언트 생성
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def convert_github_url_to_raw(url):
    """
    GitHub 파일 URL (예: https://github.com/user/repo/blob/branch/path/to/file.py)
    을 raw 파일 URL (예: https://raw.githubusercontent.com/user/repo/branch/path/to/file.py)로 변환합니다.
    """
    pattern = r"https://github.com/(.+)/blob/(.+)"
    match = re.match(pattern, url)
    if match:
        return f"https://raw.githubusercontent.com/{match.group(1)}/{match.group(2)}"
    return url

@app.route("/")
def index():
    return send_from_directory(app.static_folder, 'index2.html')

@app.route("/api/check", methods=["POST"])
def check_code():
    data = request.get_json()
    github_url = data.get("github_url")
    if not github_url:
        return jsonify({"error": "github_url 필드가 필요합니다."}), 400

    raw_url = convert_github_url_to_raw(github_url)

    try:
        resp = requests.get(raw_url)
        resp.raise_for_status()
        code = resp.text
    except Exception as e:
        return jsonify({"error": f"파일을 가져오는 중 에러 발생: {e}"}), 500

    prompt = (
        "다음 소스코드에서 보안 취약점을 분석해줘.\n"
        "각 취약점에 대해 해당 코드의 라인 번호, 코드 스니펫, 취약점 설명과 "
        "개선 방안을 마크다운 형식의 리스트로 출력해줘.\n\n"
        "소스코드:\n"
        "------------------------------\n"
        f"{code}\n"
        "------------------------------"
    )

    try:
        response = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            temperature=0.2,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        analysis = response.content[0].text
        print(analysis)
    except Exception as e:
        return jsonify({"error": f"Claude API 호출 중 에러 발생: {e}"}), 500

    return jsonify({
        "code": code,
        "analysis": analysis
    })

if __name__ == "__main__":
    app.run(debug=True)
