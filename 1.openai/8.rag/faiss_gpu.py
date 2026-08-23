# RAG with FAISS - 부록: GPU 가속 (선택 사항, Linux 전용)
# pip install faiss-gpu   (윈도우 미지원 — Linux에서만 설치 가능)
#
# 1~5단계는 모두 CPU(faiss-cpu)로 동작하며, 문서 수백~수천 개 수준에서는 충분하다.
# 수백만 개 이상의 벡터를 검색할 때 GPU 인덱스로 가속할 수 있다.
# (이 파일은 단계별 빌드업에 포함되지 않는 참고용 예제다.)

import faiss
import numpy as np

# [관전 포인트] CPU 인덱스를 만든 뒤 GPU로 옮긴다
cpu_index = faiss.IndexFlatL2(768)
gpu_resources = faiss.StandardGpuResources()              # GPU 리소스 할당
gpu_index = faiss.index_cpu_to_gpu(gpu_resources, 0, cpu_index)  # 0번 GPU로 이동

# 예제 데이터 (무작위 벡터 1000개) — 실제로는 문서 임베딩이 들어간다
data = np.random.rand(1000, 768).astype("float32")
gpu_index.add(data)

# GPU에서 검색 — 가장 가까운 5개
query = np.random.rand(1, 768).astype("float32")
distances, indices = gpu_index.search(query, k=5)

print("검색된 인덱스:", indices)
print("거리 값:", distances)
