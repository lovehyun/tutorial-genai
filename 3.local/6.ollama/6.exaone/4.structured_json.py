"""
(4) 구조화 출력(JSON) — 자유 텍스트에서 정보를 뽑아 JSON 으로 (ollama SDK)
ollama 의 format="json" 으로 '유효한 JSON' 출력을 강제한다.
앱/DB 연동의 핵심 — LLM 출력을 코드로 바로 쓸 수 있게.

준비: pip install ollama  +  ollama pull exaone3.5
"""
import ollama
import json

MODEL = "exaone3.5:latest"


def extract_json(text):
    """format='json' 으로 JSON 만 출력하도록 강제 → dict 로 파싱"""
    resp = ollama.chat(
        model=MODEL,
        format="json",                       # ← 유효한 JSON 출력 강제
        options={"temperature": 0.0},
        messages=[
            {"role": "system", "content":
             "너는 텍스트에서 정보를 추출해 JSON 으로만 답한다. "
             "키: name(이름), age(나이, 정수), city(도시), interests(관심사 배열)."},
            {"role": "user", "content": text},
        ],
    )
    return json.loads(resp["message"]["content"])


sentence = "안녕하세요, 저는 서울에 사는 32살 박수현입니다. 등산과 사진 찍기를 좋아해요."

data = extract_json(sentence)
print("입력 문장:", sentence)
print("\n추출된 JSON (dict):")
print(json.dumps(data, ensure_ascii=False, indent=2))

# 코드에서 바로 활용 가능
print(f"\n→ 이름={data.get('name')} / 나이={data.get('age')} / 관심사 수={len(data.get('interests', []))}")

# 학습 포인트:
#   - format="json" 이 핵심 — 모델이 설명문 없이 JSON 만 내도록 강제
#   - temperature=0 으로 안정적 추출, json.loads 로 바로 파싱해 앱에 연결
