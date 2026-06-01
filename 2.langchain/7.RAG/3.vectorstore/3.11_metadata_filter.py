"""
메타데이터 필터링 — 삽입 시 풍부한 메타데이터를 부여하고, 검색을 그걸로 좁히기.
이 예제: 문서마다 category/year/tier 를 붙여 Chroma 에 넣고, where 연산자로 필터 검색.

핵심:
  - Chroma 메타데이터 값은 str / int / float / bool 만 가능 (list/dict 불가)
  - similarity_search(query, filter={...}) 의 where 연산자:
      {"category": "nvme"}                  동등 ($eq 축약)
      {"year": {"$gte": 2020}}              숫자 비교 ($gt/$gte/$lt/$lte/$ne)
      {"category": {"$in": ["nvme","sata"]}}  목록 포함 ($nin = 제외)
      {"$and": [조건1, 조건2]}              여러 조건 AND ( $or 도 동일 형식 )
  → "의미 유사도(벡터) + 정형 조건(메타데이터)" 를 함께 거는 게 실무 RAG 의 기본기.
"""

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma

load_dotenv()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 삽입할 문서 — page_content(벡터화 대상) + 풍부한 metadata(필터 대상)
docs = [
    Document(page_content="NVMe SSD 는 PCIe 로 약 7GB/s 의 시퀀셜 속도를 낸다.",
             metadata={"category": "nvme", "year": 2022, "tier": "high"}),
    Document(page_content="SATA SSD 는 약 0.5GB/s 로 NVMe 보다 느리지만 호환성이 좋다.",
             metadata={"category": "sata", "year": 2018, "tier": "mid"}),
    Document(page_content="HDD 는 회전 디스크 기반이라 IO 가 느린 편이다.",
             metadata={"category": "hdd", "year": 2015, "tier": "low"}),
    Document(page_content="최신 PCIe 5.0 NVMe 는 약 14GB/s 까지 도달한다.",
             metadata={"category": "nvme", "year": 2024, "tier": "high"}),
]

# from_documents 가 page_content 를 임베딩하고 metadata 를 함께 저장
store = Chroma.from_documents(docs, embeddings, collection_name="meta_filter_demo")

query = "저장장치 속도"


def show(title: str, where: dict | None = None):
    print("\n" + "=" * 56)
    print(title)
    print("=" * 56)
    for d in store.similarity_search(query, k=4, filter=where):
        m = d.metadata
        print(f"  [{m['category']:4s} {m['year']} {m['tier']:4s}] {d.page_content[:38]}...")


# 1) 필터 없음 — 전체에서 top-k (메타데이터 무관)
show("(1) 필터 없음 — 전체 후보")

# 2) 동등 — category 가 nvme 인 것만
show("(2) category == 'nvme'", {"category": "nvme"})

# 3) 숫자 비교 — 2020년 이후 문서만
show("(3) year >= 2020", {"year": {"$gte": 2020}})

# 4) 목록 포함 — nvme / sata 계열만 (hdd 제외)
show("(4) category in [nvme, sata]", {"category": {"$in": ["nvme", "sata"]}})

# 5) 복합 AND — nvme 이면서 2023년 이후
show("(5) nvme AND year >= 2023", {"$and": [{"category": "nvme"}, {"year": {"$gte": 2023}}]})

store.delete_collection()

# 정리:
#   - 삽입: Document(metadata={...}) 로 부여 → Chroma 가 벡터와 함께 저장
#   - 검색: similarity_search(filter=where) 로 후보를 메타데이터로 먼저 제한
#   - 활용: 최신 문서만 / 특정 출처만 / 권한 있는 문서만 등 (RAG 정확도·보안의 핵심)


# ─────────────────────────────────────────────────────────────────────
# 실제 실행 결과  (py312_gpt)
#
#   (2) category == 'nvme'          → nvme 2개만
#   (3) year >= 2020                → 2022, 2024 (숫자 비교)
#   (4) category in [nvme, sata]    → nvme 2개 + sata 1개 (hdd 제외)
#   (5) nvme AND year >= 2023       → 2024 한 개만 (복합 조건)
#
#   ⇒ 같은 query("저장장치 속도") 인데 where 조건만으로 후보 집합이 정확히 좁혀짐.
# ─────────────────────────────────────────────────────────────────────
