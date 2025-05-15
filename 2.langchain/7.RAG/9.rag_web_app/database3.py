# pip install pyyaml
import os
import yaml
import json
from typing import Dict
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

VECTOR_DB = './chroma_db'
DATA_DIR = './DATA'
COLLECTION_NAME = 'my-data'
store = None

# 전역 선언
llm = None
output_parser = None
prompts = None
PROMPT_FILE = "prompts.yaml"

# 저장된 store 가져오기
def get_store():
    return store

# 프롬프트 로딩 함수 - 하나의 KEY 기반 (load_prompt_from_json(PROMPT_FILE, "scored_prompt"))
def load_prompt_from_json(json_path: str, prompt_name: str) -> ChatPromptTemplate:
    with open(json_path, "r", encoding="utf-8") as f:
        prompt_data = json.load(f)
    template = prompt_data[prompt_name]["template"]
    return ChatPromptTemplate.from_template(template)
        
# 프롬프트 전체 로딩 함수 - YAML
def load_prompts_from_yaml(yaml_path: str) -> Dict[str, ChatPromptTemplate]:
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
        # 아래와 동일한 list-comprehension 포멧
        return {
            name: ChatPromptTemplate.from_template(p["template"])
            for name, p in data.items()
        }

# 프롬프트 전체 로딩 함수 -JSON
def load_prompts_from_json(json_path: str) -> Dict[str, ChatPromptTemplate]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
        result = {}
        for name, p in data.items():
            template = p["template"]
            result[name] = ChatPromptTemplate.from_template(template)

        return result

# 초기 로딩 함수
def initialize_vector_db():
    global store
    if os.path.exists(VECTOR_DB) and os.listdir(VECTOR_DB):
        store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=OpenAIEmbeddings(),
            persist_directory=VECTOR_DB
        )
        
    # DATA 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def initialize_components():
    global llm, output_parser, prompts
    
    # LLM 준비 (gpt-3.5-turbo 기반)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # 출력 파서
    output_parser = StrOutputParser()

    # 프롬프트 템플릿 정의
    prompts = load_prompts_from_yaml(PROMPT_FILE)
    # prompts = load_prompts_from_json(PROMPT_FILE)
    # prompts = load_prompt_from_json(PROMPT_FILE, "scored_prompt")

def create_vector_db(file_path):
    global store
    
    # 1. PDF 문서 로딩
    loader = PyPDFLoader(file_path) # 기본 metadata["source"] 및 metadata["page"] 가 추가됨
    documents = loader.load()
    
    # metadata["source"]를 basename(파일명)으로 덮어쓰기
    for doc in documents:
        doc.metadata["source"] = os.path.basename(file_path)

    # 2. 문서 분할
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    # 3. 임베딩 모델
    embeddings = OpenAIEmbeddings()

    # 4. 저장 폴더 없으면 생성
    if not os.path.exists(VECTOR_DB):
        os.makedirs(VECTOR_DB)

    # 5. 기존 DB가 있으면 불러와서 추가
    if os.path.isdir(VECTOR_DB) and os.listdir(VECTOR_DB):
        store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=VECTOR_DB
        )
        
        store.add_documents(texts) # 내용 추가
    else: # 없으면 새로 생성
        store = Chroma.from_documents(
            texts,
            embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=VECTOR_DB
        )

    return store

def preview_file_entries(file_name: str):
    """특정 source 메타데이터를 가진 벡터 문서들을 미리 조회하고 출력"""
    global store
    if store is None:
        print("벡터 스토어가 초기화되지 않았습니다.")
        return

    # 내부 컬렉션에서 조건에 맞는 벡터 가져오기
    result = store._collection.get(where={"source": file_name})

    ids = result.get("ids", [])
    documents = result.get("documents", [])
    metadatas = result.get("metadatas", [])

    print(f"파일명 '{file_name}'에 해당하는 벡터 {len(documents)}개가 존재합니다.")
    for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
        print(f"\n문서 {i}")
        print(f"내용: {doc[:50]}...")  # 앞 50자만 표시
        print(f"메타데이터: {meta}")
        
def delete_file(file_name: str):
    """지정한 파일명(source)과 매칭되는 벡터를 삭제하고, 실제 PDF/Text 파일도 지움."""
    global store
    
    # 1. 컬렉션 내에서 metadata.source == file_name 인 벡터 삭제
    # 내부 collection 객체를 직접 삭제
    # preview_file_entries(file_name)
    store._collection.delete(where={"source": file_name})
    
    # persist 옵션 사용중이면 persist() 호출
    if hasattr(store, "persist"):
        store.persist()
    
    # 2. DATA 디렉토리의 원본 파일 삭제
    path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(path):
        os.remove(path)

def list_files():
    """DATA_DIR에 남아있는 파일 목록 리턴"""
    files = [f for f in os.listdir(DATA_DIR)
            if os.path.isfile(os.path.join(DATA_DIR, f))]
    return files

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
    # chain = prompt | llm | output_parser # 사전에 하나만 로딩한 경우
    chain = prompts["scored_prompt"] | llm | output_parser # 여러개 프롬프트 중 원하는것 선택

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
