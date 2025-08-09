from dotenv import load_dotenv
import os, json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser, StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# ============================================================
# [0] 환경 준비
# ============================================================
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")

# 공용 LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.6)
to_str = StrOutputParser()

# ============================================================
# [1] CSV 강제: 회사명 후보 N개 생성 → 리스트로 파싱
#    - CommaSeparatedListOutputParser 사용
# ============================================================
names_parser = CommaSeparatedListOutputParser()
names_format = names_parser.get_format_instructions()

names_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 전문 작명 컨설턴트입니다. 한국어로 회사명을 제안하세요."),
    ("human",
     "다음 제품/서비스를 만드는 회사명을 {count}개 제안해줘. "
     "각 후보는 간결하고 발음이 쉬워야 합니다. 제품: {product}\n"
     "반드시 아래 형식만 출력하세요.\n{format_instructions}")
]).partial(format_instructions=names_format)

names_chain = names_prompt | llm | names_parser

# ============================================================
# [2] JSON 강제: 선정된 회사에 대한 구조화 정보 생성
#    - JsonOutputParser 사용 (필드: company_name, catch_phrase, mission, offerings(list), usp)
# ============================================================
json_parser = JsonOutputParser(pydantic_object=None)  # 스키마를 문구로 강제
json_format = (
    "JSON 객체만 출력하세요. 스키마 예시:\n"
    "{\n"
    '  "company_name": "문자열",\n'
    '  "catch_phrase": "문자열",\n'
    '  "mission": "문자열",\n'
    '  "offerings": ["문자열", "문자열", ...],\n'
    '  "usp": "문자열"\n'
    "}"
)

profile_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 브랜드 전략 컨설턴트입니다. 정확한 JSON만 출력하세요(설명 금지)."),
    ("human",
     "회사명: {company_name}\n"
     "아래 스키마를 따르는 JSON으로 소개 정보를 작성하세요.\n"
     "{format_instructions}")
]).partial(format_instructions=json_format)

profile_chain = profile_prompt | llm | json_parser

# ============================================================
# [3] Passthrough로 파이프 구성
#   - A) CSV 후보 생성 → 리스트
#   - B) 첫 후보 선택 (데모용) 또는 다른 선택 로직 삽입 가능
#   - C) JSON 스키마 강제 프로필 생성 → dict
# ============================================================
def pick_first(candidates: list[str]) -> str:
    return candidates[0] if candidates else "임시회사"

pipeline = (
    {"product": lambda x: x.get("product", ""), "count": lambda x: x.get("count", 5)}
    | RunnablePassthrough.assign(
        candidates=lambda x: names_chain.invoke({"product": x["product"], "count": x["count"]})
    )
    | RunnablePassthrough.assign(
        company_name=lambda x: pick_first(x["candidates"])
    )
    | RunnablePassthrough.assign(
        company_profile=lambda x: profile_chain.invoke({"company_name": x["company_name"]})
    )
)

# ============================================================
# [4] 안전 장치: JSON 파싱 실패 시 폴백(문자열 → dict 시도)
#   - 모델이 드물게 설명을 붙이면 JsonOutputParser가 실패할 수 있음 → 간단 폴백
# ============================================================
def safe_profile(d: dict):
    data = d.copy()
    try:
        # 이미 dict면 통과
        _ = data["company_profile"]
        if isinstance(_, str):
            data["company_profile"] = json.loads(_)
    except Exception:
        # 최소 구조 폴백
        data["company_profile"] = {
            "company_name": data.get("company_name", ""),
            "catch_phrase": "",
            "mission": "",
            "offerings": [],
            "usp": ""
        }
    return data

pipeline = pipeline | RunnableLambda(safe_profile)

# ============================================================
# [5] 실행
# ============================================================
if __name__ == "__main__":
    inputs = {"product": "웹게임", "count": 5}
    out = pipeline.invoke(inputs)

    print("\n[회사명 후보 (CSV 강제 -> 리스트)]")
    for i, name in enumerate(out["candidates"], start=1):
        print(f" - {i}. {name}")

    print("\n[선정된 회사명]")
    print(" →", out["company_name"])

    print("\n[구조화 프로필 (JSON 강제 -> dict)]")
    prof = out["company_profile"]
    print(json.dumps(prof, ensure_ascii=False, indent=2))

# ============================================================
# [6] 팁
# - CSV/JSON 강제 시 반드시 get_format_instructions() 또는 스키마 예시문을 프롬프트에 포함하세요.
# - 실패 대비: JsonOutputParser 실패에 대비해 문자열이면 json.loads 시도, 그래도 실패 시 폴백 스키마.
# - 선택 로직: 후보 중 도메인 가용성/길이/발음 기준 등 점수화 체인으로 대체 가능.
# ============================================================
