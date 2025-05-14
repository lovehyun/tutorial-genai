# pip install chromadb tiktoken langchain-chroma

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# 1. .env 파일에서 OpenAI API 키 로드
load_dotenv(dotenv_path='../.env')

# 2. Chroma 벡터 DB 저장 디렉토리
PERSIST_DIR = "./chroma_db"

# 2-1. 최초 1회 실행 시: 문서 로드 → 임베딩 → Chroma DB에 저장
def create_vector_db():
    # 문서 로딩 (euc-kr 인코딩)
    loader = TextLoader('./nvme.txt', encoding='euckr')
    documents = loader.load()

    # 각 문서에 출처 메타데이터 추가
    documents = [Document(page_content=doc.page_content, metadata={"source": "nvme.txt"}) for doc in documents]

    # 문서 분할 (1000자 단위, 100자 중복 유지)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    # 임베딩 생성 및 Chroma DB에 저장 (collection 이름 지정, 저장 경로 지정)
    embeddings = OpenAIEmbeddings()
    store = Chroma.from_documents(
        texts, 
        embeddings, 
        collection_name="nvme",
        persist_directory=PERSIST_DIR
    )
    return store

# 2-2. 이미 저장된 벡터 DB가 있을 경우: 불러오기
def load_vector_db():
    embeddings = OpenAIEmbeddings()
    store = Chroma(
        collection_name="nvme",
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR
    )
    return store

# 3. 저장된 DB가 있으면 로드, 없으면 새로 생성
if os.path.exists(PERSIST_DIR):
    store = load_vector_db()
else:
    store = create_vector_db()

# 4. OpenAI ChatGPT 모델 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 5. 프롬프트 템플릿 정의 (문서 기반 + 규칙 명시)
template2 = """주어진 문서들을 참고하여 질문에 답변해주세요.

문서 내용: {context}

질문: {question}

답변 작성 규칙:
1. 자연스러운 한국어로 작성하세요
2. 문서에 없는 내용은 "죄송합니다. 주어진 문서에서 해당 정보를 찾을 수 없습니다."라고 답변하세요
3. 문서의 내용을 바탕으로 명확하고 이해하기 쉽게 설명하세요
4. 기술적인 용어가 나오면 가능한 풀어서 설명해주세요
"""

# 6. 프롬프트 + 검색 + LLM + 출력 포맷 체인 구성
prompt = ChatPromptTemplate.from_template(template2)
retriever = store.as_retriever(search_kwargs={"k": 5})  # 유사도 기준 상위 5개 문서 검색

chain = (
    {"context": retriever, "question": lambda x: x}  # context는 문서, question은 사용자 질문
    | prompt
    | llm
    | StrOutputParser()  # 결과를 문자열로 출력
)

# 7. 질문을 받아 답변 + 출처를 포맷에 맞게 반환하는 함수 (7-1, 7-2는 생략가능. 바로 7-3부터 실행 가능.)
def answer_question(question):
    try:
        # 7-1. 관련 문서 직접 가져오기
        docs = retriever.get_relevant_documents(question)

        # 7-2. context 생성: 문서 내용 + 출처 함께 구성
        context = ""
        sources = []
        for i, doc in enumerate(docs, start=1):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "N/A")
            sources.append(f"{source} (page {page})")
            context += f"[출처: {source}, 페이지: {page}]\n{doc.page_content.strip()}\n\n"

        # 7-3. 체인 실행
        # result = chain.invoke(question) # 체인을 통해서 context 수행 (get_relevant_documents 가 자동으로 추출)
        result = chain.invoke({"context": context, "question": question})
        answer = result.strip()

        # 7-4. 의미 없는 응답 필터링
        if not answer or answer.lower() in ["i don't know.", "i don’t know."]:
            return f"질문: {question}\n응답: 죄송합니다. 주어진 문서에서 해당 정보를 찾을 수 없습니다.\n"

        # 7-5. 결과 반환
        return f"질문: {question}\n응답: {answer}\n출처: {', '.join(sources)}\n"

    except Exception as e:
        return f"질문: {question}\n응답: 오류가 발생했습니다: {str(e)}\n"

# 8. 테스트 질문 실행
print(answer_question("NVME와 SATA의 차이점을 100글자로 요약해줘"))
print(answer_question("PCIe는?"))
print(answer_question("우주의 크기는 얼마나 되나요?"))  # 문서에 없는 질문 → 예외 처리 확인
