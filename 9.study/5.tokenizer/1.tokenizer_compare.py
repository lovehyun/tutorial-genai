"""
토크나이저 알고리즘 비교 — WordPiece, BPE, SentencePiece
- 설치: pip install transformers sentencepiece protobuf
"""
from transformers import AutoTokenizer


def show_tokenization(tokenizer_name, text, label=""):
    """토크나이저의 결과를 상세히 출력"""
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    tokens = tokenizer.tokenize(text)
    token_ids = tokenizer.encode(text, add_special_tokens=False)

    print(f"\n  [{label}] {tokenizer_name}")
    print(f"  입력: {text}")
    print(f"  토큰 수: {len(tokens)}")
    print(f"  토큰: {tokens}")
    print(f"  토큰 ID: {token_ids}")

    # 토큰 → 텍스트 복원
    decoded = tokenizer.decode(token_ids)
    print(f"  복원: {decoded}")

    return tokens


def compare_tokenizers():
    """3가지 토크나이저 알고리즘 비교"""
    print("=" * 60)
    print("  토크나이저 알고리즘 비교")
    print("=" * 60)

    # 비교할 토크나이저
    tokenizers = [
        ("google-bert/bert-base-multilingual-cased", "WordPiece (BERT)"),
        ("openai-community/gpt2", "BPE (GPT-2)"),
        ("google-t5/t5-base", "SentencePiece (T5)"),
    ]

    # ── 영어 텍스트 비교 ──
    print("\n" + "=" * 60)
    print("  1. 영어 텍스트")
    print("=" * 60)

    en_text = "Artificial intelligence is transforming the world."
    for model_name, label in tokenizers:
        show_tokenization(model_name, en_text, label)

    # ── 한국어 텍스트 비교 ──
    print("\n" + "=" * 60)
    print("  2. 한국어 텍스트")
    print("=" * 60)

    ko_text = "인공지능이 세상을 변화시키고 있습니다."
    for model_name, label in tokenizers:
        show_tokenization(model_name, ko_text, label)

    # ── 한영 혼합 텍스트 비교 ──
    print("\n" + "=" * 60)
    print("  3. 한영 혼합 텍스트")
    print("=" * 60)

    mixed_text = "GPT-4는 OpenAI가 만든 대규모 언어모델입니다."
    for model_name, label in tokenizers:
        show_tokenization(model_name, mixed_text, label)


def compare_token_efficiency():
    """한국어 vs 영어 토큰 효율성 비교"""
    print("\n" + "=" * 60)
    print("  4. 토큰 효율성 비교")
    print("=" * 60)

    # 의미적으로 같은 문장
    texts = [
        ("영어", "Artificial intelligence is changing our daily lives significantly."),
        ("한국어", "인공지능이 우리의 일상생활을 크게 변화시키고 있습니다."),
    ]

    tokenizers = [
        ("google-bert/bert-base-multilingual-cased", "BERT (WordPiece)"),
        ("openai-community/gpt2", "GPT-2 (BPE)"),
        ("google-t5/t5-base", "T5 (SentencePiece)"),
    ]

    print(f"\n  {'모델':<25} {'영어 토큰 수':>12} {'한국어 토큰 수':>14} {'비율':>8}")
    print("  " + "-" * 60)

    for model_name, label in tokenizers:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        en_count = len(tokenizer.tokenize(texts[0][1]))
        ko_count = len(tokenizer.tokenize(texts[1][1]))
        ratio = ko_count / en_count

        print(f"  {label:<25} {en_count:>12} {ko_count:>14} {ratio:>7.1f}x")

    print("\n  → 한국어는 영어보다 토큰 수가 많음 = 같은 내용을 처리하는 데 더 많은 비용")
    print("  → 한국어 특화 토크나이저(EXAONE, Kanana 등)가 중요한 이유")


def show_special_tokens():
    """특수 토큰 이해"""
    print("\n" + "=" * 60)
    print("  5. 특수 토큰")
    print("=" * 60)

    text = "안녕하세요"

    # BERT: [CLS], [SEP] 사용
    bert_tok = AutoTokenizer.from_pretrained("google-bert/bert-base-multilingual-cased")
    bert_encoded = bert_tok.encode(text)
    bert_decoded = [bert_tok.decode([t]) for t in bert_encoded]

    print(f"\n  BERT 특수 토큰:")
    print(f"  입력: {text}")
    print(f"  인코딩: {bert_encoded}")
    print(f"  디코딩: {bert_decoded}")
    print(f"  [CLS]={bert_tok.cls_token_id}, [SEP]={bert_tok.sep_token_id}, [PAD]={bert_tok.pad_token_id}")

    # GPT-2: <|endoftext|> 사용
    gpt_tok = AutoTokenizer.from_pretrained("openai-community/gpt2")
    gpt_encoded = gpt_tok.encode(text)

    print(f"\n  GPT-2 특수 토큰:")
    print(f"  입력: {text}")
    print(f"  인코딩: {gpt_encoded}")
    print(f"  EOS={gpt_tok.eos_token} (ID: {gpt_tok.eos_token_id})")

    # T5: </s> 사용
    t5_tok = AutoTokenizer.from_pretrained("google-t5/t5-base")
    t5_encoded = t5_tok.encode(text)
    t5_decoded = [t5_tok.decode([t]) for t in t5_encoded]

    print(f"\n  T5 특수 토큰:")
    print(f"  입력: {text}")
    print(f"  인코딩: {t5_encoded}")
    print(f"  디코딩: {t5_decoded}")
    print(f"  EOS={t5_tok.eos_token} (ID: {t5_tok.eos_token_id})")


def print_learning_points():
    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. 서브워드 토크나이징:
   - 단어 단위가 아닌 서브워드 단위로 분할
   - 처음 보는 단어(OOV)도 서브워드 조합으로 처리 가능
   - 어휘 크기와 표현력의 균형

2. 알고리즘별 차이:
   - WordPiece (BERT): ##접두사로 서브워드 표시, 양방향 인코더 최적화
   - BPE (GPT-2): 바이트 단위 병합, 영어에 최적화됨
   - SentencePiece (T5): ▁로 공백 표시, 언어 무관 설계

3. 한국어 토큰 효율성:
   - 영어 중심 토크나이저는 한국어를 잘게 쪼갬 (토큰 수 2~4배)
   - 한국어 특화 모델(EXAONE, Kanana)은 한국어 전용 어휘 포함
   - 토큰 효율성 = 비용 효율성 (API 과금 기준)

4. 특수 토큰:
   - [CLS]: 문장 분류용 (BERT)
   - [SEP]: 문장 구분 (BERT)
   - <|endoftext|>: 생성 종료 (GPT)
   - </s>: 시퀀스 종료 (T5)
""")


if __name__ == "__main__":
    compare_tokenizers()
    compare_token_efficiency()
    show_special_tokens()
    print_learning_points()
