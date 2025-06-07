import json
import openai
import os
import re
import requests
import wikipedia
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, session

# 환경 변수 로드
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
WEATHER_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
STOCK_API_KEY = os.getenv("STOCK_API_KEY")
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = "your_secret_key"

# 최대 대화 저장 개수
MAX_HISTORY_LENGTH = 10 

# 안전한 Python 코드 실행
def execute_python_code(code):
    """GPT가 생성한 Python 코드를 실행하여 결과 반환"""
    try:
        exec_globals = {}
        exec(code, exec_globals)
        return exec_globals.get("result", "결과 없음")
    except Exception as e:
        return f"코드 실행 오류: {str(e)}"

# 날씨 API 호출
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
    print(f"날씨: {url}")
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            return f"{city}의 현재 날씨는 '{weather_desc}', 온도는 {temp}°C 입니다."
        return f"{city} 날씨 정보를 가져올 수 없습니다."
    except Exception as e:
        return f"날씨 API 오류: {str(e)}"

# 뉴스 API 호출
def get_news():
    print(f"뉴스 검색")
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

# 네이버 뉴스 검색 API 호출
def get_naver_news(query):
    print(f"네이버 검색: {query}")
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query,  # GPT에서 생성한 뉴스 검색 키워드
        "display": 3,  # 최대 3개 기사 반환
        "sort": "date"  # 최신순 정렬
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if "items" in data:
            top_news = [f"- {news['title']} ({news['originallink']})" for news in data["items"][:3]]
            return "\n".join(top_news)
        
        return f"'{query}' 뉴스를 가져올 수 없습니다."
    
    except Exception as e:
        return f"네이버 뉴스 API 오류: {str(e)}"
    
# 주식 가격 조회
def get_stock_price(symbol):
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

# 환율 조회
def get_exchange_rate():
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/USD"
    try:
        response = requests.get(url)
        data = response.json()
        return f"현재 USD-KRW 환율은 {data['conversion_rates']['KRW']}원입니다."
    except Exception as e:
        return f"환율 API 오류: {str(e)}"

# 위키백과 검색
def search_wikipedia(query):
    print(f"위키검색 키워드: {query}")
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

    # GPT에게 분류 및 검색 키워드 요청
    gpt_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": 
                """사용자의 질문을 분석하여 적절한 태스크 목록을 JSON 배열로 반환하세요.
                - "수학 연산": 계산을 실행해야 함.
                - "날씨 조회": 특정 지역의 날씨를 검색해야 함. (OpenWeatherMap에서 지원하는 영어 도시명으로 변환 필수)
                - "뉴스 검색": 최신 뉴스를 조회해야 함.
                - "네이버 뉴스 검색": 특정 주제나 인물, 기업 관련 뉴스를 검색해야 합니다. (네이버 검색 API에서 사용할 검색어 필수)
                - "주식 가격 조회": 특정 주식의 가격을 조회해야 함. (정확한 종목 티커(symbol) 반환 필수)
                - "환율 조회": 현재 환율 정보를 검색해야 함.
                - "위키백과 검색": 위키백과에서 특정 키워드를 검색해야 함. 가능하면 사용자 질문에서 물어본 언어로 키워드 도출.

                응답은 JSON 배열 형식으로 제공하세요.
                예시:
                [
                    {"task": "날씨 조회", "keyword": "Seoul"},
                    {"task": "위키백과 검색", "keyword": "나폴레옹"}
                ]
                """
            },
            {"role": "user", "content": user_input}
        ]
    )

    # GPT의 JSON 응답 처리
    try:
        tasks = json.loads(gpt_response.choices[0].message.content)
    except json.JSONDecodeError:
        return jsonify({"response": "질문을 이해하지 못했습니다. 다시 시도해주세요."})

    print(f"작업 목록: {tasks}")
    
    response_text = []

    # 여러 개의 태스크를 반복하여 실행
    for task_info in tasks:
        task = task_info.get("task", "")
        keyword = task_info.get("keyword", "")

        if task == "수학 연산":
            gpt_math_response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "사용자가 입력한 수식을 Python 코드로 변환하고 'result' 변수에 저장하세요."},
                          {"role": "user", "content": f"다음 수식을 Python 코드로 변환하세요: {keyword}"}]
            )
            generated_code = gpt_math_response.choices[0].message.content
            result = execute_python_code(generated_code)
            response_text.append(f"계산 결과: {result}")

        elif task == "날씨 조회":
            response_text.append(get_weather(keyword))

        elif task == "뉴스 검색":
            response_text.append(get_news())
            
        elif task == "네이버 뉴스 검색":
            response_text.append(get_naver_news(keyword))

        elif task == "주식 가격 조회":
            response_text.append(get_stock_price(keyword))

        elif task == "환율 조회":
            response_text.append(get_exchange_rate())

        elif task == "위키백과 검색":
            response_text.append(search_wikipedia(keyword))

        else:
            response_text.append(f"지원되지 않는 태스크입니다: {task}")

    # 2GPT에게 최종 정리 요청 (프롬프트 엔지니어링 적용)
    summary_prompt = f"""
사용자 질문: {user_input}

아래 정보를 참고하여 사용자가 이해하기 쉽게 자연스럽게 정리해 주세요.
검색 정보에 하이퍼링크가 있다면 해당 부분을 [] 괄호에 출처를 담에서 참고링크를 제공해 주세요.
답변은 최대한 간단한 HTML 태그 형태로 표현해 주세요.

검색 정보:

{"".join(f"- {item}\n" for item in response_text)}
"""
    # {"\n".join(response_text)}
    
    print(f"최종 요약 데이터: {summary_prompt}")
    
    gpt_summary = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 정보를 명확하고 자연스럽게 요약하는 AI입니다."},
            {"role": "user", "content": summary_prompt}
        ]
    )

    final_response = gpt_summary.choices[0].message.content

    print("-" * 50)
    print(f"최종 사용자 전달 응답:\n{final_response}")

    session["messages"].append({"role": "user", "content": user_input})
    session["messages"].append({"role": "assistant", "content": final_response})

    if len(session["messages"]) > MAX_HISTORY_LENGTH + 1:
        session["messages"] = [session["messages"][0]] + session["messages"][-MAX_HISTORY_LENGTH:]

    session.modified = True

    return jsonify({"response": final_response})

@app.route("/clear", methods=["POST"])
def clear():
    """대화 내용 초기화"""
    session.pop("messages", None)
    return jsonify({"message": "대화 기록이 초기화되었습니다."})

if __name__ == "__main__":
    app.run(debug=True)
