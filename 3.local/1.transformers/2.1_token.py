import tiktoken

# GPT-4 기준 토크나이저 로딩
enc = tiktoken.encoding_for_model("gpt-4")

# 확인할 단어들
words = ["redone", "redo", "re-done", "walking", "walker", "walked"]

for w in words:
    tokens = enc.encode(w)
    decoded = [enc.decode([t]) for t in tokens]
    print(f"{w:8} → 토큰 ID: {tokens} → 분리된 토큰: {decoded}")
