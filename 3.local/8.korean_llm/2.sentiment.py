"""
한국어 감성 분석 — LLM 프롬프트 기반 감성 판별
- 설치: ollama pull qwen3:4b
"""
import requests
import json

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:4b"


def analyze_sentiment(text, model=MODEL):
    """한국어 텍스트의 감성을 분석하여 JSON으로 반환"""
    prompt = f"""다음 한국어 텍스트의 감성을 분석해주세요.

반드시 아래 JSON 형식으로만 답변하세요. 다른 텍스트는 출력하지 마세요:
{{"sentiment": "긍정" 또는 "부정" 또는 "중립", "confidence": 0.0~1.0, "keywords": ["핵심 감성 키워드"]}}

텍스트: {text}"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        },
    )
    return response.json()["response"]


def analyze_batch(texts, model=MODEL):
    """여러 텍스트를 한 번에 분석"""
    results = []
    for text in texts:
        result = analyze_sentiment(text, model)
        results.append({"text": text, "analysis": result})
    return results


def main():
    print("=" * 50)
    print("  한국어 감성 분석")
    print("=" * 50)

    # ── 쇼핑 리뷰 감성 분석 ──
    print("\n[ 쇼핑 리뷰 ]")
    print("-" * 40)

    reviews = [
        "이 제품 정말 좋아요! 배송도 빠르고 품질도 훌륭합니다.",
        "최악이에요. 돈 아까워요. 다시는 안 삽니다.",
        "가격 대비 그냥 그래요. 보통이에요.",
        "포장이 좀 아쉽지만 제품 자체는 괜찮네요.",
        "사진이랑 너무 달라서 실망했어요. 환불 요청합니다.",
    ]

    for review in reviews:
        print(f"\n리뷰: {review}")
        try:
            result = analyze_sentiment(review)
            print(f"분석: {result}")
        except Exception as e:
            print(f"오류: {e}")

    # ── 음식점 리뷰 감성 분석 ──
    print("\n\n[ 음식점 리뷰 ]")
    print("-" * 40)

    restaurant_reviews = [
        "분위기 좋고 음식도 맛있어요. 직원분들도 친절합니다.",
        "웨이팅 1시간인데 음식은 평범... 가성비 별로",
        "여기 떡볶이 진짜 맛있어요!! 매운맛 추천합니다 ㅋㅋ",
    ]

    for review in restaurant_reviews:
        print(f"\n리뷰: {review}")
        try:
            result = analyze_sentiment(review)
            print(f"분석: {result}")
        except Exception as e:
            print(f"오류: {e}")

    # ── 학습 포인트 ──
    print("\n" + "=" * 50)
    print("  [ 학습 포인트 ]")
    print("=" * 50)
    print("""
1. 프롬프트 기반 감성 분석:
   - 학습 데이터 없이 프롬프트만으로 감성 분류 가능
   - JSON 형식을 지시하여 구조화된 출력 획득

2. Temperature 설정:
   - 감성 분석처럼 정확도가 중요한 태스크는 temperature=0.1
   - 창의적 생성이 필요한 태스크는 temperature=0.7~0.9

3. BERT 파인튜닝 방식과의 차이:
   - BERT: 학습 데이터 필요, 특정 태스크에 높은 정확도
   - LLM 프롬프트: 데이터 불필요, 유연하지만 출력 형식 불안정할 수 있음

4. 실무 활용:
   - 소량 리뷰 분석: LLM 프롬프트 방식이 빠름
   - 대량 리뷰 분석: BERT 파인튜닝이 효율적 (속도+일관성)
""")


if __name__ == "__main__":
    main()
