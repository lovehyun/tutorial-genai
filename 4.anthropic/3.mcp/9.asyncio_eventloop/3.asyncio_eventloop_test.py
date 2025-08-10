# eventloop_comparison.py - 이벤트 루프 방식 비교 (공정한 측정)
"""
4가지 이벤트 루프 실행 방식 비교 (측정 방법 수정):

1. 하나의 루프 + 순차 실행: await를 하나씩 순서대로
2. 하나의 루프 + 동시 실행: asyncio.gather()로 모든 작업 동시
3. 개별 루프 + 순차 실행: asyncio.run()을 5번 반복
4. 개별 루프 + 병렬 실행: ThreadPoolExecutor로 5개 스레드 동시

수정사항: 모든 방법에서 asyncio.run() 호출 시간을 포함하여 공정하게 측정
"""

import asyncio
import time
import concurrent.futures

# 테스트 설정
NUM_TASKS = 5
TASK_DELAY = 0.1

async def async_task(task_id: int):
    """기본 비동기 작업"""
    print(f"작업 {task_id} 시작")
    await asyncio.sleep(TASK_DELAY)
    print(f"작업 {task_id} 완료")
    return f"결과_{task_id}"

def method1_single_loop_sequential():
    """
    방법 1: 하나의 이벤트 루프 + 순차 실행
    
    특징:
    - 하나의 이벤트 루프에서 실행
    - await를 하나씩 순서대로 실행
    - 이전 작업 완료 후 다음 작업 시작
    
    예상 시간: 0.5초 (0.1 x 5) + 최소 오버헤드
    """
    print("\n=== 방법 1: 하나의 루프 + 순차 실행 ===")
    
    async def run_sequential():
        results = []
        for i in range(1, NUM_TASKS + 1):
            print(f"[{i}번째] 작업 시작...")
            result = await async_task(i)
            results.append(result)
        return results
    
    # 공정한 측정: asyncio.run() 포함
    start_time = time.time()
    results = asyncio.run(run_sequential())
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"총 실행 시간: {duration:.3f}초")
    print(f"예상 시간: {NUM_TASKS * TASK_DELAY:.1f}초")
    print(f"오버헤드: {duration - (NUM_TASKS * TASK_DELAY):.3f}초")
    
    return duration, results

def method2_single_loop_concurrent():
    """
    방법 2: 하나의 이벤트 루프 + 동시 실행
    
    특징:
    - 하나의 이벤트 루프에서 실행
    - asyncio.gather()로 모든 작업 동시 시작
    - 모든 작업이 첫 번째 await에서 대기 상태로 전환
    - 가장 오래 걸리는 작업 기준으로 완료
    
    예상 시간: 0.1초 (가장 긴 작업 기준) + 최소 오버헤드
    """
    print("\n=== 방법 2: 하나의 루프 + 동시 실행 ===")
    
    async def run_concurrent():
        print("모든 작업을 동시에 시작...")
        tasks = [async_task(i) for i in range(1, NUM_TASKS + 1)]
        results = await asyncio.gather(*tasks)
        return results
    
    # 공정한 측정: asyncio.run() 포함
    start_time = time.time()
    results = asyncio.run(run_concurrent())
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"총 실행 시간: {duration:.3f}초")
    print(f"예상 시간: {TASK_DELAY:.1f}초")
    print(f"오버헤드: {duration - TASK_DELAY:.3f}초")
    
    return duration, results

def method3_multiple_loops_sequential():
    """
    방법 3: 개별 이벤트 루프 + 순차 실행
    
    특징:
    - 각 작업마다 새로운 이벤트 루프 생성 (asyncio.run())
    - 5번의 이벤트 루프 생성/삭제 오버헤드 발생
    - 순차적으로 하나씩 실행
    
    예상 시간: 0.5초 + 루프 생성 오버헤드 (방법 1보다 느려야 함)
    """
    print("\n=== 방법 3: 개별 루프 + 순차 실행 ===")
    
    # 공정한 측정: 모든 asyncio.run() 포함
    start_time = time.time()
    
    results = []
    for i in range(1, NUM_TASKS + 1):
        print(f"[{i}번째] 새 이벤트 루프 생성 및 작업 실행...")
        result = asyncio.run(async_task(i))
        results.append(result)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"총 실행 시간: {duration:.3f}초")
    print(f"예상 순수 작업 시간: {NUM_TASKS * TASK_DELAY:.1f}초")
    print(f"루프 생성 오버헤드: {duration - (NUM_TASKS * TASK_DELAY):.3f}초")
    
    return duration, results

def method4_multiple_loops_parallel():
    """
    방법 4: 개별 이벤트 루프 + 병렬 실행
    
    특징:
    - ThreadPoolExecutor로 5개 스레드 생성
    - 각 스레드에서 독립적인 이벤트 루프 실행 (asyncio.run())
    - 진짜 병렬 실행 (멀티스레딩)
    
    예상 시간: 0.1초 + 스레드/루프 생성 오버헤드
    """
    print("\n=== 방법 4: 개별 루프 + 병렬 실행 ===")
    
    # 공정한 측정: 모든 과정 포함
    start_time = time.time()
    
    print(f"{NUM_TASKS}개 스레드에서 각각 새 이벤트 루프 생성...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_TASKS) as executor:
        # 각 스레드에서 독립적인 asyncio.run() 실행
        futures = [
            executor.submit(asyncio.run, async_task(i)) 
            for i in range(1, NUM_TASKS + 1)
        ]
        
        # 모든 스레드 완료 대기
        results = [future.result() for future in futures]
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"총 실행 시간: {duration:.3f}초")
    print(f"예상 순수 작업 시간: {TASK_DELAY:.1f}초")
    print(f"스레드/루프 생성 오버헤드: {duration - TASK_DELAY:.3f}초")
    
    return duration, results

