# app.py
# 주제(topic)를 받아 어떤 뉴스든 카드뉴스 이미지로 만드는 범용 앱.
#   python app.py "주제 문장"      (인자 없으면 기본 예시 주제로 실행)
import sys, re, base64, requests
from bs4 import BeautifulSoup

from dotenv import load_dotenv

from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
client = OpenAI()


# 1단계: 뉴스 가져오는 도구
def fetch_news(query: str) -> str:
    """뉴스 검색 결과를 가져온다."""
    url = "https://news.google.com/rss/search"
    params = {
        "q": query,
        "hl": "ko", # 인터페이스 언어
        "gl": "KR", # 국가 (geolocation)
        "ceid": "KR:ko" # 뉴스 에디션
    }

    xml = requests.get(url, params=params, timeout=10).text
    soup = BeautifulSoup(xml, "xml")

    items = []
    for item in soup.find_all("item")[:8]:
        items.append({
            "title": item.title.text,
            "link": item.link.text,
            "date": item.pubDate.text
        })

    return str(items)


# 뉴스 수집 Agent
news_agent = create_agent(
    model=llm,
    tools=[fetch_news],
    system_prompt="""
너는 뉴스 조사 에이전트다.
사용자가 준 주제와 관련된 최신 뉴스 목록을 수집하고,
핵심 사실을 주제 중심으로 간결히 정리한다.
"""
)


# 2단계: 뉴스 요약 → 이미지 프롬프트 생성
def make_image_prompt(news_summary: str) -> str:
    prompt = f"""
다음 뉴스 요약을 바탕으로 '카드뉴스/웹툰' 스타일 이미지 생성 프롬프트를 영어로 작성해라.

규칙(주제에 상관없이 항상 적용):
- 요약 '내용'에서 핵심 장면을 직접 추출해 시각화한다(특정 형식·일정표 등을 가정하지 말 것).
- 한 장, 패널 3~5개, 과밀 금지.
- 특정 실존 인물·실제 상표/로고는 묘사하지 말 것(일반화된 캐릭터/심볼로 표현).
- 이미지 내 글자는 최소화(모델이 한글을 잘 못 그림 — 텍스트 칸은 비워두는 느낌).
- 밝고 깔끔한 인포그래픽 톤.

뉴스 요약:
{news_summary}
"""

    result = llm.invoke(prompt)
    return result.content


def slugify(text: str) -> str:
    """주제를 파일명으로 쓸 수 있게 정리(한글 유지, 금지문자 제거)."""
    text = re.sub(r'[\\/:*?"<>|]+', "", text)
    text = re.sub(r"\s+", "_", text.strip())
    return text[:40] or "cardnews"


# 3단계: 이미지 생성
def generate_image(image_prompt: str, output_path: str = "cardnews.png"):
    result = client.images.generate(
        model="gpt-image-1.5",
        prompt=image_prompt,
        size="1024x1536",
        quality="medium"
    )

    image_base64 = result.data[0].b64_json

    with open(output_path, "wb") as f:
        f.write(base64.b64decode(image_base64))

    return output_path


def main():
    # 기본 예시 주제(최근 이슈) — 그대로 실행하면 이게 돈다.
    # 다른 주제로 쓰려면 인자로:  python app.py "주제 문장"
    topic = " ".join(sys.argv[1:]).strip() or "젠슨 황 4박 5일 한국 방문 일정"
    story = f"{topic} 관련 최신 뉴스들을 조사해줘"

    # 1. 뉴스 수집
    news_result = news_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": story
            }
        ]
    })

    news_summary = news_result["messages"][-1].content

    print("\n[뉴스 요약]")
    print(news_summary)

    # 2. 이미지 프롬프트 생성
    image_prompt = make_image_prompt(news_summary)

    print("\n[이미지 프롬프트]")
    print(image_prompt)

    # 3. 이미지 생성
    output_file = generate_image(image_prompt, f"cardnews_{slugify(topic)}.png")

    print(f"\n이미지 생성 완료: {output_file}")


if __name__ == "__main__":
    main()
