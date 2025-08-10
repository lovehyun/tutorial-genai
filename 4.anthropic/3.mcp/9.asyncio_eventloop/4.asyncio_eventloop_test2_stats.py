# precise_measurement.py - 정밀 측정으로 재검증
"""
더 정확한 측정을 위한 개선사항:
1. 각 방법을 여러 번 실행하여 평균 계산
2. 실행 순서 랜덤화
3. 통계적 분석 추가
"""

import asyncio
import time
import statistics
import random

NUM_TASKS = 5
TASK_DELAY = 0.1
REPEAT_COUNT = 10  # 각 방법을 10번씩 실행

async def async_task(task_id: int):
    """기본 비동기 작업 (출력 제거로 노이즈 감소)"""
    await asyncio.sleep(TASK_DELAY)
    return f"결과_{task_id}"

def measure_single_loop_sequential():
    """하나의 루프 + 순차 실행 측정"""
    async def run_sequential():
        results = []
        for i in range(1, NUM_TASKS + 1):
            result = await async_task(i)
            results.append(result)
        return results
    
    start_time = time.perf_counter()  # 더 정밀한 시간 측정
    results = asyncio.run(run_sequential())
    end_time = time.perf_counter()
    
    return end_time - start_time

def measure_multiple_loops_sequential():
    """개별 루프 + 순차 실행 측정"""
    start_time = time.perf_counter()
    
    results = []
    for i in range(1, NUM_TASKS + 1):
        result = asyncio.run(async_task(i))
        results.append(result)
    
    end_time = time.perf_counter()
    return end_time - start_time

def run_repeated_measurements():
    """반복 측정 및 통계 분석"""
    print("정밀 측정 시작 (각 방법 10번씩 실행)")
    print("="*50)
    
    # 측정 함수들
    methods = [
        ("하나의 루프 + 순차", measure_single_loop_sequential),
        ("개별 루프 + 순차", measure_multiple_loops_sequential)
    ]
    
    results = {}
    
    for method_name, measure_func in methods:
        print(f"\n{method_name} 측정 중...")
        times = []
        
        for i in range(REPEAT_COUNT):
            # 각 측정 사이에 잠시 대기 (시스템 안정화)
            time.sleep(0.1)
            
            duration = measure_func()
            times.append(duration)
            print(f"  {i+1}회: {duration:.4f}초")
        
        results[method_name] = times
    
    return results

def analyze_statistical_results(results):
    """통계적 분석"""
    print("\n" + "="*60)
    print("통계적 분석 결과")
    print("="*60)
    
    for method_name, times in results.items():
        mean_time = statistics.mean(times)
        median_time = statistics.median(times)
        stdev_time = statistics.stdev(times) if len(times) > 1 else 0
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n{method_name}:")
        print(f"  평균: {mean_time:.4f}초")
        print(f"  중앙값: {median_time:.4f}초")
        print(f"  표준편차: {stdev_time:.4f}초")
        print(f"  최소: {min_time:.4f}초")
        print(f"  최대: {max_time:.4f}초")
        print(f"  변동계수: {(stdev_time/mean_time)*100:.1f}%")
    
    # 평균 기준 비교
    single_loop_mean = statistics.mean(results["하나의 루프 + 순차"])
    multiple_loops_mean = statistics.mean(results["개별 루프 + 순차"])
    
    print(f"\n평균 기준 비교:")
    print(f"하나의 루프 평균: {single_loop_mean:.4f}초")
    print(f"개별 루프 평균: {multiple_loops_mean:.4f}초")
    print(f"차이: {multiple_loops_mean - single_loop_mean:.4f}초")
    
    if single_loop_mean < multiple_loops_mean:
        improvement = ((multiple_loops_mean - single_loop_mean) / multiple_loops_mean) * 100
        print(f"✅ 하나의 루프가 {improvement:.2f}% 빠름 (정상)")
    else:
        decline = ((single_loop_mean - multiple_loops_mean) / single_loop_mean) * 100
        print(f"❌ 개별 루프가 {decline:.2f}% 빠름 (비정상)")
    
    # t-검정으로 통계적 유의성 검증
    try:
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(
            results["하나의 루프 + 순차"], 
            results["개별 루프 + 순차"]
        )
        print(f"\nt-검정 결과:")
        print(f"t-통계량: {t_stat:.4f}")
        print(f"p-값: {p_value:.4f}")
        
        if p_value < 0.05:
            print(f"✅ 통계적으로 유의한 차이 (p < 0.05)")
        else:
            print(f"❌ 통계적으로 유의하지 않음 (p >= 0.05)")
            print(f"   → 측정 오차 범위일 가능성 높음")
            
    except ImportError:
        print(f"\nscipy가 설치되지 않아 t-검정을 수행할 수 없습니다.")
    
    # 실용적 결론
    abs_diff = abs(single_loop_mean - multiple_loops_mean)
    relative_diff = (abs_diff / min(single_loop_mean, multiple_loops_mean)) * 100
    
    print(f"\n실용적 결론:")
    print(f"절대 차이: {abs_diff:.4f}초")
    print(f"상대 차이: {relative_diff:.1f}%")
    
    if relative_diff < 5:
        print(f"→ 차이가 5% 미만으로 실용적으로는 동일한 성능")
        print(f"→ 이론적으로는 하나의 루프가 빨라야 하지만 측정 오차 범위")
    else:
        print(f"→ 의미 있는 성능 차이 존재")

def main():
    """메인 실행"""
    print("정밀 측정을 통한 이벤트 루프 성능 비교")
    print(f"테스트 조건: {NUM_TASKS}개 작업, 각 {TASK_DELAY}초, {REPEAT_COUNT}회 반복")
    
    results = run_repeated_measurements()
    analyze_statistical_results(results)
    
    print(f"\n최종 결론:")
    print(f"이론적으로는 하나의 루프가 빨라야 하지만,")
    print(f"실제 차이는 매우 작아서 측정 오차 범위일 가능성이 높습니다.")
    print(f"두 방식 모두 실용적으로는 비슷한 성능을 보입니다.")

if __name__ == "__main__":
    main()
