"""
한국어 형태소 분석 — KoNLPy 형태소 분석기 비교
- 설치: pip install konlpy
- Java 런타임 필요: sudo apt-get install default-jdk
"""
from konlpy.tag import Okt, Kkma, Komoran


def compare_analyzers():
    """3가지 형태소 분석기 비교"""
    print("=" * 60)
    print("  한국어 형태소 분석기 비교")
    print("=" * 60)

    okt = Okt()
    kkma = Kkma()
    komoran = Komoran()

    test_sentences = [
        "인공지능이 세상을 변화시키고 있습니다.",
        "오늘 강남역에서 친구를 만나서 맛있는 점심을 먹었다.",
        "삼성전자 주가가 오늘 3% 이상 급등했다.",
    ]

    for text in test_sentences:
        print(f"\n  입력: {text}")
        print("  " + "-" * 55)

        print(f"  {'분석기':<12} 결과")
        print(f"  Okt        {okt.pos(text)}")
        print(f"  Kkma       {kkma.pos(text)}")
        print(f"  Komoran    {komoran.pos(text)}")


def pos_tagging_detail():
    """품사 태깅 상세 분석"""
    print("\n" + "=" * 60)
    print("  품사 태깅 상세")
    print("=" * 60)

    okt = Okt()
    text = "나는 오늘 아주 맛있는 한국 음식을 먹었습니다."

    print(f"\n  입력: {text}")
    print(f"\n  형태소 분석 (Okt):")

    pos_result = okt.pos(text)
    pos_labels = {
        "Noun": "명사", "Verb": "동사", "Adjective": "형용사",
        "Adverb": "부사", "Josa": "조사", "Eomi": "어미",
        "Punctuation": "구두점", "Determiner": "관형사",
        "Conjunction": "접속사", "Suffix": "접미사",
    }

    for morph, pos in pos_result:
        ko_pos = pos_labels.get(pos, pos)
        print(f"    {morph:<10} {pos:<15} ({ko_pos})")


def extract_by_pos():
    """품사별 추출"""
    print("\n" + "=" * 60)
    print("  품사별 단어 추출")
    print("=" * 60)

    okt = Okt()
    text = """인공지능 기술이 빠르게 발전하면서 다양한 산업에 변화를 가져오고 있다.
특히 자연어 처리 분야에서는 대규모 언어모델이 혁신적인 성과를 보여주고 있으며,
이미지 생성, 코드 작성, 번역 등 다양한 태스크에서 인간 수준의 능력을 달성했다."""

    print(f"\n  입력 텍스트:\n  {text.strip()}")

    # 명사 추출
    nouns = okt.nouns(text)
    print(f"\n  명사 추출 ({len(nouns)}개):")
    print(f"  {nouns}")

    # 품사별 분류
    pos_result = okt.pos(text)
    by_pos = {}
    for morph, pos in pos_result:
        if pos not in by_pos:
            by_pos[pos] = []
        if morph not in by_pos[pos]:
            by_pos[pos].append(morph)

    print(f"\n  품사별 분류:")
    for pos, words in sorted(by_pos.items()):
        print(f"    {pos:<15} ({len(words)}개): {words[:8]}{'...' if len(words) > 8 else ''}")


def normalize_text():
    """한국어 정규화"""
    print("\n" + "=" * 60)
    print("  한국어 텍스트 정규화 (Okt)")
    print("=" * 60)

    okt = Okt()

    test_texts = [
        "아ㅋㅋㅋ 진짜 웃기다ㅋㅋ",
        "이거 레알 맛있어욬ㅋㅋㅋㅋ",
        "오늘 너무너무너무 좋은 날!!!",
    ]

    for text in test_texts:
        normalized = okt.normalize(text)
        print(f"\n  원문: {text}")
        print(f"  정규화: {normalized}")


def print_learning_points():
    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. 형태소 분석기 비교:
   - Okt (Open Korean Text): 속도 빠름, 정규화 기능, SNS 텍스트에 강함
   - Kkma (꼬꼬마): 가장 정확, 느림, 학술 텍스트에 적합
   - Komoran: 속도/정확도 균형, 사전 추가 용이

2. 한국어 품사 체계:
   - 체언: 명사(NNG), 대명사(NP), 수사(NR)
   - 용언: 동사(VV), 형용사(VA)
   - 관계언: 조사(JKS, JKO, JX...)
   - 어미: 종결어미(EF), 연결어미(EC)

3. 실무 활용:
   - 키워드 추출: 명사만 추출하여 핵심어 파악
   - 감성 분석 전처리: 형용사/부사 추출
   - 검색 엔진: 형태소 단위 인덱싱
   - 텍스트 정규화: SNS/댓글 전처리

4. 서브워드 토크나이저와의 관계:
   - 형태소 분석: 언어학적 규칙 기반 (정확하지만 느림)
   - 서브워드 (BPE/SentencePiece): 통계 기반 (빠르지만 의미 무시)
   - 최신 LLM은 서브워드 방식 사용, 형태소 분석은 전처리/분석용
""")


if __name__ == "__main__":
    compare_analyzers()
    pos_tagging_detail()
    extract_by_pos()
    normalize_text()
    print_learning_points()
