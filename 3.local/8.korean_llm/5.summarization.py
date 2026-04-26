"""
한국어 텍스트 요약 — LLM 프롬프트 기반 요약 생성
- 설치: ollama pull exaone3.5:2.4b
"""
import requests
import json

OLLAMA_URL = "http://localhost:11434"
MODEL = "exaone3.5:2.4b"


def summarize(text, max_sentences=3, model=MODEL):
    """한국어 텍스트를 지정된 문장 수로 요약"""
    prompt = f"""다음 한국어 텍스트를 {max_sentences}문장 이내로 요약해주세요.
핵심 내용만 간결하게 작성하세요. 요약만 출력하세요.

텍스트:
{text}

요약:"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3},
        },
    )
    return response.json()["response"]


def summarize_bullet(text, num_points=5, model=MODEL):
    """핵심 포인트를 불릿 리스트로 요약"""
    prompt = f"""다음 한국어 텍스트의 핵심 내용을 {num_points}개 불릿 포인트로 정리해주세요.
각 포인트는 한 줄로 간결하게 작성하세요.

텍스트:
{text}

핵심 포인트:"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3},
        },
    )
    return response.json()["response"]


def main():
    print("=" * 50)
    print("  한국어 텍스트 요약")
    print("=" * 50)

    # ── 뉴스 기사 요약 ──
    print("\n[ 뉴스 기사 요약 ]")
    print("-" * 40)

    article1 = """인공지능(AI) 기술의 발전이 가속화되면서 한국 기업들도 자체 AI 모델 개발에
박차를 가하고 있다. LG는 EXAONE 시리즈를, 카카오는 Kanana 시리즈를,
네이버는 HyperCLOVA를 각각 개발하며 글로벌 AI 경쟁에 뛰어들었다.
특히 2025년 정부의 소버린 AI 프로젝트에 네이버, SK텔레콤, 업스테이지,
LG AI 리서치, NC AI 등 5개 컨소시엄이 선정되어 한국어에 특화된
대규모 언어모델 개발이 본격화되고 있다. 이들 모델은 한국어의 교착어적
특성과 문화적 맥락을 깊이 반영하여, 영어 중심 모델에서는 부족했던
한국어 이해 능력을 크게 개선할 것으로 기대된다. 정부는 2400억 원 규모의
예산을 투입하여 2026년까지 세계 수준의 한국어 AI 모델을 확보한다는
목표를 세웠다."""

    print(f"\n원문 ({len(article1)}자):")
    print(article1.strip())

    try:
        print(f"\n3문장 요약:")
        print(summarize(article1, 3))

        print(f"\n불릿 포인트 요약:")
        print(summarize_bullet(article1, 5))
    except Exception as e:
        print(f"오류: {e}")

    # ── 긴 기술 문서 요약 ──
    print("\n\n[ 기술 문서 요약 ]")
    print("-" * 40)

    article2 = """트랜스포머(Transformer)는 2017년 구글이 발표한 'Attention Is All You Need'
논문에서 처음 제안된 딥러닝 아키텍처이다. 기존의 RNN이나 LSTM과 달리
셀프 어텐션(Self-Attention) 메커니즘을 사용하여 입력 시퀀스의 모든 위치를
동시에 참조할 수 있다. 이를 통해 병렬 처리가 가능해지면서 학습 속도가
크게 향상되었다.

트랜스포머의 핵심인 멀티헤드 어텐션(Multi-Head Attention)은 여러 개의
어텐션 헤드가 서로 다른 관점에서 입력을 분석하는 구조이다. 인코더는
입력 시퀀스를 이해하고, 디코더는 인코더의 출력을 참조하여 새로운
시퀀스를 생성한다. 포지셔널 인코딩으로 단어의 위치 정보를 보존한다.

이후 BERT(인코더만), GPT(디코더만), T5(인코더-디코더) 등 다양한 변형이
등장하면서 NLP 분야 전반에 혁신을 가져왔다. 현재 대부분의 대규모
언어모델(LLM)은 트랜스포머 아키텍처를 기반으로 하고 있다."""

    try:
        print(f"\n원문 ({len(article2)}자):")
        print(article2.strip())
        print(f"\n2문장 요약:")
        print(summarize(article2, 2))
    except Exception as e:
        print(f"오류: {e}")

    # ── 학습 포인트 ──
    print("\n" + "=" * 50)
    print("  [ 학습 포인트 ]")
    print("=" * 50)
    print("""
1. 요약 유형:
   - 추출 요약(Extractive): 원문에서 중요 문장을 선택
   - 생성 요약(Abstractive): 새로운 문장으로 재구성 ← LLM 방식
   - LLM은 생성 요약에 강점 (자연스러운 한국어 생성)

2. Temperature 설정:
   - 요약은 정확성이 중요 → temperature=0.3 (낮게)
   - 창작/대화는 다양성이 중요 → temperature=0.7~0.9

3. 출력 형식 제어:
   - "N문장 이내로" → 길이 제어
   - "불릿 포인트로" → 구조화된 출력
   - "한 줄로 간결하게" → 압축 수준 제어

4. EXAONE 3.5의 한국어 요약 강점:
   - 한국어 문법에 맞는 자연스러운 문장 생성
   - 핵심 내용 파악 및 재구성 능력 우수
""")


if __name__ == "__main__":
    main()
