# config/problems.py
"""수학 문제 데이터 정의"""

PROBLEMS = [
    {
        "id": 1,
        "title": "복합 함수의 미분",
        "problem": "f(x) = e^(sin(x²)) 에서 f'(π/2)를 구하시오.",
        "difficulty": "고급",
        "topics": ["복합함수", "연쇄법칙", "삼각함수", "지수함수"],
        "hint": "연쇄법칙을 사용하여 단계별로 미분하세요.",
        "solution_type": "calculus",
        "expected_answer": "약 -4.58"
    },
    {
        "id": 2,
        "title": "조건부 확률과 베이즈 정리",
        "problem": "한 병원에서 특정 질병의 검사를 실시합니다. 이 질병의 유병률은 1%입니다. 검사의 민감도는 95%, 특이도는 90%입니다. 검사 결과가 양성인 사람이 실제로 병에 걸려있을 확률은?",
        "difficulty": "중급",
        "topics": ["베이즈정리", "조건부확률", "의학통계"],
        "hint": "베이즈 정리: P(A|B) = P(B|A) × P(A) / P(B)",
        "solution_type": "probability",
        "expected_answer": "약 8.76%"
    },
    {
        "id": 3,
        "title": "선형대수와 고유값",
        "problem": "행렬 A = [[3, 1], [0, 2]]의 고유값과 고유벡터를 구하고, 대각화 가능한지 판단하시오.",
        "difficulty": "중급",
        "topics": ["고유값", "고유벡터", "대각화", "선형대수"],
        "hint": "특성방정식 det(A - λI) = 0을 풀어보세요.",
        "solution_type": "linear_algebra",
        "expected_answer": "λ₁=3, λ₂=2, 대각화 가능"
    },
    {
        "id": 4,
        "title": "최적화 문제",
        "problem": "한 회사가 제품을 생산하는데, 생산량을 x라 할 때 수익함수가 R(x) = -2x² + 100x - 500 입니다. 최대 수익과 그때의 생산량을 구하시오.",
        "difficulty": "초급",
        "topics": ["2차함수", "최적화", "미분", "응용수학"],
        "hint": "수익함수의 1차 도함수를 구하고 0이 되는 점을 찾으세요.",
        "solution_type": "optimization",
        "expected_answer": "생산량 25개, 최대수익 750"
    },
    {
        "id": 5,
        "title": "급수와 수렴성",
        "problem": "급수 Σ(n=1 to ∞) [(-1)^(n+1) / (n² + 1)]의 수렴성을 판단하고, 가능하다면 합을 구하시오.",
        "difficulty": "고급",
        "topics": ["급수", "교대급수", "수렴성", "라이프니츠정리"],
        "hint": "교대급수의 수렴성을 확인하려면 라이프니츠 조건을 검토하세요.",
        "solution_type": "series",
        "expected_answer": "절대수렴, 합 ≈ 0.915"
    }
]