def measure_pure_overhead():
    """순수 오버헤드 측정 (빈 작업으로)"""
    print("\n=== 순수 오버헤드 측정 ===")
    
    async def empty_task():
        return "빈_작업"
    
    async def empty_sequential():
        results = []
        for i in range(NUM_TASKS):
            result = await empty_task()
            results.append(result)
        return results
    
    async def empty_concurrent():
        tasks = [empty_task() for _ in range(NUM_TASKS)]
        return await asyncio.gather(*tasks)
    
    # 하나의 루프 오버헤드
    start = time.time()
    asyncio.run(empty_sequential())
    single_loop_overhead = time.time() - start
    
    # 개별 루프 오버헤드
    start = time.time()
    for _ in range(NUM_TASKS):
        asyncio.run(empty_task())
    multiple_loops_overhead = time.time() - start
    
    print(f"하나의 루프 오버헤드: {single_loop_overhead:.3f}초")
    print(f"개별 루프 오버헤드: {multiple_loops_overhead:.3f}초")
    print(f"루프 생성 비용: {multiple_loops_overhead - single_loop_overhead:.3f}초")
    
    return single_loop_overhead, multiple_loops_overhead

def analyze_results(results, overhead_data):
    """결과 분석 및 비교"""
    print("\n" + "="*60)
    print("최종 성능 비교 결과")
    print("="*60)
    
    methods = [
        ("하나의 루프 + 순차", results[0]),
        ("하나의 루프 + 동시", results[1]), 
        ("개별 루프 + 순차", results[2]),
        ("개별 루프 + 병렬", results[3])
    ]
    
    # 실행 시간순 정렬
    sorted_methods = sorted(methods, key=lambda x: x[1][0])
    
    print("실행 시간 순위:")
    for i, (name, (duration, _)) in enumerate(sorted_methods, 1):
        print(f"{i}위. {name}: {duration:.3f}초")
    
    # 성능 비교
    fastest_time = sorted_methods[0][1][0]
    print(f"\n성능 비교 (가장 빠른 방식 기준):")
    for name, (duration, _) in sorted_methods:
        if duration == fastest_time:
            print(f"{name}: 기준 (가장 빠름)")
        else:
            slower_percent = ((duration / fastest_time) - 1) * 100
            print(f"{name}: {slower_percent:.1f}% 느림")
    
    # 이론적 예상과 비교
    single_overhead, multiple_overhead = overhead_data
    print(f"\n오버헤드 분석:")
    print(f"하나의 루프 순차 vs 개별 루프 순차:")
    print(f"  하나의 루프: {results[0][0]:.3f}초")
    print(f"  개별 루프: {results[2][0]:.3f}초")
    print(f"  차이: {results[2][0] - results[0][0]:.3f}초")
    print(f"  순수 루프 생성 비용: {multiple_overhead - single_overhead:.3f}초")
    
    # 논리적 검증
    print(f"\n논리적 검증:")
    if results[0][0] < results[2][0]:
        print("✅ 정상: 하나의 루프 순차가 개별 루프 순차보다 빠름")
    else:
        print("❌ 비정상: 개별 루프 순차가 하나의 루프 순차보다 빠름 (측정 오류 가능)")
    
    if results[1][0] < results[0][0]:
        print("✅ 정상: 동시 실행이 순차 실행보다 빠름")
    else:
        print("❌ 비정상: 순차 실행이 동시 실행보다 빠름")

def main():
    """메인 실행 함수"""
    print("이벤트 루프 실행 방식 비교 테스트 (공정한 측정)")
    print(f"테스트 조건: {NUM_TASKS}개 작업, 각 {TASK_DELAY}초씩 대기")
    print("="*60)
    
    # 순수 오버헤드 먼저 측정
    overhead_data = measure_pure_overhead()
    
    # 4가지 방식 실행
    results = []
    
    # 방법 1: 하나의 루프 + 순차
    result1 = method1_single_loop_sequential()
    results.append(result1)
    
    # 방법 2: 하나의 루프 + 동시  
    result2 = method2_single_loop_concurrent()
    results.append(result2)
    
    # 방법 3: 개별 루프 + 순차
    result3 = method3_multiple_loops_sequential()
    results.append(result3)
    
    # 방법 4: 개별 루프 + 병렬
    result4 = method4_multiple_loops_parallel()
    results.append(result4)
    
    # 결과 분석
    analyze_results(results, overhead_data)
    
    print(f"\n핵심 인사이트:")
    print(f"1. 동시/병렬 실행이 순차 실행보다 압도적으로 빠름")
    print(f"2. 하나의 루프가 개별 루프보다 오버헤드 적음")
    print(f"3. I/O 바운드 작업에서는 이벤트 루프 하나로도 충분히 빠름")
    print(f"4. 멀티스레딩은 추가 오버헤드가 있지만 CPU 집약 작업에 유리")

if __name__ == "__main__":
    main()
