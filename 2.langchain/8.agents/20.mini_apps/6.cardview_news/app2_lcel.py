# app2_lcel.py
# app.py 를 LCEL(LangChain Expression Language) 구조로 재작성한 버전.
#
# 핵심 아이디어
#   - 각 단계를 Runnable 로 만들고  |  파이프로 연결한다.
#   - LLM 이 아닌 단계(뉴스수집/이미지생성)는 RunnableLambda 로 감싼다.
#   - LLM 단계는  prompt | llm | parser  로 구성한다.
#   - RunnablePassthrough.assign 으로 중간 결과(news, summary, image_prompt)를
#     dict 에 누적하며 흐르게 해서 한 줄 파이프라인으로 만든다.
#
# ★ 범용(topic-driven): 특정 주제(젠슨 황/4박5일 등)를 "프롬프트"에 박지 않는다.
#   기본 예시 주제는 main() 에 두고(그대로 실행하면 동작), 프롬프트 규칙은 주제 비종속.
#     python app2_lcel.py "주제 문장"      (인자 없으면 기본 예시 주제로 실행)
#
# 원본(app.py) 대비 바뀐 점
#   1) create_agent(에이전트) 제거 → RunnableLambda 로 직접 호출.
#      뉴스 검색은 "어떤 도구를 쓸지" LLM 판단이 필요 없는 결정적 호출이라
#      에이전트보다 LCEL 체인이 더 단순/예측가능하다.
#   2) fetch_news 가 str(list) 대신 JSON 문자열을 반환(LLM 입력으로 더 깔끔).
#   3) 프롬프트를 주제 비종속(범용)으로 작성: 실존 인물/상표/형식 가정 제거.

import sys
import re
import base64
import json
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
oai = OpenAI()


# --- 비-LLM 단계 (순수 함수) -------------------------------------------------
def fetch_news(query: str) -> str:
    """구글 뉴스 RSS 검색 결과를 JSON 문자열로 반환한다."""
    url = "https://news.google.com/rss/search"
    params = {"q": query, "hl": "ko", "gl": "KR", "ceid": "KR:ko"}
    xml = requests.get(url, params=params, timeout=10).text
    soup = BeautifulSoup(xml, "xml")   # lxml 필요: pip install lxml
    items = [
        {"title": it.title.text, "link": it.link.text, "date": it.pubDate.text}
        for it in soup.find_all("item")[:8]
    ]
    return json.dumps(items, ensure_ascii=False)


def slugify(text: str) -> str:
    """주제를 파일명으로 쓸 수 있게 정리(한글 유지, 금지문자 제거)."""
    text = re.sub(r'[\\/:*?"<>|]+', "", text)
    text = re.sub(r"\s+", "_", text.strip())
    return text[:40] or "cardnews"


def generate_image(image_prompt: str, output_path: str) -> str:
    """이미지 생성 후 파일로 저장하고 경로를 반환한다."""
    result = oai.images.generate(
        model="gpt-image-1",            # 품질이 더 필요하면 "gpt-image-1.5"
        prompt=image_prompt,
        size="1024x1536",
        quality="medium",
    )
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(result.data[0].b64_json))
    return output_path


# RunnableLambda 로 감싸 파이프라인에 끼울 수 있게 한다 (입력은 누적 dict)
fetch_news_step = RunnableLambda(lambda x: fetch_news(x["topic"]))
generate_image_step = RunnableLambda(
    lambda x: generate_image(x["image_prompt"], f"cardnews_{slugify(x['topic'])}.png")
)


# --- LLM 단계 (prompt | llm | parser) ---------------------------------------
summarize_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "너는 뉴스 조사 에이전트다. 주어진 뉴스 목록에서 핵심 사실을 주제 중심으로 간결히 정리한다."),
        ("human", "다음 뉴스 목록(JSON)을 한국어로 요약해줘:\n\n{news}"),
    ])
    | llm
    | StrOutputParser()
)

image_prompt_chain = (
    ChatPromptTemplate.from_messages([
        ("human",
         "다음 뉴스 요약을 바탕으로 '카드뉴스/웹툰' 스타일 이미지 생성 프롬프트를 영어로 작성해라.\n"
         "규칙(주제에 상관없이 항상 적용):\n"
         "- 요약 '내용'에서 핵심 장면을 직접 추출해 시각화한다(특정 형식·일정표 등을 가정하지 말 것).\n"
         "- 한 장, 패널 3~5개, 과밀 금지.\n"
         "- 특정 실존 인물·실제 상표/로고는 묘사하지 말 것(일반화된 캐릭터/심볼로 표현).\n"
         "- 이미지 내 글자는 최소화(모델이 한글을 잘 못 그림 — 텍스트 칸은 비워두는 느낌).\n"
         "- 밝고 깔끔한 인포그래픽 톤.\n\n"
         "뉴스 요약:\n{summary}"),
    ])
    | llm
    | StrOutputParser()
)


# --- 전체 파이프라인: 중간 결과를 누적(assign)하며 한 번에 흐른다 ----------------
pipeline = (
    RunnablePassthrough.assign(news=fetch_news_step)            # {topic} -> +news
    | RunnablePassthrough.assign(summary=summarize_chain)       # +summary
    | RunnablePassthrough.assign(image_prompt=image_prompt_chain)  # +image_prompt
    | RunnablePassthrough.assign(image_path=generate_image_step)   # +image_path
)


def main():
    # 기본 예시 주제(최근 이슈) — 그대로 실행하면 이게 돈다.
    # 다른 주제로 쓰려면 인자로:  python app2_lcel.py "주제 문장"
    topic = " ".join(sys.argv[1:]).strip() or "젠슨 황 4박 5일 한국 방문 일정"

    result = pipeline.invoke({"topic": topic})

    print("\n[뉴스 요약]")
    print(result["summary"])
    print("\n[이미지 프롬프트]")
    print(result["image_prompt"])
    print(f"\n이미지 생성 완료: {result['image_path']}")


if __name__ == "__main__":
    main()
