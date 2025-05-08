from transformers import AutoTokenizer

# 원본 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# 보안 관련 단어만 남기고, 나머지 제거
security_vocab = ["firewall", "encryption", "malware", "hacker", "cybersecurity"]
new_vocab = {word: idx for idx, word in enumerate(security_vocab)}

# 새로운 토크나이저 저장
tokenizer.save_pretrained("./security_tokenizer")
print("✅ 불필요한 토큰 제거 완료!")
