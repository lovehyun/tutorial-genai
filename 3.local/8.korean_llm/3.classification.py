"""
한국어 텍스트 분류 — 뉴스 기사 카테고리 분류
- 설치: ollama pull qwen3:4b
"""
import requests
import json

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:4b"

CATEGORIES = ["정치", "경제", "스포츠", "기술", "연예", "사회"]


def classify_text(text, categories=CATEGORIES, model=MODEL):
    """한국어 텍스트를 주어진 카테고리 중 하나로 분류"""
    cats = ", ".join(categories)
    prompt = f"""다음 한국어 텍스트를 아래 카테고리 중 하나로 분류해주세요.

카테고리: [{cats}]

반드시 아래 JSON 형식으로만 답변하세요. 다른 텍스트는 출력하지 마세요:
{{"category": "선택한 카테고리", "confidence": 0.0~1.0, "reason": "분류 이유 한 줄"}}

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


def classify_with_custom_categories(text, categories, model=MODEL):
    """사용자 정의 카테고리로 분류"""
    return classify_text(text, categories, model)


def main():
    print("=" * 50)
    print("  한국어 텍스트 분류")
    print("=" * 50)

    # ── 뉴스 기사 분류 ──
    print("\n[ 뉴스 기사 카테고리 분류 ]")
    print("-" * 40)

    news_articles = [
        "코스피가 오늘 3% 이상 급등하며 2,800선을 돌파했다. 외국인 매수세가 유입되며 반도체 관련주가 강세를 보였다.",
        "손흥민이 프리미어리그에서 시즌 15번째 골을 기록하며 팀의 3-1 승리를 이끌었다.",
        "삼성전자가 3나노 GAA 공정 기반 차세대 AI 반도체를 공개했다. 전력 효율이 기존 대비 40% 개선됐다.",
        "여야가 국회 본회의에서 예산안 처리를 두고 격돌했다. 야당은 필리버스터를 예고했다.",
        "BTS 진이 솔로 앨범을 발매하며 빌보드 핫100 상위권에 진입했다.",
        "서울 강남역 일대 침수 피해가 발생해 긴급 복구 작업이 진행 중이다.",
    ]

    for article in news_articles:
        print(f"\n기사: {article[:50]}...")
        try:
            result = classify_text(article)
            print(f"분류: {result}")
        except Exception as e:
            print(f"오류: {e}")

    # ── 커스텀 카테고리 분류 ──
    print("\n\n[ 커스텀 카테고리 분류: 고객 문의 유형 ]")
    print("-" * 40)

    support_categories = ["배송 문의", "환불/교환", "제품 불량", "사용법 문의", "기타"]
    support_messages = [
        "주문한 지 5일이 지났는데 아직 배송이 안 왔어요.",
        "제품 박스가 찌그러져서 왔는데 교환 가능한가요?",
        "전원 버튼을 눌러도 켜지지 않아요. 불량인 것 같습니다.",
        "블루투스 연결 방법을 모르겠어요. 설명서에도 안 나와있어요.",
    ]

    for msg in support_messages:
        print(f"\n문의: {msg}")
        try:
            result = classify_with_custom_categories(msg, support_categories)
            print(f"분류: {result}")
        except Exception as e:
            print(f"오류: {e}")

    # ── 학습 포인트 ──
    print("\n" + "=" * 50)
    print("  [ 학습 포인트 ]")
    print("=" * 50)
    print("""
1. Zero-shot 분류:
   - 학습 데이터 없이 카테고리 목록만 주면 분류 가능
   - 카테고리를 자유롭게 변경할 수 있는 유연성

2. 커스텀 카테고리:
   - 뉴스 분류, 고객 문의 분류, 이메일 분류 등
   - 카테고리 리스트만 바꾸면 어떤 도메인이든 적용

3. BERT 분류와의 차이 (9.nlp/2.bert/ 참조):
   - BERT: 2,000~5,000개 학습 데이터로 파인튜닝 → 높은 정확도
   - LLM: 프롬프트만으로 즉시 분류 → 빠른 프로토타이핑
   - 실무: LLM으로 먼저 검증 → 확정되면 BERT로 최적화

4. JSON 구조화 출력:
   - 프롬프트에 정확한 JSON 형식을 명시
   - temperature=0.1로 출력 안정성 확보
""")


if __name__ == "__main__":
    main()
