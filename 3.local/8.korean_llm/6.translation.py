"""
한국어 ↔ 영어 양방향 번역 — LLM 프롬프트 기반
- 설치: ollama pull qwen3:4b
"""
import requests
import json

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:4b"


def translate_ko2en(text, model=MODEL):
    """한국어 → 영어 번역"""
    prompt = f"""Translate the following Korean text to natural English.
Only output the translation. Do not include any explanation.

Korean: {text}

English:"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        },
    )
    return response.json()["response"]


def translate_en2ko(text, model=MODEL):
    """영어 → 한국어 번역"""
    prompt = f"""다음 영어 텍스트를 자연스러운 한국어로 번역해주세요.
번역 결과만 출력하세요. 설명은 포함하지 마세요.

English: {text}

한국어:"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        },
    )
    return response.json()["response"]


def translate_with_style(text, style, model=MODEL):
    """스타일 지정 번역 (존댓말, 반말, 비즈니스 등)"""
    prompt = f"""다음 영어 텍스트를 한국어로 번역해주세요.
문체: {style}
번역 결과만 출력하세요.

English: {text}

한국어:"""

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
    print("  한국어 ↔ 영어 번역")
    print("=" * 50)

    # ── 한국어 → 영어 ──
    print("\n[ 한국어 → 영어 ]")
    print("-" * 40)

    ko_texts = [
        "오늘 날씨가 정말 좋네요. 산책하기 딱 좋은 날입니다.",
        "인공지능 기술이 빠르게 발전하면서 다양한 산업에 변화를 가져오고 있습니다.",
        "이번 프로젝트는 3개월 안에 완료해야 하므로 일정 관리가 중요합니다.",
    ]

    for text in ko_texts:
        print(f"\n한국어: {text}")
        try:
            result = translate_ko2en(text)
            print(f"영  어: {result}")
        except Exception as e:
            print(f"오류: {e}")

    # ── 영어 → 한국어 ──
    print("\n\n[ 영어 → 한국어 ]")
    print("-" * 40)

    en_texts = [
        "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
        "The quarterly revenue exceeded expectations, driven by strong demand in the Asian market.",
        "Please submit the report by Friday and schedule a follow-up meeting for next week.",
    ]

    for text in en_texts:
        print(f"\n영  어: {text}")
        try:
            result = translate_en2ko(text)
            print(f"한국어: {result}")
        except Exception as e:
            print(f"오류: {e}")

    # ── 스타일 지정 번역 ──
    print("\n\n[ 스타일 지정 번역 ]")
    print("-" * 40)

    source = "We need to discuss the project timeline and adjust our priorities."
    styles = [
        ("비즈니스 공식 문서체 (존댓말)", "비즈니스 공식 문서체, 높임말 사용"),
        ("친구 간 대화체 (반말)", "친구 간 캐주얼한 대화체, 반말 사용"),
        ("뉴스 기사체", "뉴스 보도 문체, 객관적이고 간결하게"),
    ]

    print(f"\n원문: {source}")
    for style_name, style_desc in styles:
        try:
            result = translate_with_style(source, style_desc)
            print(f"\n  [{style_name}]")
            print(f"  {result}")
        except Exception as e:
            print(f"  오류: {e}")

    # ── 학습 포인트 ──
    print("\n" + "=" * 50)
    print("  [ 학습 포인트 ]")
    print("=" * 50)
    print("""
1. 양방향 번역:
   - 한→영: 영어 프롬프트로 지시 (영어 출력 유도)
   - 영→한: 한국어 프롬프트로 지시 (한국어 출력 유도)
   - 프롬프트 언어 = 출력 언어 유도 효과

2. 스타일 지정 번역:
   - 동일 원문이라도 문체(비즈니스/캐주얼/뉴스)에 따라 다른 번역
   - 전통 번역기에는 없는 LLM만의 강점

3. Temperature 설정:
   - 번역은 정확성 중요 → temperature=0.2 (매우 낮게)
   - 창의적 의역이 필요하면 0.4~0.5

4. 모델별 번역 품질:
   - Qwen3 4B: 다국어 학습량이 많아 번역 품질 우수
   - EXAONE 3.5: 한국어 자연스러움은 최고
   - 전문 번역: 더 큰 모델(7B+)이나 전용 번역 모델 권장
""")


if __name__ == "__main__":
    main()
