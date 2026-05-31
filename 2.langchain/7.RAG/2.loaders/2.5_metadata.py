"""
메타데이터 — Document.metadata 에 출처 정보를 부착해 추적 가능하게.
이 예제: 여러 파일을 청킹할 때 source / chunk_id 를 부여하고 통합합니다.

왜 메타데이터?
  - 답변에 "출처: nvme.txt 청크 #3" 같이 인용
  - 특정 파일/날짜로 필터링 검색 (advanced)
"""

import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

FILES = ["../DATA/nvme.txt", "../DATA/ssd.txt"]
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

all_chunks = []
for path in FILES:
    documents = TextLoader(path, encoding="utf-8").load()
    chunks = splitter.split_documents(documents)

    # 파일별로 source(파일명만) + chunk_id(파일 내부 1..N) 부여
    for i, chunk in enumerate(chunks, start=1):
        chunk.metadata["source"] = os.path.basename(path)
        chunk.metadata["chunk_id"] = i

    all_chunks.extend(chunks)
    print(f"{os.path.basename(path)}: {len(chunks)} 청크")

print(f"\n전체 청크: {len(all_chunks)}\n")

# 메타데이터 확인
print("=== 청크별 메타데이터 ===")
for c in all_chunks[:5]:
    print(f"  source={c.metadata['source']:10s} chunk_id={c.metadata['chunk_id']}  "
          f"({len(c.page_content)} 글자)")
print(f"  ... 외 {len(all_chunks) - 5} 개")

# 이렇게 메타데이터를 부여해두면, 검색 결과에서:
#   doc.metadata["source"], doc.metadata["chunk_id"]
# 로 출처를 정확히 인용할 수 있습니다 (4.rag_chain/4.2_with_citations 에서 활용).
