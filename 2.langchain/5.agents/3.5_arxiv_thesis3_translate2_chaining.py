# 필요한 패키지
# pip install langchain_openai arxiv python-dotenv

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain_community.tools.arxiv.tool import ArxivQueryRun

# 0) 환경 변수 로드 (OPENAI_API_KEY 등)
load_dotenv()

# 1) LLM 준비
llm_summary   = ChatOpenAI(model="gpt-4o-mini", temperature=0)    # 영문 요약(결정적)
llm_translate = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)  # 한글 번역(자연스러움)

# 2) arXiv 검색기 구성 (최신순 상위 5건)
arxiv = ArxivAPIWrapper(
    top_k_results=5,
    load_max_docs=5,
    sort_by="lastUpdatedDate",
    sort_order="descending",
)
tool = ArxivQueryRun(api_wrapper=arxiv)

# 3) 영문 요약 프롬프트
sum_prompt = ChatPromptTemplate.from_template(
    """Summarize the arXiv results below into concise English:
- For ~5 papers: Title / Authors / Year / Key Contributions / Limitations(if any) / arXiv ID
- End with 3 bullet points on 'Recent Trends'
- Do not hallucinate.

[Results]
{raw}
"""
)

# 4) 한국어 번역 프롬프트
trans_prompt = ChatPromptTemplate.from_template(
    "아래 영문 요약을 자연스럽고 정확한 한국어로 번역해 주세요:\n\n{text}"
)

# 5) 파이프라인 구성: 검색 → 영문 요약 → {english, korean} 동시 출력
pipeline = (
    # (a) 검색 실행: {"query": "..."} → {"raw": "...arxiv text..."}
    RunnableLambda(lambda x: {"raw": tool.run(x["query"])})
    # (b) 영문 요약: {"raw": "..."} → "english summary text"
    | (sum_prompt | llm_summary | StrOutputParser())
    # (c) 분기: 최종적으로 {"english": "...", "korean": "..."} 반환
    | { # 한국어/영어 동시(병렬) 실행
        "english": RunnableLambda(lambda s: s),
        "korean": (
            RunnableLambda(lambda s: {"text": s})
            | trans_prompt
            | llm_translate
            | StrOutputParser()
        ),
    }
)

# {"english": ..., "korean": ...} 형태의 딕셔너리 Runnable은 LangChain에서 Parallel mapping으로 처리됩니다.
# 즉, "english"와 "korean" 키에 해당하는 Runnable이 서로 독립적으로 동시에 실행됩니다.


# 질의는 주제+보조키워드로 구체화 권장
query = 'deep learning AND (survey OR overview OR foundation model)'
result = pipeline.invoke({"query": query})

print("\n[English Summary]\n", result["english"])
print("\n[Korean Translation]\n", result["korean"])
