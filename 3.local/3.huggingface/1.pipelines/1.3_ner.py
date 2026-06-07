# (파이프라인) 개체명 인식(NER) — 문장에서 인물/조직/장소 등을 추출
# pip install transformers torch
#
# NER 전용으로 '파인튜닝된' 모델을 써야 한다. (분류 헤드가 없는 base 모델은 의미 없는 결과)
#   여기선 영어 NER 표준 모델 dslim/bert-base-NER (CoNLL-03: PER/ORG/LOC/MISC).

from transformers import pipeline

# aggregation_strategy="simple" : 쪼개진 subword 를 하나의 개체로 합쳐서 보여줌
#   (예: 'El', '##on' → 'Elon')
ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

text = "Elon Musk is the CEO of Tesla, based in Austin."

print(f"문장: {text}\n")
for ent in ner(text):
    print(f"  {ent['word']:12} → {ent['entity_group']:4} (신뢰도 {ent['score']:.3f})")

# entity_group: PER(사람) / ORG(조직) / LOC(장소) / MISC(기타)
