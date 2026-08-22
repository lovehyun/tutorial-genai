"""
한국어 텍스트 전처리 파이프라인
- 설치: pip install konlpy
"""
import re
from konlpy.tag import Okt


okt = Okt()


def remove_special_chars(text):
    """특수문자 제거 (한글, 영문, 숫자, 공백만 유지)"""
    return re.sub(r'[^가-힣a-zA-Z0-9\s]', '', text)


def remove_stopwords(tokens, stopwords=None):
    """불용어 제거"""
    if stopwords is None:
        stopwords = {
            "의", "가", "이", "은", "는", "을", "를", "에", "에서",
            "와", "과", "도", "로", "으로", "부터", "까지", "에게",
            "한", "하다", "있다", "되다", "것", "수", "등", "및",
            "그", "저", "이것", "그것", "저것", "여기", "거기", "저기",
        }
    return [t for t in tokens if t not in stopwords]


def extract_keywords(text, top_n=10):
    """명사 기반 키워드 추출"""
    nouns = okt.nouns(text)
    # 1글자 명사 제외
    nouns = [n for n in nouns if len(n) > 1]
    # 빈도 계산
    freq = {}
    for noun in nouns:
        freq[noun] = freq.get(noun, 0) + 1
    # 빈도순 정렬
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return sorted_freq[:top_n]


def preprocess_pipeline(text):
    """전체 전처리 파이프라인"""
    steps = {}

    # 1. 원본
    steps["원본"] = text

    # 2. 소문자 변환 (영문)
    text = text.lower()
    steps["소문자 변환"] = text

    # 3. 정규화 (Okt)
    text = okt.normalize(text)
    steps["정규화"] = text

    # 4. 특수문자 제거
    text = remove_special_chars(text)
    steps["특수문자 제거"] = text

    # 5. 형태소 분석
    morphs = okt.morphs(text)
    steps["형태소 분석"] = morphs

    # 6. 불용어 제거
    filtered = remove_stopwords(morphs)
    steps["불용어 제거"] = filtered

    return steps


def main():
    print("=" * 60)
    print("  한국어 텍스트 전처리 파이프라인")
    print("=" * 60)

    # ── 전처리 파이프라인 시연 ──
    print("\n[ 전처리 파이프라인 ]")
    print("-" * 50)

    test_texts = [
        "아ㅋㅋ 이거 진짜 맛있다!!! 강추합니다~~ #맛집 #서울",
        "삼성전자(005930)의 주가가 2024년 1월 3% 급등!! 외국인 매수세 유입",
        "AI 기술이 빠르게 발전하고 있습니다... 특히 NLP 분야에서요!!!",
    ]

    for text in test_texts:
        steps = preprocess_pipeline(text)
        print(f"\n  원본: {steps['원본']}")
        for step_name, result in steps.items():
            if step_name != "원본":
                print(f"  {step_name}: {result}")

    # ── 키워드 추출 ──
    print("\n\n[ 키워드 추출 ]")
    print("-" * 50)

    article = """인공지능 기술이 빠르게 발전하면서 다양한 산업에 변화를 가져오고 있다.
특히 자연어 처리 분야에서는 대규모 언어모델이 혁신적인 성과를 보여주고 있으며,
이미지 생성, 코드 작성, 번역 등 다양한 태스크에서 인간 수준의 능력을 달성했다.
한국에서도 LG의 EXAONE, 카카오의 Kanana, 네이버의 HyperCLOVA 등
한국어 특화 인공지능 모델 개발이 활발하게 진행되고 있다.
정부는 소버린 AI 프로젝트를 통해 한국어 인공지능 기술 경쟁력을 확보할 계획이다."""

    print(f"\n  텍스트 ({len(article)}자):")
    print(f"  {article.strip()[:80]}...")

    keywords = extract_keywords(article)
    print(f"\n  키워드 TOP {len(keywords)}:")
    for word, count in keywords:
        bar = "█" * count
        print(f"    {word:<10} {count}회  {bar}")

    # ── 전처리 전후 비교 ──
    print("\n\n[ 전처리 전후 비교: 감성 분석 입력 ]")
    print("-" * 50)

    reviews = [
        "이 제품 진짜 최고입니다ㅋㅋㅋ 강력 추천해요!!!★★★★★",
        "배송 느리고... 품질도 별로에요ㅠㅠ 환불하고 싶다...",
    ]

    for review in reviews:
        steps = preprocess_pipeline(review)
        print(f"\n  원본:   {review}")
        print(f"  전처리: {' '.join(steps['불용어 제거'])}")

    # ── 학습 포인트 ──
    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. 전처리 파이프라인 순서:
   소문자 변환 → 정규화 → 특수문자 제거 → 형태소 분석 → 불용어 제거
   (순서가 결과에 영향 — 정규화는 특수문자 제거 전에!)

2. 한국어 전처리 핵심:
   - 정규화: 'ㅋㅋㅋ' → 'ㅋㅋ', 구어체 표준화
   - 형태소 분석: 어절을 의미 단위로 분리
   - 불용어: 조사/접속사 등 분석에 불필요한 토큰 제거

3. 키워드 추출:
   - 명사만 추출 → 빈도 계산 → 상위 N개 선택
   - 1글자 명사 제외 (의미가 약한 경우 많음)
   - TF-IDF 적용하면 문서 간 특성 키워드 추출 가능

4. 실무 활용:
   - 검색 엔진: 형태소 분석 후 인덱싱
   - 감성 분석: 전처리 후 모델 입력
   - 토픽 모델링: 키워드 기반 주제 분류
   - 챗봇: 사용자 입력 정규화 후 의도 파악
""")


if __name__ == "__main__":
    main()
