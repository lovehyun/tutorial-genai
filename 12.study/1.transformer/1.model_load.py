# pip install -U sentence-transformers <-- huggingface 등 추가 라이브러리 자동 설치됨

from sentence_transformers import SentenceTransformer

# 모델 로드
model = SentenceTransformer('all-MiniLM-L6-v2')
# Model Local Path: C:\Users\Username\.cache\huggingface\hub\models--sentence-transform--*

# 사용 가능한 속성 출력
# print("Available attributes in model:")
# for attr in dir(model):
#     print(attr)
    
# 테스트: 문장 임베딩 생성
sentences = ["안녕하세요, 오늘 기분이 어떠세요?", "This is a test sentence."]
embeddings = model.encode(sentences)

print("임베딩 생성 완료:", embeddings)

