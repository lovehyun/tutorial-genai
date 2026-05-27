# LLM 4일차: RAG 모델을 통한 내 문서 학습

## 학습 목표
- 문서 로딩 → 청킹 → 임베딩 → 벡터DB(Chroma) 색인 → 검색/생성(**RAG**) 파이프라인을 완성합니다.
- 메타데이터 관리, 하이브리드 검색, 간단 리랭킹, 평가까지 살펴봅니다.

---

## 설치
```bash
pip install langchain langchain-openai chromadb tiktoken pypdf python-dotenv
```

## 프로젝트 구조
```
rag/
 ├─ ingest.py        # 문서 로딩/청킹/색인
 ├─ ask.py           # 질의 응답
 ├─ .env
 └─ data/            # 문서 보관
```

### .env
```
OPENAI_API_KEY=sk-...
```

---

## 인덱싱 파이프라인 (`ingest.py`)
```python
# ingest.py
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

load_dotenv()
DATA_DIR = Path("data")
DB_DIR = "chroma_db"
COLLECTION = "my-docs"

def load_documents():
    docs = []
    for p in DATA_DIR.glob("**/*"):
        if p.suffix.lower() == ".pdf":
            docs.extend(PyPDFLoader(str(p)).load())
        elif p.suffix.lower() in {".txt", ".md"}:
            docs.extend(TextLoader(str(p), encoding="utf-8").load())
    return docs

def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=150, separators=["\n\n","\n"," ",""]
    )
    return splitter.split_documents(docs)

def index(chunks):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vs = Chroma(
        collection_name=COLLECTION,
        persist_directory=DB_DIR,
        embedding_function=embeddings
    )
    vs.add_documents(chunks)
    vs.persist()
    print(f"Indexed {len(chunks)} chunks to {DB_DIR} ({COLLECTION})")

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    docs = load_documents()
    chunks = chunk_documents(docs)
    index(chunks)
```

---

## 질의 응답 체인 (`ask.py`)
```python
# ask.py
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

DB_DIR = "chroma_db"
COLLECTION = "my-docs"

load_dotenv()
emb = OpenAIEmbeddings(model="text-embedding-3-small")
vs = Chroma(collection_name=COLLECTION, persist_directory=DB_DIR, embedding_function=emb)
retriever = vs.as_retriever(search_kwargs={"k":4})

SYSTEM = (
"당신은 문서 기반 질의응답 비서입니다. "
"문서 근거가 없으면 지어내지 말고 '정보가 부족합니다.'라고 답하세요. "
"근거로 사용한 문서의 파일명과 페이지(가능하다면)를 끝에 나열하세요."
)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("human", "질문: {question}\n관련 컨텍스트: {context}")
])

def format_docs(docs):
    out = []
    for d in docs:
        meta = d.metadata or {}
        src = meta.get("source","unknown")
        page = meta.get("page","?")
        out.append(f"[{src} p.{page}]\n{d.page_content}")
    return "\n\n".join(out)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = (
    {"context": retriever | (lambda docs: format_docs(docs)), "question": lambda x: x["question"]}
    | prompt
    | llm
    | StrOutputParser()
)

if __name__ == "__main__":
    while True:
        q = input("질문> ").strip()
        if not q: break
        print(chain.invoke({"question": q}))
```

---

## 하이브리드 검색(옵션)
BM25 + 벡터 결합, 혹은 메타필터링(`where`)을 추가할 수 있습니다. Chroma의 `similarity_search_with_score`로 스코어 확인 후 리랭킹하는 간단 전략도 유용합니다.

```python
docs = vs.similarity_search_with_score("질문", k=8)
docs = sorted(docs, key=lambda x: x[1])[:4]  # 낮을수록 유사
```

---

## 간단 평가 아이디어
- **정확성**: 답이 문서 근거와 일치하는가?
- **근거 링크**: 출처/페이지를 잘 표시하는가?
- **거짓말 방지율**: 근거 없을 때 “정보가 부족”을 내는가?

> RAGAS 등 평가 프레임워크를 추후 접목해볼 수 있습니다.

---

## 실습 과제
1) PDF+TXT 복합 인덱싱 후, 질문 10개에 대한 답변 품질을 수작업 평가표로 점수화하세요.  
2) `chunk_size`, `chunk_overlap`을 바꿔 성능 비교.  
3) 메타데이터(파일명/페이지)를 출력에 확보하도록 `format_docs`를 개선하세요.
