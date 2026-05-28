"""
RunnableParallel — 같은 입력을 여러 체인에 동시 실행하는 Runnable.
이 예제: 상품 설명 1개 → 광고 문구 / SEO 메타 설명 / SNS 해시태그를 한 번에 동시 생성.

콘텐츠 마케팅 자동화의 전형.
입력 1개로 여러 채널(광고/검색/SNS) 콘텐츠를 즉시 만들어내는 패턴.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

ad_chain = (
    ChatPromptTemplate.from_template("다음 상품의 매력적인 광고 문구를 1줄로 만들어줘.\n상품: {product}")
    | llm | StrOutputParser()
)

seo_chain = (
    ChatPromptTemplate.from_template("다음 상품의 SEO 메타 설명을 120자 이내로 작성해줘.\n상품: {product}")
    | llm | StrOutputParser()
)

hashtag_chain = (
    ChatPromptTemplate.from_template("다음 상품에 어울리는 인스타그램 해시태그 5개를 만들어줘 (#포함, 공백 구분).\n상품: {product}")
    | llm | StrOutputParser()
)

marketing_chain = RunnableParallel({
    "ad":       ad_chain,
    "seo":      seo_chain,
    "hashtags": hashtag_chain,
})

product = "수면을 도와주는 라벤더 향 아로마 디퓨저 (USB 충전식, 7가지 LED 색상)"
result = marketing_chain.invoke({"product": product})

print(f"📦 [상품] {product}\n")
print(f"📢 [광고 문구]\n  {result['ad']}\n")
print(f"🔍 [SEO 설명]\n  {result['seo']}\n")
print(f"🏷️ [해시태그]\n  {result['hashtags']}")
