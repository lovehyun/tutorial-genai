# Attention 메커니즘 시각화

Transformer의 핵심인 Self-Attention이 실제로 어떤 단어에 주목하는지 시각화합니다.

## Self-Attention이란?

```
"나는 사과를 먹었다"

  나는  사과를  먹었다
나는   0.1    0.3    0.6    ← "나는"이 가장 주목하는 단어는 "먹었다"
사과를  0.2    0.1    0.7    ← "사과를"도 "먹었다"에 주목
먹었다  0.3    0.5    0.2    ← "먹었다"는 "사과를"에 주목 (무엇을 먹었는지)
```

각 단어가 다른 모든 단어에 대해 "얼마나 주목하는지" 가중치(0~1)를 계산합니다.

## 예제

| 파일 | 설명 |
|------|------|
| `1.attention_visualize.py` | BERT Attention 가중치 추출 및 히트맵 시각화 |

## 설치

```bash
pip install transformers torch matplotlib seaborn
```
