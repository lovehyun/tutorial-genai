# pip install langchain-ollama langchain-chroma
#
# Ollama + LangChain 8: RAG (검색 증강 생성).
# OllamaEmbeddings 로 문서를 벡터화 → Chroma 에 저장 → 검색 → LCEL 로 답변.
# 먼저: ollama pull nomic-embed-text  (임베딩 모델)

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 지식 문서 (실전에선 파일/DB 에서 로드)
docs = [
    "Python은 강력하고 배우기 쉬운 프로그래밍 언어입니다.",
    "Chroma와 FAISS는 벡터 검색을 위한 라이브러리입니다.",
    "Ollama는 로컬 환경에서 LLM을 실행하는 오픈소스 도구입니다.",
]

# 1) 임베딩 + 벡터스토어 (메모리)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma.from_texts(docs, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# 2) LLM + 프롬프트
llm = ChatOllama(model="mistral", temperature=0)
prompt = ChatPromptTemplate.from_template(
    "다음 정보만 사용해 한국어로 답하라.\n\n정보:\n{context}\n\n질문: {question}"
)

def format_docs(docs):
    return "\n".join(d.page_content for d in docs)

# 3) LCEL RAG 체인: 질문 → (검색+원문) → 프롬프트 → 답변
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print(rag_chain.invoke("Ollama가 뭐야?"))
