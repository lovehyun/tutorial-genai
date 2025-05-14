# 필요한 패키지 설치
# pip install pypdf langchain-chroma

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma

# .env 파일에서 OpenAI API 키 로드
load_dotenv(dotenv_path='../.env')

# PDF 파일 및 Chroma 저장 경로 설정
PDF_FILENAME = './DATA/Python_시큐어코딩_가이드(2023년_개정본).pdf'
PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "secure_coding_python"

# Chroma DB를 새로 생성하는 함수
def create_vector_db(file_path):
    try:
        # PDF 문서 로딩
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"총 {len(documents)} 페이지의 문서가 로드되었습니다.")

        # 각 페이지에 메타데이터 추가: 파일명, 페이지번호
        for doc in documents:
            doc.metadata["source"] = os.path.basename(file_path)
            if "page" not in doc.metadata:
                doc.metadata["page"] = doc.metadata.get("page", 0) + 1

    except Exception as e:
        print(f"PDF 파일을 로드하는 동안 오류가 발생했습니다: {e}")
        return None

    # 첫 번째 내용 있는 페이지 출력
    for i, doc in enumerate(documents):
        if doc.page_content.strip():
            print(f"내용이 있는 첫 번째 페이지 번호: {doc.metadata['page']}")
            print(f"내용 샘플: {doc.page_content[:500]}...")
            break

    # 문서 분할 (tiktoken 기준, 중복 500자)
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n\n",
        chunk_size=2000,
        chunk_overlap=500,
    )
    texts = text_splitter.split_documents(documents)

    # 중복 청크 제거 (같은 텍스트 반복 방지)
    seen = {}
    unique_texts = []
    for text in texts:
        if text.page_content not in seen:
            seen[text.page_content] = True
            unique_texts.append(text)

    # OpenAI 임베딩 생성 및 Chroma에 저장
    embeddings = OpenAIEmbeddings()
    store = Chroma.from_documents(
        unique_texts,
        embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR
    )
    return store

# 기존 Chroma DB 로드
def load_vector_db():
    embeddings = OpenAIEmbeddings()
    store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR
    )
    return store

def check_collection_exists(persist_dir, collection_name):
    try:
        embeddings = OpenAIEmbeddings()
        store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_dir
        )
        # 임의 호출: 문서 일부 조회
        results = store.get(include=[])
        # 빈 컬렉션이라면 len(results["ids"]) == 0
        return len(results["ids"]) > 0
    except Exception as e:
        print(f"컬렉션 존재 여부 확인 중 오류: {e}")
        return False

# DB내에 문서 존재 여부 확인
if check_collection_exists(PERSIST_DIR, COLLECTION_NAME):
    store = load_vector_db()
else:
    store = create_vector_db(PDF_FILENAME)
    if store is None:
        raise Exception("벡터 DB 생성에 실패했습니다.")

# ChatGPT LLM 초기화 (정확한 응답을 위한 temperature 0)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 질문 프롬프트 정의 (출처 포함, 구조화된 규칙 포함)
template = """주어진 문서 내용을 바탕으로 질문에 답변해주세요.

문서 내용: {context}

질문: {question}

답변 작성 규칙:
1. 명확하고 구조적으로 답변을 작성하세요
2. 시큐어 코딩 관련 내용은 실제 코드 예시나 구체적인 대응방안을 포함하세요
3. 리스트 형태로 요청된 경우, 번호를 매겨 구분하여 작성하세요
4. 보안 취약점과 그에 대한 대응방안을 함께 설명하세요
"""

prompt = ChatPromptTemplate.from_template(template)

# 검색기 구성 (문서 중 관련성 높은 5개 청크 검색)
retriever = store.as_retriever(search_kwargs={"k": 5})

# 체인 구성: 검색 → 프롬프트 → LLM → 출력 파싱
chain = (
    # {"context": retriever, "question": lambda x: x}
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 7. 질문을 받아 답변 + 출처를 포맷에 맞게 반환하는 함수 (7-1, 7-2는 생략가능. 바로 7-3부터 실행 가능.)
def answer_question(question):
    try:
        # 7-1. 관련 문서 직접 검색
        docs = retriever.get_relevant_documents(question)

        # 7-2. context 구성: 문서 내용 + 출처 함께 표시
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

        # 7-4. 응답이 없거나 의미 없을 경우
        if not answer or answer.lower() in ["i don't know.", "죄송합니다. 주어진 문서에서 해당 정보를 찾을 수 없습니다."]:
            return f"질문: {question}\n응답: 죄송합니다. 해당 질문에 대한 적절한 답변을 찾을 수 없습니다.\n"

        # 7-5. 최종 출력
        return f"질문: {question}\n\n답변:\n{answer}\n\n참고 문서:\n" + "\n".join(sources)
    
    except Exception as e:
        return f"질문: {question}\n오류 발생: {str(e)}\n"

# 테스트 질문 실행
try:
    print(answer_question("시큐어코딩의 주요 기법들에 대해서 리스트 형태로 요약해서 설명해줘"))
    print(answer_question("입력데이터 검증 및 오류 기법에 대해서 상세히 설명해줘"))
except Exception as e:
    print(f"질문 처리 중 오류가 발생했습니다: {e}")
