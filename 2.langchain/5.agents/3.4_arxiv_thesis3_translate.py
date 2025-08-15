# pip install langchain_openai arxiv python-dotenv
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain_community.tools.arxiv.tool import ArxivQueryRun


# 0. 환경 변수 로드
load_dotenv()

# 1. ChatOpenAI로 LLM 설정 (논문 검색용 및 번역용 분리)
llm_summary = ChatOpenAI(model="gpt-4o-mini", temperature=0)      # 요약
llm_translate = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)  # 번역 톤 자유도↑

# 2. 검색기 세팅: 최신순, 상위 5건
arxiv = ArxivAPIWrapper(top_k_results=5, load_max_docs=5,
                        sort_by="lastUpdatedDate", sort_order="descending")
tool = ArxivQueryRun(api_wrapper=arxiv)

# 3. 질의 실행
raw = tool.run('deep learning AND (survey OR overview OR foundation model)')

# 4. 프롬프트 생성 (영문 요약)
sum_prompt = ChatPromptTemplate.from_template(
    """Summarize the arXiv results below into concise English:
- For 5 papers: Title / Authors / Year / Key Contributions / Limitations(if any) / arXiv ID
- End with 3 bullet points on 'Recent Trends'
- Do not hallucinate.

[Results]
{raw}
""")

# 4-1. 한줄로 체인 생성 및 실행
english_summary = (sum_prompt | llm_summary).invoke({"raw": raw}).content

# 4-2. 두줄로 체인 생성 및 실행
# chain = sum_prompt | llm_summary | RunnableLambda(lambda x: x.content.strip())
# english_summary = chain.invoke({"raw": raw})

# 5. 한국어 번역
trans_prompt = ChatPromptTemplate.from_template(
    "다음을 자연스럽고 정확하게 한국어로 번역해줘:\n\n{text}"
)
translation_chain = trans_prompt | llm_translate | RunnableLambda(lambda x: {"ko": x.content.strip()})
translated = translation_chain.invoke({"text": english_summary})["ko"]

print("\n[English Summary]\n", english_summary)
print("\n[Korean Translation]\n", translated)
