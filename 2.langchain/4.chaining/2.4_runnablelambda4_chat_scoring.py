from dotenv import load_dotenv
import os, json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser, StrOutputParser
from langchain_core.runnables import RunnableLambda

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
# - temperature는 0.7로 네이밍 다양성 확보
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
to_str = StrOutputParser()

# ============================================================
# [2] 회사명 후보 다발 생성 체인
#    - 입력: product, count
#    - 출력: 후보 이름 리스트(List[str])
#    - CSV 파서로 안정적 파싱
# ============================================================
name_list_parser = CommaSeparatedListOutputParser()
format_hint = name_list_parser.get_format_instructions()

name_list_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 전문 작명 컨설턴트입니다. 한국어로 창의적인 회사명을 제안하세요."),
    ("human",
     "다음 제품/서비스를 만드는 회사명을 {count}개 제안해줘. "
     "각 후보는 간결하고 발음이 쉬워야 합니다. 제품: {product}\n"
     "반드시 아래 형식으로만 출력하세요.\n{format_hint}")
]).partial(format_hint=format_hint)

name_list_chain = name_list_prompt | llm | name_list_parser

# ============================================================
# [3] 후보 점수화(Scoring) 체인
#    - 입력: product, criteria, candidates(List[str])
#    - 출력: JSON 파싱된 리스트[ {candidate, score, reason}, ... ]
#    - 안전을 위해 LLM 출력 → 문자열 → json.loads 로 파싱
# ============================================================
score_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 브랜드 네이밍 심사위원입니다. 후보를 0~100점으로 채점하고 간단한 이유를 덧붙이세요. "
     "정확한 JSON만 출력하세요."),
    ("human",
     "제품/서비스: {product}\n"
     "평가 기준: {criteria}\n"
     "후보 목록: {candidates}\n\n"
     "아래 JSON 형식만 출력하세요(다른 말 금지). "
     '예시: [{{"candidate":"이름","score":87,"reason":"간결/기억 용이"}}]\n'
     "JSON:")
])

def _safe_json_loads(s: str):
    try:
        data = json.loads(s)
        if not isinstance(data, list):
            raise ValueError("JSON 루트는 list 여야 합니다.")
        # 최소 필드 검증
        for item in data:
            if not all(k in item for k in ("candidate", "score")):
                raise ValueError("각 항목에 candidate, score 필드가 필요합니다.")
        return data
    except Exception as e:
        raise ValueError(f"JSON 파싱 실패: {e}")

score_chain = score_prompt | llm | to_str | RunnableLambda(_safe_json_loads)

# ============================================================
# [4] 슬로건 체인
#    - 입력: company_name
#    - 출력: 슬로건 문자열(1개)
# ============================================================
slogan_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 브랜드 카피라이터입니다. 간결하고 임팩트 있는 한국어 슬로건을 작성하세요."),
    ("human", "회사명: {company_name}\n이 회사에 어울리는 캐치프레이즈를 1개 작성해줘.")
])
slogan_chain = slogan_prompt | llm | to_str

# ============================================================
# [5] 파이프라인 함수
#    - generate_candidates(product, count)
#    - score_candidates(product, criteria, candidates_list)
#    - select_top(candidates_scored, top_n=3)
#    - make_slogans(top_list)  # 각 회사명별 슬로건 생성
# ============================================================
def generate_candidates(product: str, count: int = 7):
    return name_list_chain.invoke({"product": product, "count": count})

def score_candidates(product: str, criteria: str, candidates_list):
    return score_chain.invoke({
        "product": product,
        "criteria": criteria,
        "candidates": ", ".join(candidates_list)
    })

def select_top(scored_list, top_n: int = 3):
    # score 내림차순 → 동점이면 candidate 사전순
    sorted_items = sorted(
        scored_list,
        key=lambda x: (-int(x.get("score", 0)), str(x.get("candidate", "")))
    )
    return sorted_items[: min(top_n, len(sorted_items))]

def make_slogans(top_items):
    # top_items: [{candidate, score, reason?}, ...]
    results = []
    for item in top_items:
        name = item["candidate"]
        slogan = slogan_chain.invoke({"company_name": name}).strip()
        results.append({
            "company_name": name,
            "score": int(item.get("score", 0)),
            "reason": item.get("reason", ""),
            "catch_phrase": slogan
        })
    return results

# ============================================================
# [6] 엔드투엔드 실행 함수
#    - 입력: product, criteria, count(후보 개수), top_n(상위 N개)
#    - 출력: dict {
#         "candidates": [str...],
#         "scored": [{"candidate","score","reason"}...],
#         "top": [{"company_name","score","reason","catch_phrase"}...]
#      }
# ============================================================
def run_pipeline(product: str,
                 criteria: str = "짧고 기억에 잘 남고, 한국/글로벌 모두 발음하기 쉬움",
                 count: int = 7,
                 top_n: int = 3):
    candidates = generate_candidates(product, count=count)
    scored = score_candidates(product, criteria, candidates)
    top_items = select_top(scored, top_n=top_n)
    top_with_slogans = make_slogans(top_items)
    return {
        "candidates": candidates,
        "scored": scored,
        "top": top_with_slogans
    }

# ============================================================
# [7] 실행 예시
# ============================================================
if __name__ == "__main__":
    product = "웹게임"
    criteria = "짧고 기억에 잘 남고, 한국/글로벌 모두 발음하기 쉬움. .com 도메인 확보 가능성도 고려."
    result = run_pipeline(product, criteria=criteria, count=7, top_n=3)

    print("\n[회사명 후보]")
    for i, name in enumerate(result["candidates"], start=1):
        print(f" - {i}. {name}")

    print("\n[후보 점수(상위 표시 전 전체)]")
    for item in sorted(result["scored"], key=lambda x: -int(x.get("score", 0))):
        print(f" - {item['candidate']}: {item['score']}점 | {item.get('reason','')}")

    print("\n[상위 Top N (슬로건 포함)]")
    for i, item in enumerate(result["top"], start=1):
        print(f"#{i}. {item['company_name']} ({item['score']}점)")
        if item.get("reason"):
            print(f"   - 선택 이유: {item['reason']}")
        print(f"   - 캐치프레이즈: {item['catch_phrase']}")
