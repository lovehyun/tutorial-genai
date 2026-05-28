"""
[Task] AI 뉴스 분석기 — 한 기사를 여러 관점으로 동시에 분석

같은 입력(뉴스)에 대해 요약/감정분석/카테고리 분류를 병렬로 수행합니다.
'여행 플래너' 와 패턴은 같지만, 입력 하나를 다각도로 분석한다는 점이 다릅니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

summary_chain = (
    ChatPromptTemplate.from_template("다음 뉴스를 2~3문장으로 요약해줘.\n\n{news}")
    | llm | StrOutputParser()
)

sentiment_chain = (
    ChatPromptTemplate.from_template(
        "다음 뉴스의 전반적 감정을 한 단어로 답해 (긍정 / 부정 / 중립).\n\n{news}"
    )
    | llm | StrOutputParser()
)

category_chain = (
    ChatPromptTemplate.from_template(
        "다음 뉴스의 카테고리를 한 단어로 답해 (정치/경제/IT/스포츠/사회 등).\n\n{news}"
    )
    | llm | StrOutputParser()
)

news_chain = RunnableParallel({
    "summary":   summary_chain,
    "sentiment": sentiment_chain,
    "category":  category_chain,
})

news = (
    "OpenAI는 오늘 새로운 추론 모델을 공개했다. "
    "이번 모델은 수학·과학 문제에서 기존 대비 30% 향상된 성능을 보였으며, "
    "API 가격도 함께 인하되어 개발자 커뮤니티의 환영을 받고 있다."
)

result = news_chain.invoke({"news": news})

print("📰 [원문]")
print(news)
print("\n📋 [요약]      ", result["summary"])
print("💭 [감정]      ", result["sentiment"])
print("🗂️  [카테고리]  ", result["category"])
