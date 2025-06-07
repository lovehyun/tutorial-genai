import os
import re
import requests
from flask import Flask, request, jsonify, send_from_directory, session
from dotenv import load_dotenv
from openai import OpenAI

# 환경 변수 로드
load_dotenv()
openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
WEATHER_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")  # 날씨 API 키

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = "your_secret_key"  # Flask 세션을 위한 키

# 최대 대화 저장 개수
MAX_HISTORY_LENGTH = 10  

# 안전한 Python 코드 실행 함수
def execute_python_code(code):
    """GPT가 생성한 Python 코드를 실행하여 결과 반환"""
    try:
        exec_globals = {}  # 실행을 위한 별도 네임스페이스
        exec(code, exec_globals)
        return exec_globals.get("result", "결과 없음")  # 결과 반환
    except Exception as e:
        return f"코드 실행 오류: {str(e)}"

# 한글 도시명 → 영어 변환 테이블
CITY_MAPPING = {
    "서울": "Seoul",
    "부산": "Busan",
    "인천": "Incheon",
    "대구": "Daegu",
    "대전": "Daejeon",
    "광주": "Gwangju",
    "울산": "Ulsan",
    "수원": "Suwon",
    "제주": "Jeju",
    "청주": "Cheongju",
    "전주": "Jeonju",
    "포항": "Pohang",
    "창원": "Changwon"
}

# 날씨 API 호출 함수
def get_weather(city):
    """OpenWeatherMap API를 사용하여 날씨 정보를 가져옴"""
    city_english = CITY_MAPPING.get(city, city)  # 매핑된 도시가 없으면 원래 값 사용
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_english}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
    # print(url)
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            return f"{city}의 현재 날씨는 '{weather_desc}', 온도는 {temp}°C 입니다."
        else:
            return "날씨 정보를 가져올 수 없습니다."
    except Exception as e:
        return f"날씨 API 오류: {str(e)}"

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question")

    if not user_input:
        return jsonify({"error": "질문을 입력하세요."}), 400

    # 세션에서 대화 기록 가져오기 (없으면 초기화)
    if "messages" not in session:
        session["messages"] = [{"role": "system", "content": "You are a helpful assistant."}]
        session["conversation_count"] = 0

    # 대화 길이 제한 (최근 MAX_HISTORY_LENGTH개 유지)
    if len(session["messages"]) > MAX_HISTORY_LENGTH + 1:  # system 메시지 제외
        session["messages"] = [session["messages"][0]] + session["messages"][-MAX_HISTORY_LENGTH:]

    # 현재 대화 개수 계산 (시스템 메시지 제외)
    session["conversation_count"] = session.get("conversation_count", 0) + 1

    # 1️. **수학 연산 감지** (예: "5 + 3", "100 * (2 + 3)")
    if re.match(r"^[0-9+\-*/().\s]+$", user_input.strip()):
        # GPT에게 Python 코드 생성 요청
        gpt_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "사용자가 입력한 수식을 Python 코드로 변환하고 'result' 변수에 저장하세요."},
                {"role": "user", "content": f"다음 수식을 Python 코드로 변환하세요: {user_input}"}
            ]
        )
        generated_code = gpt_response.choices[0].message.content

        # GPT가 생성한 Python 코드 실행
        result = execute_python_code(generated_code)

        # 응답 반환
        bot_reply = f"코드 실행 결과: {result}"
        session["messages"].append({"role": "assistant", "content": bot_reply})
        return jsonify({"response": bot_reply})

    # 2️. **날씨 질문 감지** (예: "서울 날씨 어때?", "부산 날씨 알려줘")
    if any(kw in user_input for kw in ["날씨", "기온", "온도"]):
        city_match = re.search(r"([가-힣]+)\s?날씨", user_input)
        city = city_match.group(1) if city_match else "서울"  # 기본값: 서울(Seoul)
        weather_info = get_weather(city)
        print(weather_info)

        bot_reply = f"{weather_info}"
        session["messages"].append({"role": "assistant", "content": bot_reply})
        session.modified = True
        
        return jsonify({"response": bot_reply})

    # 3️. **일반적인 질문은 기존 방식 유지**
    session["messages"].append({"role": "user", "content": user_input})
    session.modified = True

    # 시스템 메시지 업데이트 (대화 개수 추가 - 히스토리에 매번 10개만 남김으로...)
    session["messages"][0] = {
        "role": "system",
        "content": f"You are a helpful assistant. 현재까지 총 {session["conversation_count"]}개의 대화가 오갔습니다."
    }
    
    print(session["messages"])
    print('-' * 50)
    
    # GPT API 호출
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=session["messages"]
    )

    # GPT 응답 저장
    bot_reply = response.choices[0].message.content
    session["messages"].append({"role": "assistant", "content": bot_reply})
    session.modified = True

    return jsonify({"response": bot_reply})

@app.route("/clear", methods=["POST"])
def clear():
    """대화 내용 초기화"""
    session.pop("messages", None)
    return jsonify({"message": "대화 기록이 초기화되었습니다."})

if __name__ == "__main__":
    app.run(debug=True)
