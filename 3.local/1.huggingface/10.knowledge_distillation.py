from transformers import DistilBertForSequenceClassification, AutoModelForSequenceClassification

# 큰 모델 (BERT) → 작은 모델 (DistilBERT)로 학습
teacher_model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")
student_model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased")

# student_model이 teacher_model을 학습하도록 설정 (Knowledge Distillation)
# (이 부분은 학습 코드가 필요함. 기본적으로 teacher_model의 출력을 student_model이 따라가도록 함)
