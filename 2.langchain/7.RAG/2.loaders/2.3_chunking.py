"""
청킹(Chunking) — 긴 문서를 임베딩 가능한 작은 조각으로 나누기.
이 예제: 동일 텍스트에 세 가지 splitter 를 적용해 결과를 비교합니다.

왜 청킹?
  - 임베딩 모델은 입력 길이 제한이 있음
  - 너무 큰 청크는 검색 정확도 ↓ (한 청크에 잡다한 주제 섞임)
  - 너무 작은 청크는 맥락 손실
  - 보통 200~1000 토큰 + overlap(50~200) 이 시작점
"""

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

documents = TextLoader("../DATA/nvme.txt", encoding="utf-8").load()
original = documents[0].page_content
print(f"원본 글자수: {len(original)}\n")


# 1) CharacterTextSplitter — 단순히 정해진 separator 로 나누기
char_splitter = CharacterTextSplitter(
    separator="\n\n",     # 빈 줄 기준
    chunk_size=500,
    chunk_overlap=100,
)
chunks_char = char_splitter.split_documents(documents)
print(f"[CharacterTextSplitter] {len(chunks_char)} 청크")
print(f"  첫 청크 글자수: {len(chunks_char[0].page_content)}\n")


# 2) RecursiveCharacterTextSplitter — 여러 separator 를 순서대로 시도
# (\n\n → \n → 공백 → 글자 순). 가장 권장되는 일반용 splitter.
recur_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)
chunks_recur = recur_splitter.split_documents(documents)
print(f"[RecursiveCharacterTextSplitter] {len(chunks_recur)} 청크")
print(f"  첫 청크 글자수: {len(chunks_recur[0].page_content)}\n")


# 3) Token 기반 — tiktoken 으로 실제 토큰 수 기준 (OpenAI 모델 호환)
#   ※ pip install tiktoken
token_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=200,        # 토큰 단위!
    chunk_overlap=50,
)
chunks_token = token_splitter.split_documents(documents)
print(f"[tiktoken 기반] {len(chunks_token)} 청크")
print(f"  첫 청크 글자수: {len(chunks_token[0].page_content)}")

# 권장 선택:
#   - 일반 텍스트:       RecursiveCharacterTextSplitter
#   - OpenAI 비용 관리:  from_tiktoken_encoder (실제 청구 토큰과 일치)
#   - 단순한 데모/구조:  CharacterTextSplitter
