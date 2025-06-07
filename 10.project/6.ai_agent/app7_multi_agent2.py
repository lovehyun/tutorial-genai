import os
import re
import requests
import wikipedia
from flask import Flask, request, jsonify, send_from_directory, session
from dotenv import load_dotenv
from openai import OpenAI

# 환경 변수 로드
load_dotenv()
openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
WEATHER_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")  # 날씨 API 키
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
STOCK_API_KEY = os.getenv("STOCK_API_KEY")
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = "your_secret_key"  # Flask 세션을 위한 키

# 최대 대화 저장 개수
MAX_HISTORY_LENGTH = 10  

# 안전한 Python 코드 실행 함수
def execute_python_code(code):
    """GPT가 생성한 Python 코드를 실행하여 결과 반환"""
    try:
        exec_globals = {}  
        exec(code, exec_globals)
        return exec_globals.get("result", "결과 없음")  
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
    "제주도": "Jeju",
    "청주": "Cheongju",
    "전주": "Jeonju",
    "포항": "Pohang",
    "창원": "Changwon"
}

# (1) 날씨 API 호출
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
            return f"{city} 날씨 정보를 가져올 수 없습니다."
    except Exception as e:
        return f"날씨 API 오류: {str(e)}"

# (2) 뉴스 검색 API 호출
def get_news():
    """뉴스 API를 사용하여 최신 뉴스 가져오기"""
    url = f"https://newsapi.org/v2/top-headlines?country=kr&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if "articles" in data:
            top_news = [f"{news['title']} - {news['url']}" for news in data["articles"][:3]]
            return "\n".join(top_news)
        return "뉴스를 가져올 수 없습니다."
    except Exception as e:
        return f"뉴스 API 오류: {str(e)}"

# (3) 주식 가격 조회 API 호출
def get_stock_price(symbol):
    """주식 가격 조회"""
    url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={STOCK_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if data and isinstance(data, list):
            price = data[0]["price"]
            return f"{symbol} 현재 주가는 {price}원입니다."
        return f"{symbol} 주식 정보를 가져올 수 없습니다."
    except Exception as e:
        return f"주식 API 오류: {str(e)}"

# (4) 환율 조회 API 호출
def get_exchange_rate():
    """환율 조회"""
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/USD"
    try:
        response = requests.get(url)
        data = response.json()
        return f"현재 USD-KRW 환율은 {data['conversion_rates']['KRW']}원입니다."
    except Exception as e:
        return f"환율 API 오류: {str(e)}"

# (5) 위키백과 검색
def search_wikipedia(query):
    """위키백과 검색"""
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.PageError:
        return f"해당 주제({query})에 대한 위키백과 정보가 없습니다."
    except Exception as e:
        return f"위키백과 검색 오류: {str(e)}"

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
        session.modified = True
        
        return jsonify({"response": bot_reply})

    # 2️. **날씨 질문 감지** (예: "서울 날씨 어때?", "부산 날씨 알려줘")
    if "날씨" in user_input:
        city = re.search(r"([가-힣]+)\s?날씨", user_input)
        city_name = city.group(1) if city else "서울"
        weather_info = get_weather(city_name)
        session["messages"].append({"role": "assistant", "content": weather_info})
        session.modified = True
        return jsonify({"response": weather_info})

    # 3. 뉴스 검색
    if "뉴스" in user_input:
        news_info = get_news()
        session["messages"].append({"role": "assistant", "content": news_info})
        session.modified = True
        return jsonify({"response": news_info})

    # 4. 주식 가격 조회
    if "주가" in user_input:
        stock_symbol = "005930.KQ"  # 삼성전자 예시
        stock_info = get_stock_price(stock_symbol)
        session["messages"].append({"role": "assistant", "content": stock_info})
        session.modified = True
        return jsonify({"response": stock_info})

    # 5. 환율 조회
    if "환율" in user_input:
        exchange_info = get_exchange_rate()
        session["messages"].append({"role": "assistant", "content": exchange_info})
        session.modified = True
        return jsonify({"response": exchange_info})

    # 6. 위키백과 검색
    if "위키백과" in user_input or "설명해줘" in user_input:
        query = user_input.replace("위키백과", "").replace("설명해줘", "").strip()
        wiki_info = search_wikipedia(query)
        session["messages"].append({"role": "assistant", "content": wiki_info})
        session.modified = True
        return jsonify({"response": wiki_info})

    # 7. 일반 대화 처리
    session["messages"].append({"role": "user", "content": user_input})
    
    # 시스템 메시지 업데이트 (대화 개수 추가 - 히스토리에 매번 10개만 남김으로...)
    session["messages"][0] = {
        "role": "system",
        "content": f"You are a helpful assistant. 현재까지 총 {session["conversation_count"]}개의 대화가 오갔습니다."
    }
    print(session["messages"])
    print('-' * 50)
    
    response = openai.chat.completions.create(model="gpt-4o", messages=session["messages"])
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
