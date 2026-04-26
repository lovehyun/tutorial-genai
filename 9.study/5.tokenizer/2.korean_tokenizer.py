"""
한국어 토크나이저 심화 — 한국어 특화 모델의 토크나이저 분석
- 설치: pip install transformers sentencepiece protobuf
"""
from transformers import AutoTokenizer


def compare_korean_tokenizers():
    """한국어 특화 vs 범용 토크나이저 비교"""
    print("=" * 60)
    print("  한국어 특화 토크나이저 비교")
    print("=" * 60)

    # 한국어 특화 모델과 범용 모델 비교
    tokenizer_list = [
        ("google-bert/bert-base-multilingual-cased", "BERT 다국어"),
        ("openai-community/gpt2", "GPT-2 (영어 중심)"),
        ("Qwen/Qwen2.5-1.5B", "Qwen2.5 (다국어)"),
    ]

    test_sentences = [
        "대한민국의 수도는 서울특별시입니다.",
        "자연어 처리는 인공지능의 한 분야입니다.",
        "삼성전자가 새로운 반도체를 개발했습니다.",
        "오늘 점심은 김치찌개를 먹었어요.",
    ]

    for text in test_sentences:
        print(f"\n  입력: {text}")
        print(f"  {'모델':<25} {'토큰 수':>8}  토큰")
        print("  " + "-" * 70)

        for model_name, label in tokenizer_list:
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                tokens = tokenizer.tokenize(text)
                print(f"  {label:<25} {len(tokens):>8}  {tokens[:10]}{'...' if len(tokens) > 10 else ''}")
            except Exception as e:
                print(f"  {label:<25}  오류: {e}")


def analyze_korean_morphemes():
    """한국어 교착어 특성과 토크나이징"""
    print("\n" + "=" * 60)
    print("  한국어 교착어 특성과 토크나이징")
    print("=" * 60)

    tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-multilingual-cased")

    # 같은 어간에 다른 조사/어미
    morpheme_groups = [
        ("조사 변화", ["학교가", "학교를", "학교에서", "학교에", "학교의", "학교로"]),
        ("어미 변화", ["먹다", "먹고", "먹으며", "먹었다", "먹을까", "먹자"]),
        ("존칭 변화", ["갑니다", "가요", "가", "가십니다", "가시나요"]),
    ]

    for group_name, words in morpheme_groups:
        print(f"\n  [{group_name}]")
        for word in words:
            tokens = tokenizer.tokenize(word)
            print(f"    {word:<10} → {tokens}")

    print("\n  → 한국어는 조사/어미에 따라 토큰이 크게 달라짐")
    print("  → 영어 'school'은 항상 1토큰, '학교'는 문맥에 따라 토큰 수 변동")


def vocab_size_comparison():
    """토크나이저별 어휘 크기 비교"""
    print("\n" + "=" * 60)
    print("  토크나이저 어휘(Vocab) 크기 비교")
    print("=" * 60)

    models = [
        ("google-bert/bert-base-multilingual-cased", "BERT 다국어"),
        ("google-bert/bert-base-uncased", "BERT 영어"),
        ("openai-community/gpt2", "GPT-2"),
        ("google-t5/t5-base", "T5"),
        ("Qwen/Qwen2.5-1.5B", "Qwen2.5"),
    ]

    print(f"\n  {'모델':<25} {'어휘 크기':>12}")
    print("  " + "-" * 40)

    for model_name, label in models:
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            vocab_size = tokenizer.vocab_size
            print(f"  {label:<25} {vocab_size:>12,}")
        except Exception as e:
            print(f"  {label:<25}  오류: {e}")

    print("\n  → 어휘 크기가 클수록 한 토큰에 더 많은 정보를 담을 수 있음")
    print("  → 다국어 모델은 여러 언어를 커버해야 하므로 어휘가 큼")


def token_cost_analysis():
    """토큰 수 기반 비용 분석"""
    print("\n" + "=" * 60)
    print("  토큰 수와 API 비용의 관계")
    print("=" * 60)

    # 같은 의미의 한/영 문장
    pairs = [
        (
            "Artificial intelligence technology is rapidly advancing.",
            "인공지능 기술이 빠르게 발전하고 있습니다.",
        ),
        (
            "The quarterly financial report shows significant growth.",
            "분기별 재무 보고서에서 상당한 성장이 나타났습니다.",
        ),
        (
            "Please review the attached document and provide feedback.",
            "첨부된 문서를 검토하고 피드백을 제공해 주세요.",
        ),
    ]

    tokenizer = AutoTokenizer.from_pretrained("openai-community/gpt2")

    total_en, total_ko = 0, 0
    print(f"\n  {'영어':>40} {'토큰':>5}  |  {'한국어':>40} {'토큰':>5}")
    print("  " + "-" * 100)

    for en, ko in pairs:
        en_tokens = len(tokenizer.tokenize(en))
        ko_tokens = len(tokenizer.tokenize(ko))
        total_en += en_tokens
        total_ko += ko_tokens
        print(f"  {en[:38]:>40} {en_tokens:>5}  |  {ko[:38]:>40} {ko_tokens:>5}")

    ratio = total_ko / total_en
    print(f"\n  합계: 영어 {total_en}토큰 vs 한국어 {total_ko}토큰 (한국어가 {ratio:.1f}배)")
    print(f"  → 같은 내용이라도 한국어는 API 비용이 ~{ratio:.0f}배 더 듦")
    print(f"  → 한국어 특화 토크나이저를 쓰면 이 격차를 줄일 수 있음")


def print_learning_points():
    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. 한국어 교착어 문제:
   - '학교가/학교를/학교에서' → 조사에 따라 토큰화 결과 달라짐
   - 영어 'school'은 문맥 무관하게 일정한 토큰
   - 한국어 특화 토크나이저가 형태소 경계를 더 잘 인식

2. 토큰 효율성 = 비용 효율성:
   - API 과금은 토큰 수 기반 (GPT-4, Claude 등)
   - 같은 내용이라도 한국어는 영어보다 2~4배 많은 토큰 소비
   - 한국어 특화 모델 사용 시 토큰 효율 개선

3. 어휘 크기의 의미:
   - 큰 어휘: 토큰 수 감소 → 효율적 but 모델 크기 증가
   - 작은 어휘: 토큰 수 증가 → 비효율적 but 모델 크기 감소
   - 적절한 균형점 찾기가 중요

4. 실무 팁:
   - 프롬프트 최적화 시 토큰 수를 항상 체크
   - 한국어 서비스라면 한국어 특화 모델 사용 고려
   - tokenizer.tokenize()로 미리 토큰 수 확인 가능
""")


if __name__ == "__main__":
    compare_korean_tokenizers()
    analyze_korean_morphemes()
    vocab_size_comparison()
    token_cost_analysis()
    print_learning_points()
