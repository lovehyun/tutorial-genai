"""
PydanticOutputParser — Pydantic 모델로 구조화된 출력 파싱

LLM 응답을 Pydantic 모델에 맞춰 자동으로 파싱합니다.
format_instructions를 프롬프트에 주입하여 LLM이 올바른 JSON 형식으로 응답하도록 유도합니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ===== 1. Pydantic 모델 정의 =====
class MovieReview(BaseModel):
    """영화 리뷰 분석 결과"""
    title: str = Field(description="영화 제목")
    sentiment: str = Field(description="감성 분류: 긍정, 부정, 중립")
    score: int = Field(description="1~10 점수")
    summary: str = Field(description="리뷰 요약 (1~2문장)")
    keywords: list[str] = Field(description="핵심 키워드 3개")


# ===== 2. 파서 생성 및 format_instructions 확인 =====
parser = PydanticOutputParser(pydantic_object=MovieReview)
print("Format Instructions:")
print(parser.get_format_instructions())
print()

# ===== 3. 프롬프트에 format_instructions 주입 =====
prompt = ChatPromptTemplate.from_template(
    """다음 영화 리뷰를 분석해주세요.

리뷰: {review}

{format_instructions}
"""
)

# ===== 4. 체인 구성 =====
chain = prompt | llm | parser

# ===== 5. 실행 =====
reviews = [
    "인터스텔라는 정말 감동적인 영화였습니다. 우주의 광활함과 아버지의 사랑이 절묘하게 어우러져 있어요. 한스 짐머의 음악도 완벽했습니다!",
    "이 영화는 스토리가 너무 뻔하고 연기도 어색했어요. 2시간이 아깝네요. 특수효과만 볼만했습니다.",
    "전체적으로 무난한 영화예요. 시간 때우기에는 괜찮지만 특별히 기억에 남는 건 없었어요.",
]

for review in reviews:
    result = chain.invoke({
        "review": review,
        "format_instructions": parser.get_format_instructions()
    })
    print(f"제목: {result.title}")
    print(f"감성: {result.sentiment} (점수: {result.score}/10)")
    print(f"요약: {result.summary}")
    print(f"키워드: {result.keywords}")
    print()
