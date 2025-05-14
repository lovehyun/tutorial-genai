import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_chroma import Chroma

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

PERSIST_DIR = './chroma_db'
COLLECTION_NAME = 'my-data'
store = None

def get_store():
    return store

# 초기 로딩 함수
def initialize_vector_db():
    global store
    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
        store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=OpenAIEmbeddings(),
            persist_directory=PERSIST_DIR
        )
        
def create_vector_db(file_path):
    global store
    
    # 1. PDF 문서 로딩
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # 2. 문서 분할
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    # 3. 임베딩 모델
    embeddings = OpenAIEmbeddings()

    # 4. 저장 폴더 없으면 생성
    if not os.path.exists(PERSIST_DIR):
        os.makedirs(PERSIST_DIR)

    # 5. 기존 DB가 있으면 불러와서 추가
    if os.path.isdir(PERSIST_DIR) and os.listdir(PERSIST_DIR):
        store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=PERSIST_DIR
        )
        store.add_documents(texts)
    else: # 없으면 새로 생성
        store = Chroma.from_documents(
            texts,
            embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=PERSIST_DIR
        )

    return store


# LLM 준비 (gpt-3.5-turbo 기반)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 출력 파서
output_parser = StrOutputParser()

# 프롬프트 템플릿 정의
prompt = ChatPromptTemplate.from_template("""
당신은 문서 기반 질문 응답 시스템입니다.
다음 문서를 참고하여 사용자의 질문에 답변해 주세요. 
모르겠다면 절대로 지어내지 말고 "모르겠습니다"라고 답하세요.

문서:
{context}

질문:
{question}

답변:
""")

prompt2 = ChatPromptTemplate.from_template("""
당신은 문서 기반 질문 응답 시스템입니다.
다음 문서를 참고하여 사용자의 질문에 답변해 주세요. 
각 문서에는 번호가 붙어 있습니다. 응답 후 어떤 문서 번호가 가장 관련 있었는지도 알려주세요.
모르겠다면 절대로 지어내지 말고 "모르겠습니다"라고 답하세요.

문서:
{context}

질문:
{question}

답변:
""")

def answer_question(question: str) -> str:
    global store
    if store is None:
        return "문서가 로드되지 않았습니다. 먼저 PDF를 업로드해주세요."

    # 1. 벡터 DB에서 유사 문서 검색 (점수 포함)
    docs_with_scores = store.similarity_search_with_score(question, k=5)

    # 2. context 구성
    # context = "\n\n".join([doc.page_content for doc, _ in docs_with_scores])
    context = "\n\n".join(
        [f"[문서 {i+1}] (score {round((1 - score) * 100, 2)}%)\n{doc.page_content}"
        for i, (doc, score) in enumerate(docs_with_scores)]
    )
    print(context)
    
    # 3. LLM 체인 실행
    chain = prompt2 | llm | output_parser
    try:
        result = chain.invoke({
            "context": context,
            "question": question
        })
    except Exception as e:
        return f"GPT 처리 중 오류: {e}"

    # 4. 출처 + 유사도 정보 추출
    source_lines = []
    for doc, score in docs_with_scores:
        source = os.path.basename(doc.metadata.get("source", "unknown"))
        page = int(doc.metadata.get("page", 0)) + 1
        score_percent = round((1 - score) * 100, 2)  # 유사도는 낮을수록 가까움 → 반전
        source_lines.append(f"{source} (page {page}, 유사도 {score_percent}%)")

    # 중복 제거 + 정렬
    source_lines = sorted(set(source_lines))

    # 5. 최종 출력
    return (
        f"질문: {question}\n"
        f"응답: {result.strip()}\n"
        f"관련 문서:\n" + "\n".join(f" - {line}" for line in source_lines)
    )
