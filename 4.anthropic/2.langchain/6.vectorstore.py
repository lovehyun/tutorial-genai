# pip install chromadb langchain-chroma langchain-openai

import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 환경 변수 로드
load_dotenv()

# API 키 가져오기
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# 샘플 문서 생성 (실제 사용 시 이 부분을 제거하고 기존 문서 사용)
sample_text = """
인공지능(AI)은 컴퓨터 시스템이 인간의 지능을 모방하여 학습, 추론, 자가 수정 능력을 갖추는 기술입니다.

인공지능의 윤리적 문제:
1. 프라이버시 침해: AI는 방대한 개인 데이터를 수집하고 분석할 수 있어 프라이버시 침해 우려가 있습니다.
2. 편향과 차별: AI 시스템은 학습 데이터의 편향을 그대로 반영할 수 있어 불공정한 결정을 내릴 수 있습니다.
3. 자율성과 책임: 자율적 AI 시스템의 결정에 대한 책임 소재가 불분명합니다.
4. 일자리 대체: 자동화로 인한 일자리 감소와 경제적 불평등이 심화될 수 있습니다.
5. 안전과 보안: 군사용 AI나 자율 무기 시스템의 위험성이 증가합니다.

인공지능의 발전 방향:
현재 AI는 딥러닝과 신경망 기술의 발전으로 급속도로 성장하고 있습니다.
미래에는 더욱 인간과 유사한 일반 인공지능(AGI)으로 발전할 가능성이 있습니다.
AI는 의료, 교육, 운송, 금융 등 다양한 산업 분야를 혁신하고 있습니다.
"""

# 샘플 문서 저장
with open("ai_sample.txt", "w", encoding="utf-8") as f:
    f.write(sample_text)

# Claude 모델 초기화
llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    anthropic_api_key=anthropic_api_key,
    temperature=0.7,
    max_tokens=1000
)

# 문서 로드
loader = TextLoader("ai_sample.txt", encoding="utf-8")
documents = loader.load()

# 텍스트 분할
text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=1000,
    chunk_overlap=200
)
docs = text_splitter.split_documents(documents)

print(f"문서가 {len(docs)}개의 청크로 분할되었습니다.")

# 임베딩 모델 초기화
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# 벡터 데이터베이스 생성
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# 유사도 검색
query = "인공지능의 윤리적 문제는 무엇인가요?"
similar_docs = vectorstore.similarity_search(query, k=3)

print(f"질문: {query}")
print(f"관련 문서 {len(similar_docs)}개를 찾았습니다.")

for i, doc in enumerate(similar_docs):
    print(f"\n관련 문서 #{i+1}:")
    print(doc.page_content[:150] + "...")

# LCEL 기반 RAG 체인
retriever = vectorstore.as_retriever()

prompt = ChatPromptTemplate.from_template(
    "다음 문서를 참고하여 질문에 답변해주세요.\n\n"
    "문서:\n{context}\n\n질문: {question}"
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

result = rag_chain.invoke(query)
print("\n최종 답변:")
print(result)
