from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser, StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel

# ============================================================
# [0] 환경 준비
# ============================================================
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")

# ============================================================
# [1] 공용 LLM 설정 (최신/경량)
# ============================================================
# - gpt-4o-mini: 빠르고 합리적인 품질
# - temperature는 살짝 높여 네이밍 다양성 확보
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
to_str = StrOutputParser()

# ============================================================
# [2] 회사명 후보 다발 생성 체인
#    - 입력: product, count
#    - 출력: 후보 이름 리스트(List[str])  ex) ["플레이버스", "웹아케이드", ...]
#    - 포맷: CSV 파서를 쓰므로 모델에 포맷 지시를 명확히 전달
# ============================================================
name_list_parser = CommaSeparatedListOutputParser()
format_hint = name_list_parser.get_format_instructions()

name_list_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 전문 작명 컨설턴트입니다. 한국어로 창의적인 회사명을 제안하세요."),
    ("human",
     "다음 제품/서비스를 만드는 회사명을 {count}개 제안해줘. "
     "각 후보는 간결하고 발음이 쉬워야 합니다. 제품: {product}\n"
     "반드시 아래 형식으로만 출력하세요.\n{format_hint}")
]).partial(format_hint=format_hint)

# 프롬프트 → LLM → CSV 파서(List[str])
name_list_chain = name_list_prompt | llm | name_list_parser

# ============================================================
# [3] 후보 중 '최적' 회사명 선택 체인
#    - 입력: product, candidates(쉼표로 연결된 문자열), criteria
#    - 출력: 선택된 하나의 회사명 (문자열)
#    - 선택 기준은 criteria로 주입(예: '짧고 기억에 잘 남고 .com 도메인 확보 가능성 높음')
# ============================================================
select_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 브랜드 네이밍 심사위원입니다. 주어진 후보 중 가장 뛰어난 1개만 선택하세요."),
    ("human",
     "제품/서비스: {product}\n"
     "선택 기준: {criteria}\n"
     "후보 목록(쉼표 구분): {candidates}\n\n"
     "위 기준에 가장 부합하는 회사명 1개만 '정확히 그 이름만' 출력하세요.")
])

select_chain = select_prompt | llm | to_str

# ============================================================
# [4] 선택된 회사명으로 캐치프레이즈(슬로건) 생성 체인
#    - 입력: company_name
#    - 출력: 슬로건 1개 (문자열)
# ============================================================
slogan_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 브랜드 카피라이터입니다. 간결하고 임팩트 있는 한국어 슬로건을 작성하세요."),
    ("human", "회사명: {company_name}\n이 회사에 어울리는 캐치프레이즈를 1개 작성해줘.")
])

slogan_chain = slogan_prompt | llm | to_str

# ============================================================
# [5] 파이프라인 조립 (Runnable 기반)
#    - 입력: {"product": str, "count": int=5, "criteria": str=...}
#    - 단계:
#       A) 회사명 후보 리스트 생성
#       B) 후보 리스트와 product를 함께 전달 → 최적 1개 선택
#       C) 선택된 회사명으로 슬로건 생성
#    - 출력: dict { "candidates": List[str], "company_name": str, "catch_phrase": str }
# ============================================================

# (A) 후보 리스트 생성 노드
generate_candidates_node = (
    RunnableLambda(lambda x: {"product": x["product"], "count": x.get("count", 5)})
    | name_list_chain
)

# (B) 후보 + product를 묶어 선택 체인 호출할 입력 구성
prepare_selection_inputs = RunnableLambda(lambda d: {
    # d: {"product": ..., "count": ..., "criteria": ..., "candidates": ...} 형태를 만들기 위해
    # RunnableParallel에서 product/criteria와 candidates를 합쳐준다.
    "product": d["product"],
    "criteria": d.get("criteria", "짧고 기억에 잘 남으며 발음이 쉬움"),
    "candidates_list": d["candidates"]  # List[str]
})

# (C) 선택 체인 호출 → 하나의 회사명
run_selection = RunnableLambda(lambda s: {
    "product": s["product"],
    "candidates_list": s["candidates_list"],
    "company_name": select_chain.invoke({
        "product": s["product"],
        "criteria": s["criteria"],
        "candidates": ", ".join(s["candidates_list"])
    }).strip()
})

# (D) 슬로건 체인 호출 → 최종 결과 합치기
run_slogan = RunnableLambda(lambda z: {
    "candidates": z["candidates_list"],
    "company_name": z["company_name"],
    "catch_phrase": slogan_chain.invoke({"company_name": z["company_name"]}).strip()
})

# 전체 파이프라인:
#  - RunnableParallel로 원본 입력에서 product/criteria pass-through + 후보 생성 병렬 구성
pipeline = (
    RunnableParallel({
        "product": RunnableLambda(lambda x: x["product"]),
        "criteria": RunnableLambda(lambda x: x.get("criteria", "짧고 기억에 잘 남으며 발음이 쉬움")),
        "candidates": generate_candidates_node
    })
    | prepare_selection_inputs
    | run_selection
    | run_slogan
)

# ============================================================
# [6] 실행 예시
# ============================================================
if __name__ == "__main__":
    # 입력 파라미터
    inputs = {
        "product": "웹게임",
        "count": 5,  # 회사명 후보 생성 개수
        "criteria": "짧고 기억에 잘 남고, 한국/글로벌 모두 발음하기 쉬움"
    }

    result = pipeline.invoke(inputs)

    print("\n[회사명 후보]")
    for i, name in enumerate(result["candidates"], start=1):
        print(f" - {i}. {name}")

    print("\n[선정된 회사명]")
    print(" →", result["company_name"])

    print("\n[캐치프레이즈]")
    print(" →", result["catch_phrase"])
