# pip install chromadb tiktoken langchain-chroma
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma

# 1. .env 파일에서 OpenAI API 키 로드
load_dotenv(dotenv_path='../.env')

# 2. Chroma 벡터 DB 저장 디렉토리
PERSIST_DIR = "../chroma_db"
COLLECTION_NAME = "nvme"

# 2-1. 최초 1회 실행 시: 문서 로드 → 임베딩 → Chroma DB에 저장
def create_vector_db():
    loader = TextLoader('../DATA/nvme.txt', encoding='utf-8')
    documents = loader.load()

    # 원본 문서에 source, page 추가 (page는 기본 1로 가정)
    for doc in documents:
        doc.metadata.update({"source": "nvme.txt", "page": 1})

    # 문서 분할 (1000자 단위, 100자 중복 유지)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    # chunk_id 부여
    for i, chunk in enumerate(texts, start=1):
        chunk.metadata.update({"chunk_id": i})
        
    # 임베딩 생성 및 Chroma DB에 저장 (collection 이름 지정, 저장 경로 지정)
    embeddings = OpenAIEmbeddings()
    store = Chroma.from_documents(texts, embeddings, collection_name=COLLECTION_NAME, persist_directory=PERSIST_DIR)
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
    store = create_vector_db()


# 4. OpenAI ChatGPT 모델 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 5. 프롬프트 템플릿 정의 (문서 기반 + 규칙 명시)
template2 = """주어진 문서들을 참고하여 질문에 답변해주세요.

문서 내용: 
{context}

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
retriever = store.as_retriever(search_kwargs={"k": 5})  # 유사도 기준 상위 5개 문서 검색

# 질의응답을 위한 결과 및 메타데이터 일부 추가 표시
def format_docs_with_meta(docs):
    if not docs:
        return "관련 문서를 찾지 못했습니다."
    parts = []
    for i, d in enumerate(docs, start=1):
        src = d.metadata.get("source", "unknown")
        cid = d.metadata.get("chunk_id", "?")
        page = d.metadata.get("page", "?")
        parts.append(f"문서 {i}: [출처: {src}:{cid} (page {page})]\n{d.page_content.strip()}")
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

# 7. 질문을 받아 답변 + 출처를 포멧에 맞게 반환하는 함수
def answer_question_with_nochain(question):
    # 7-1. 질문마다 직접 문서를 뽑아서 텍스트로 변환
    docs = retriever.invoke(question)
    ctx = format_docs_with_meta(docs)

    # 7-2. 프롬프트 → LLM
    prompt_value = prompt.invoke({"context": ctx, "question": question})
    answer_msg = llm.invoke(prompt_value)
    answer = StrOutputParser().invoke(answer_msg)
    
    # 7-3. 최종 결과 출력
    print(f"\n=====\n질문: {question}\n---\n응답: {answer}\n=====\n")

def answer_question(question):
    # 7-1. 체인 실행
    result = chain.invoke(question)
    answer = result.strip()

    # 7-2. 최종 결과 출력
    print(f"\n=====\n질문: {question}\n---\n응답: {answer}\n=====\n")


# 8. 테스트 질문 실행
answer_question("NVME와 SATA의 차이점을 100글자로 요약해줘")
# answer_question("PCIe는?")
# answer_question("우주의 크기는 얼마나 되나요?")  # 문서에 없는 질문 → 예외 처리 확인
