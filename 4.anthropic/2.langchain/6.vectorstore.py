# pip install chromadb

import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

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
    model="claude-3-7-sonnet-20250219",  # 최신 모델
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

# 관련 문서 내용 출력
for i, doc in enumerate(similar_docs):
    print(f"\n관련 문서 #{i+1}:")
    print(doc.page_content[:150] + "...")  # 문서 내용 일부만 출력

# 검색 결과를 기반으로 답변 생성
retrieval_qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    verbose=True
)

result = retrieval_qa.invoke({"query": query})
print("\n최종 답변:")
print(result["result"])


# 임시 파일 삭제 (선택 사항)

# 벡터스토어를 참조하는 변수를 해제하여 리소스를 정리
# 최신 Chroma 버전에서는 persist() 메서드는 더 이상 필요 없으며 close() 메서드도 현재 버전에서 지원되지 않음
# retrieval_qa = None
# vectorstore = None
# embeddings = None

# # 약간의 시간 지연을 줘서 리소스가 해제되도록 함
# import time
# import shutil
# print("\n리소스 정리 중...")
# time.sleep(3)

# try:
#     if os.path.exists("./chroma_db"):
#         shutil.rmtree("./chroma_db")
#     if os.path.exists("ai_sample.txt"):
#         os.remove("ai_sample.txt")
#     print("임시 텍스트 파일이 삭제되었습니다.")
# except Exception as e:
#     print(f"파일 삭제 중 오류 발생: {e}")
