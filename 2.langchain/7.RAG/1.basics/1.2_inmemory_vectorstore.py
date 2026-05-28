"""
InMemoryVectorStore — 메모리 위의 가장 단순한 벡터 검색기.
이 예제: 문장 6개를 임베딩으로 저장하고, 질문 벡터와 가장 가까운 N개를 찾습니다.

벡터 스토어가 하는 일:
  1. 문서를 embed 해서 보관
  2. 질문이 들어오면 그 임베딩과 가장 가까운 N개 반환 (= 검색)
"""

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document

load_dotenv()

# 1) 작은 문서 집합 (Document 객체)
docs = [
    Document(page_content="NVMe 는 SSD 의 인터페이스 규격으로 PCIe 를 사용한다."),
    Document(page_content="SATA SSD 는 NVMe 보다 속도가 느리다."),
    Document(page_content="HDD 는 회전 디스크 기반이라 IO 가 느린 편이다."),
    Document(page_content="파이썬은 인기 있는 프로그래밍 언어다."),
    Document(page_content="자바스크립트는 브라우저에서 동작하는 언어다."),
    Document(page_content="Rust 는 메모리 안전성과 성능을 동시에 추구한다."),
]

# 2) 벡터 스토어에 임베딩하여 저장
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = InMemoryVectorStore.from_documents(docs, embedding=embeddings)

# 3) 검색 — 질문에 의미적으로 가까운 문서 top-k
query = "NVMe 와 SATA 의 차이?"
results = store.similarity_search(query, k=3)

print(f"질문: {query}\n")
print(f"가장 가까운 {len(results)} 개 문서:")
for i, doc in enumerate(results, 1):
    print(f"  {i}. {doc.page_content}")

# 같은 의미를 다른 단어로 물어도 잘 찾아냅니다 — 벡터는 단어가 아닌 "의미" 를 잡기 때문.
