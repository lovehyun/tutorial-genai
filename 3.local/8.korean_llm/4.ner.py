"""
한국어 개체명 인식(NER) — LLM 프롬프트 기반 엔티티 추출
- 설치: ollama pull qwen3:4b
"""
import requests
import json

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:4b"


def extract_entities(text, model=MODEL):
    """텍스트에서 고유명사(Named Entity)를 추출"""
    prompt = f"""다음 한국어 텍스트에서 고유명사(Named Entity)를 추출해주세요.

카테고리:
- PER: 인물 (사람 이름)
- ORG: 조직 (회사, 기관, 단체)
- LOC: 장소 (도시, 국가, 건물)
- DATE: 날짜/시간
- PRODUCT: 제품/서비스명

반드시 아래 JSON 배열 형식으로만 답변하세요:
[{{"entity": "추출된 텍스트", "type": "카테고리", "description": "설명"}}]

엔티티가 없으면 빈 배열 []을 반환하세요.

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


def main():
    print("=" * 50)
    print("  한국어 개체명 인식 (NER)")
    print("=" * 50)

    # ── 뉴스 기사 NER ──
    print("\n[ 뉴스 기사 ]")
    print("-" * 40)

    news_texts = [
        "삼성전자 이재용 회장은 2024년 1월 서울 서초구 삼성타운에서 갤럭시 S24 출시 행사를 진행했다.",
        "네이버 최수연 대표가 판교 그린팩토리에서 HyperCLOVA X의 성능 개선 계획을 발표했다.",
        "현대자동차는 2025년 3월 울산 공장에서 전기차 아이오닉 9를 처음 공개했다.",
    ]

    for text in news_texts:
        print(f"\n텍스트: {text}")
        try:
            result = extract_entities(text)
            print(f"엔티티: {result}")
        except Exception as e:
            print(f"오류: {e}")

    # ── 일상 대화 NER ──
    print("\n\n[ 일상 대화 ]")
    print("-" * 40)

    daily_texts = [
        "내일 오후 2시에 강남역 스타벅스에서 김민수 씨랑 미팅이 있어.",
        "지난 주말에 제주도 여행 갔다왔는데 성산일출봉이 정말 멋있었어.",
        "카카오톡으로 이모한테 추석 인사 보내야 하는데 깜빡했다.",
    ]

    for text in daily_texts:
        print(f"\n텍스트: {text}")
        try:
            result = extract_entities(text)
            print(f"엔티티: {result}")
        except Exception as e:
            print(f"오류: {e}")

    # ── 학습 포인트 ──
    print("\n" + "=" * 50)
    print("  [ 학습 포인트 ]")
    print("=" * 50)
    print("""
1. 프롬프트 기반 NER:
   - 전통 NER: 학습 데이터(BIO 태깅)로 시퀀스 레이블링 모델 학습
   - LLM NER: 프롬프트에 카테고리 정의만 주면 추출 가능
   - 새 카테고리(예: FOOD, EVENT) 추가가 즉시 가능

2. 한국어 NER의 어려움:
   - 교착어 특성: '삼성전자의', '삼성전자가' 등 조사 분리 필요
   - 띄어쓰기 불규칙: '이재용회장' vs '이재용 회장'
   - LLM은 이런 한국어 특성을 잘 처리함

3. 출력 형식:
   - JSON 배열로 구조화 → 후처리(파싱, DB 저장)에 용이
   - type 필드로 엔티티 종류 자동 분류

4. 실무 활용:
   - 뉴스 자동 태깅, 문서 메타데이터 추출
   - 고객 문의에서 주문번호/제품명 자동 추출
   - 계약서에서 당사자/날짜/금액 추출
""")


if __name__ == "__main__":
    main()
