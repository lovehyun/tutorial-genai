# app.py
# ------------------------------------------------------------
# 보안 로그 모니터링 API
# - 개발: 샘플 파일 사용
# - 운영: /var/log/auth.log 사용
# - 변경 감지(해시) 후에만 LLM 요약 호출
# ------------------------------------------------------------
import os
import logging
import hashlib
from collections import deque
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory

# LangChain (OpenAI LLM)
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

# 환경 변수 로드 및 로깅 설정
load_dotenv()
logging.basicConfig(level=logging.INFO)

USE_LOG_SAMPLE = os.getenv("USE_LOG_SAMPLE", "true").lower() == "true"
LOG_SAMPLE_PATH = os.getenv("LOG_SAMPLE_PATH", "./sample_auth.log")
AUTH_LOG_PATH = "/var/log/auth.log"

def get_log_path() -> str:
    """환경 변수에 따라 로그 경로를 반환"""
    return LOG_SAMPLE_PATH if USE_LOG_SAMPLE else AUTH_LOG_PATH

# Flask 앱
app = Flask(__name__, static_folder="public", static_url_path="")

# LLM 초기화 (보안 로그 요약)
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    api_key=os.getenv("OPENAI_API_KEY")
)

# 유틸: tail 기능
def tail_file(path: str, n: int = 10) -> list[str]:
    """파일에서 마지막 N줄 읽기"""
    d = deque(maxlen=n)
    with open(path, "r", errors="ignore") as f:
        for line in f:
            d.append(line.rstrip("\n"))
    return list(d)

def hash_lines(lines: list[str]) -> str:
    """라인 배열의 내용 해시(sha256) 생성"""
    h = hashlib.sha256()
    # 줄 간 구분을 고정하기 위해 '\n'로 합칩니다.
    h.update("\n".join(lines).encode("utf-8", errors="ignore"))
    return h.hexdigest()

# 보안 로그 요약 프롬프트
authlog_prompt = PromptTemplate.from_template(
    """당신은 리눅스 보안 분석가입니다. 아래 Ubuntu /var/log/auth.log 최근 로그 N줄을 읽고,
핵심 보안 관점에서 간결하게 해설하세요.

요구사항:
- 시간 범위(최초~최종 시각)
- SSH 로그인: 성공/실패 횟수, 관련 계정, 출발 IP/호스트, 포트
- sudo 사용/인증 실패, PAM 세션 open/close 등 주요 이벤트 요약
- 의심 징후(다수 실패, 동일 IP 반복, 존재하지 않는 사용자 시도 등) 강조
- 마지막에 "평가: 정상 / 주의 / 심각" 중 하나로 총평

[최근 로그 N줄]
{auth_lines}
"""
)

authlog_prompt2 = PromptTemplate.from_template(
    """당신은 리눅스 보안 분석가입니다. 아래 Ubuntu /var/log/auth.log 최근 로그 N줄을 읽고,
핵심 보안 관점에서 HTML 형식 보고서를 작성하세요.

요구사항:
- <h2>, <h3>, <ul><li> 등을 사용해 구조화
- 주요 수치는 <strong>태그</strong>로 강조
- 전체를 <section> 태그로 감싸기
- 추가 텍스트나 코드 블록 없이 HTML만 반환

[최근 로그 N줄]
{auth_lines}
"""
)

def summarize_authlog(lines: list[str]) -> str:
    """최근 로그를 요약"""
    text = "\n".join(lines) if lines else "(로그 없음)"
    # runnable = authlog_prompt | llm | RunnableLambda(lambda m: m.content)
    runnable = authlog_prompt2 | llm | RunnableLambda(lambda m: m.content)
    return runnable.invoke({"auth_lines": text})

# 요약 캐시 (내용 해시 기반)
# - 마지막으로 요약한 라인 내용의 해시와 결과를 보관
# - 동일 내용이면 LLM 호출 생략
last_summary_hash: str | None = None
last_summary_text: str = ""
last_summary_count: int = 0

# 전역 캐시
last_summary_hash = None
last_summary_text = ""
last_summary_count = 0

# API: /api/authlog
@app.route("/api/authlog/raw", methods=["GET"])
def api_authlog_raw():
    """RAW 로그만 반환"""
    try:
        n = int(request.args.get("n", 10))
    except ValueError:
        n = 10

    log_path = get_log_path()
    try:
        raw_lines = tail_file(log_path, n=n)
    except Exception as e:
        app.logger.error(f"[authlog] RAW read error: {e}")
        return jsonify({"error": "로그 읽기 실패"}), 500

    return jsonify({
        "raw": raw_lines,
        "count": len(raw_lines),
        "usingSample": USE_LOG_SAMPLE,
        "path": log_path,
        "updatedAt": datetime.now().isoformat(timespec="seconds"),
    })

@app.route("/api/authlog/summary", methods=["GET"])
def api_authlog_summary():
    """최근 N줄 기반 보안 로그 요약 반환 (변경 시만 생성)"""
    global last_summary_hash, last_summary_text, last_summary_count
    try:
        n = int(request.args.get("n", 10))
    except ValueError:
        n = 10

    log_path = get_log_path()
    try:
        raw_lines = tail_file(log_path, n=n)
    except Exception as e:
        app.logger.error(f"[authlog] Read error: {e}")
        return jsonify({"error": "로그 읽기 실패"}), 500

    current_hash = hash_lines(raw_lines)
    is_fresh = False

    if current_hash != last_summary_hash:
        try:
            summary = summarize_authlog(raw_lines)
            last_summary_hash = current_hash
            last_summary_text = summary
            last_summary_count = len(raw_lines)
            is_fresh = True
        except Exception as e:
            app.logger.error(f"[authlog] Summary error: {e}")
            summary = last_summary_text or "AI 요약 실패"
    else:
        summary = last_summary_text

    return jsonify({
        "summary": summary,
        "summaryFresh": is_fresh,
        "count": len(raw_lines),
        "updatedAt": datetime.now().isoformat(timespec="seconds"),
        "usingSample": USE_LOG_SAMPLE,
        "path": log_path
    })

# 정적 페이지
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# 실행
if __name__ == "__main__":
    app.run(port=5000, debug=True)
