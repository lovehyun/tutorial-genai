# (2단계-D) 어휘 축소 — 도메인 코퍼스로 '작은 vocab' 토크나이저 새로 학습
# pip install transformers torch tokenizers
#
# 모델 크기의 큰 부분은 '임베딩 = 어휘 수 × 차원' 이다. 어휘를 줄이면 임베딩도 작아진다.
# 흔한 오해: dict 를 새로 만들어 끼우면 된다? → 아니다. 토크나이저는 학습된 병합규칙이라
#   '새로 학습' 해야 진짜로 줄어든다. fast 토크나이저의 train_new_from_iterator 를 쓴다.
#   이 예제: 보안 도메인 문장으로 작은 어휘 토크나이저를 학습해 vocab 수 감소를 확인한다.

from transformers import AutoTokenizer

# 원본 (fast 토크나이저여야 train_new_from_iterator 가능)
old_tok = AutoTokenizer.from_pretrained("bert-base-uncased")

# 도메인 코퍼스 (보안 관련 문장들 — 실제로는 수천~수만 문장)
corpus = [
    "Firewall rules block malicious traffic.",
    "Encryption protects sensitive data at rest and in transit.",
    "A hacker exploited the unpatched server vulnerability.",
    "Malware was detected and quarantined by the antivirus.",
    "Cybersecurity teams monitor intrusion detection alerts.",
    "Multi-factor authentication reduces account takeover risk.",
    "The phishing email tricked users into leaking credentials.",
    "Patch management closes known security holes quickly.",
]

# [관전 포인트] 코퍼스로부터 '작은 어휘' 토크나이저를 새로 학습
new_tok = old_tok.train_new_from_iterator(corpus, vocab_size=500)

print(f"원본 어휘 수 : {old_tok.vocab_size:,}")
print(f"축소 어휘 수 : {new_tok.vocab_size:,}  (도메인 코퍼스 기반 재학습)\n")

# 같은 문장을 두 토크나이저로 쪼개 비교
sample = "Encryption protects data."
print(f"문장: {sample}")
print(f"  원본: {old_tok.tokenize(sample)}")
print(f"  축소: {new_tok.tokenize(sample)}")

new_tok.save_pretrained("./security_tokenizer")
print("\n✅ 축소 토크나이저 저장 → ./security_tokenizer")
print("   (모델과 함께 쓰려면 model.resize_token_embeddings(len(new_tok)) 로 임베딩도 맞춰야 함)")
print("   다음(2.5): 큰 모델의 '지식' 을 작은 모델로 옮기는 지식 증류")
