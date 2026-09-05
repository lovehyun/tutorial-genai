# 3단계 → 4단계 변경점 (변형 b — 인자 수준 guardrail)

자동승인은 그대로 두고, 인자까지 보는 예외 한 줄을 추가한다.

> 이 폴더는 4단계의 두 변형(`a.tool_name_only` / `b.scoped_guard`) 중 `b` 다 —
> [`../README.md`](../README.md) 참고. `a.tool_name_only/CHANGES.md`에 있는 3→4단계
> 공통 변경(자동승인 등록/해제, DB 현황·작업 로그 패널)은 그대로 적용된다. 여기서는
> `b` 고유의 차이만 적는다.

## `a.tool_name_only/` 대비 바뀐 것

`../servers/` 전부 · `agents.py` · 자동승인 등록/해제 로직 ·
`LOOP`/`run()`/`spawn()` · `JOBS` · `delegate_task` · `list_jobs` 는 `a` 와 동일하다
(포트는 `a`=5084, `b`=5085 로 다르다 — 둘 다 켜두고 비교해도 된다).

## jobs.py — 핵심 변경 한 줄

```python
# a.tool_name_only
def needs_approval(call):
    return call["name"] not in SAFE_TOOLS and call["name"] not in AUTO_APPROVED

# b.scoped_guard (여기)
def needs_approval(call):
    if call["name"] in SAFE_TOOLS:
        return False
    if _is_high_risk(call):          # ← 추가: grant_access 이고 group 이 risk=high 면
        return True                  #    자동승인 여부와 무관하게 항상 다시 물어본다
    return call["name"] not in AUTO_APPROVED
```

`_is_high_risk()`는 `servers/store.py`의 `GROUPS` 시드 데이터에서 위험도를 그대로 읽어온다 —
따로 하드코딩하면 store.py 가 바뀔 때 둘이 어긋날 수 있어서 그렇게 안 했다.

## jobs.py — 왜 '도구 이름'만으로는 안 되는가

`a` 의 자동승인은 **도구 이름** 단위였다. `grant_access` 를 한 번 자동승인하면
`email` 이든 `prod-db` 든 그냥 나갔다 — 무슨 그룹을 주는지(인자)는 안 보고
무슨 도구를 부르는지(이름)만 봤기 때문이다. `b` 는 그 판단을 **인자 수준**까지 내린다.

이건 `3.background_tasks/`(특히 `b.parallel_unsafe`) 의 "요청을 한 덩어리로 묶어서
승인하면 위험도를 구분 못 한다"는 문제와 같은 뿌리다 — 거기는 **승인 요청 단위**가
너무 굵어서, 여기는 **자동승인 등록 단위**가 너무 굵어서 생기는 문제였다.
굵은 단위의 자동화는 항상 위험도를 못 본다는 게 같은 교훈이다.

## app.py — 자동승인 등록(`/jobs/<id>/decide`)은 그대로

"항상 승인"을 누르면 여전히 **도구 이름**을 `AUTO_APPROVED` 에 올린다 — 여기를 바꾸지 않은 건
의도적이다. 사람은 실제로 "이 도구는 앞으로 안 물어봐도 돼"라고 뭉뚱그려 등록하는 경우가
많고, `b` 가 잡으려는 건 바로 그 습관이 고위험 인자까지 덮어버리는 순간이다 —
그래서 **등록은 관대하게, 실행 직전 판단(`needs_approval`)은 엄격하게** 나눴다.

## index.html — 승인 카드에 예외 표시

`job["locked"]`(고위험 인자가 섞여 있으면 True)가 오면:
- **[항상 승인] 버튼을 아예 렌더링하지 않는다** — "이번만 봐줘"(승인/거부)는 있어도
  "고위험도 앞으로 자동으로"는 선택지에서 뺐다. 그렇게 두면 guardrail 자체가 무력화된다.
- 카드에 "⚠️ 고위험 인자 포함 — 자동승인 여부와 무관하게 매번 재확인합니다" 노트를 띄운다.

## 한계

- 지금은 `grant_access` + `risk=high` 그룹, 딱 하나의 규칙만 있다. 실무라면 유효기간·횟수
  제한·감사 로그(누가 언제 왜 예외를 만들었는지)까지 필요하다 —
  [`../a.tool_name_only/CHANGES.md`](../a.tool_name_only/CHANGES.md) 의
  "더 정교하게 가는 법" 표 참고.
- 이 규칙도 `jobs.py` 안에 정적으로 박혀 있다. 그룹별 위험도가 자주 바뀌는 조직이라면
  이 조건 자체를 설정(DB/설정 파일)으로 빼는 게 다음 단계다.
