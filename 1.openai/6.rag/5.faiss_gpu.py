# pip install faiss-gpu
# conda install -c pytorch faiss-gpu
# 윈도우용은 존재하지 않아, 리눅스에서만 가능함

import faiss
import numpy as np
import torch

# FAISS의 GPU 사용 활성화
gpu_index = faiss.IndexFlatL2(768)  # 예: 768차원 벡터
gpu_res = faiss.StandardGpuResources()  # GPU 리소스 할당
gpu_index = faiss.index_cpu_to_gpu(gpu_res, 0, gpu_index)  # CPU 인덱스를 GPU로 이동

# 예제 데이터 생성 및 추가
data = np.random.rand(1000, 768).astype("float32")  # 1000개 샘플
gpu_index.add(data)  # GPU 인덱스에 데이터 추가

# 검색 실행 (GPU 활용)
query = np.random.rand(1, 768).astype("float32")  # 검색할 1개 샘플
D, I = gpu_index.search(query, k=5)  # 가장 가까운 5개 검색

print("🔍 검색 결과 인덱스:", I)
print("🎯 거리 값:", D)
