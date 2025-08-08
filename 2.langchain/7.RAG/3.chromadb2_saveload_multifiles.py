# pip install chromadb tiktoken langchain-chroma
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma

# 1. .env 파일에서 OpenAI API 키 로드
load_dotenv(dotenv_path='../.env')

# 2. Chroma 벡터 DB 저장 디렉토리
PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "my_collection_name"
FILES = ["./nvme.txt", "./ssd.txt"]

splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

# 2-1. 최초 1회 실행 시: 문서 로드 → 임베딩 → Chroma DB에 저장
def build_chunks_per_file(file_paths):
    """파일별로 split하고, 파일 내부에서 chunk_id를 1부터 부여"""
    all_chunks = []
    for path in file_paths:
        # 보통 TextLoader는 한 개 Document를 반환하지만 리스트 형태이므로 all_chunks 에 합칩니다.
        loader = TextLoader(path, encoding='utf-8')
        docs = loader.load()
        
        # 파일 메타 부여
        for d in docs:
            d.metadata.update({"source": os.path.basename(path)})

        # 파일 단위로 분할
        file_chunks = splitter.split_documents(docs)
        # 여기서 파일 내부 chunk_id를 1부터
        for i, chunk in enumerate(file_chunks, start=1):
            chunk.metadata.update({"chunk_id": i}) # 파일 내부 chunk 번호
        
        all_chunks.extend(file_chunks)

    return all_chunks

def create_vector_db(file_paths=FILES):
    chunks = build_chunks_per_file(file_paths)
    embeddings = OpenAIEmbeddings()
    store = Chroma.from_documents(chunks, embedding=embeddings, collection_name=COLLECTION_NAME, persist_directory=PERSIST_DIR)
    return store

# 2-2. 이미 저장된 벡터 DB가 있을 경우: 불러오기
def load_vector_db():
    embeddings = OpenAIEmbeddings()
    store = Chroma(collection_name=COLLECTION_NAME, embedding_function=embeddings, persist_directory=PERSIST_DIR)
    return store

# 3. 저장된 DB가 있으면 로드, 없으면 새로 생성
import os
if os.path.exists(PERSIST_DIR):
    print("기존 데이터베이스를 로딩합니다.")
    store = load_vector_db()
else:
    print("새로운 데이터베이스를 생성합니다.")
    store = create_vector_db(FILES)


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
5. 답변에는 출처를 추가해 주세요
"""

# 6. 프롬프트 + 검색 + LLM + 출력 포맷 체인 구성
prompt = ChatPromptTemplate.from_template(template2)
retriever = store.as_retriever(search_kwargs={"k": 3})  # 유사도 기준 상위 3개 문서 검색

def format_docs_with_meta(docs):
    if not docs:
        return "관련 문서를 찾지 못했습니다."
    parts = []
    for i, d in enumerate(docs, start=1):
        src = d.metadata.get("source", "unknown")
        cid = d.metadata.get("chunk_id", "?")
        parts.append(f"문서 {i}: [출처: {src}:{cid}]\n{d.page_content.strip()}")
    return "\n\n---\n\n".join(parts)

def peek_prompt(prompt_value):  # 디버깅용 함수
    print("=== LLM 직전 프롬프트 ===")
    print(prompt_value.to_string())
    return prompt_value  # 반드시 그대로 반환해서 체인이 계속 흘러가게 함

chain = (
    {"context": retriever | RunnableLambda(format_docs_with_meta),
     "question": lambda x: x}  # context는 문서, question은 사용자 질문
    | prompt
    | RunnableLambda(peek_prompt)  # <- 여기서 디버깅용 프린트
    | llm
    | StrOutputParser()  # 결과를 문자열로 출력
)

# 7. 질문을 받아 답변 + 출처를 포맷에 맞게 반환하는 함수
def answer_question(question):
    # 7-1. 체인 실행
    result = chain.invoke(question)
    answer = result.strip()

    # 7-2. 결과 반환
    print(f"\n=====\n질문: {question}\n---\n응답: {answer}\n=====\n")


# 8. 테스트 질문 실행
answer_question("NVME와 SATA의 차이점을 100글자로 요약해줘")
# answer_question("PCIe는?")
# answer_question("우주의 크기는 얼마나 되나요?")  # 문서에 없는 질문 → 예외 처리 확인
