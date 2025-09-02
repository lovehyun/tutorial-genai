import tiktoken

# GPT-4/3.5에서 쓰는 토크나이저 불러오기
enc = tiktoken.get_encoding("cl100k_base")

# 사전 크기 확인
print("사전 크기:", enc.n_vocab)

# 앞부분 토큰 20개만 보기
for i in range(20):
    print(i, enc.decode([i]))
