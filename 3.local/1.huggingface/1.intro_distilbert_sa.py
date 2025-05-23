# pip install huggingface_hub
# huggingface-cli login
# export HUGGINGFACE_HUB_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxx"
# set HUGGINGFACE_HUB_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxx"

# pip install transformers
from transformers import pipeline

# 감성 분석 파이프라인 생성
# sentiment_analyzer = pipeline("sentiment-analysis")

# 모델을 명확하게 지정
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
# sentiment_analyzer = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
# 모델의 태스크(task)를 지정 가능: 모델에 따라 지원되는 값들이 다름. "sentiment-analysis" 외 "text-classification" 도 가능하지만 어차피 SST-2 (감정분석 데이터) 라서 동일함.

# 강제로 모델 다시 다운로드
# sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english", revision="main", force_download=True)

# 문장 감성 분석 실행
result = sentiment_analyzer("I love using Hugging Face!")[0]

# 결과 출력
print(result)  # {'label': 'POSITIVE', 'score': 0.9998}
