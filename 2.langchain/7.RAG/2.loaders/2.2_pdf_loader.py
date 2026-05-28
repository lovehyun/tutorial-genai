"""
PyPDFLoader — PDF 파일을 페이지별 Document 로 불러오기.
이 예제: 작은 PDF 를 읽고, 페이지 단위로 Document 가 분리됨을 확인합니다.

  ※ pip install pypdf


─── 분할 단위 ─────────────────────────────────────────────

PyPDFLoader 는 **PDF 1 페이지 = Document 1개** 단위로 자동 분리합니다.
  (TextLoader 는 파일 통째로 Document 1개 — 2.1 참고)

  예) 10 페이지 PDF  →  길이 10 의 Document 리스트
       각 Document.metadata 에 source(파일 경로) + page(번호) 자동 부여

여전히 청킹은 하지 않습니다. 한 페이지가 길면 그 텍스트가 통째로 한 Document.
페이지 텍스트가 너무 길면 임베딩 토큰 한도를 넘을 수 있으므로
→ **2.3 splitter** 단계에서 다시 잘게 쪼갭니다.

전체 흐름 다이어그램은 2.1 docstring 참고.
"""

from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("../DATA/하계학술대회(CISC-S'24) CFP v2.pdf")
pages = loader.load()

print(f"PDF 페이지 수: {len(pages)}\n")

# 첫 번째 내용 있는 페이지 살펴보기
for p in pages:
    if p.page_content.strip():
        print(f"첫 내용 페이지 metadata: {p.metadata}")
        print(f"page_content (앞 200자):\n{p.page_content[:200]}...")
        break

# PyPDFLoader 는 페이지 하나당 Document 하나 생성.
# metadata 에 source(파일 경로) + page(페이지 번호) 가 자동 부여됨.
# 큰 PDF 는 페이지가 많아도 청크 크기는 따로 조절해야 함 (2.3 청킹).
