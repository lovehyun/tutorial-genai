# async_loop_test.py - 비동기 방식 (이벤트 루프 재사용)
"""
비동기 방식 테스트 - 하나의 이벤트 루프 재사용

핵심 특징:
- 전체 프로그램에서 하나의 이벤트 루프만 사용
- await를 사용한 순차 실행
- 순차적으로 5개 작업 실행 (한 번에 하나씩)

비교 대상: sync_loop_test.py와 정확히 같은 작업량
"""

import asyncio
import time

# 비동기 작업 시뮬레이션 (sync_loop_test.py와 동일)
async def async_work(task_id: int):
    print(f" - 작업 {task_id} 시작")
    await asyncio.sleep(0.1)  # 0.1초 대기
    print(f" - 작업 {task_id} 완료")
    return f"결과_{task_id}"

# 비동기 스타일 실행 방식
async def async_style_execution():
    # 핵심: 하나의 이벤트 루프에서 모든 작업 실행
    # 루프 재사용, 생성 오버헤드 없음
    print("=" * 50)
    print("비동기 방식: 하나의 루프 재사용")
    print("=" * 50)
    
    num_tasks = 5
    results = []
    
    # 전체 시간 측정
    total_start = time.time()
    
    # 각 작업을 순차적으로 실행 (같은 루프에서)
    for i in range(1, num_tasks + 1):
        print(f"\n[작업 {i}] 기존 이벤트 루프 재사용...")
        
        task_start = time.time()
        
        # await 사용 = 현재 루프 재사용!
        result = await async_work(i)
        results.append(result)
        
        task_end = time.time()
        task_time = task_end - task_start
        print(f"[작업 {i}] 소요시간: {task_time:.4f}초")
    
    total_end = time.time()
    total_time = total_end - total_start
    
    # 결과 출력
    print("\n" + "=" * 50)
    print("비동기 방식 결과")
    print("=" * 50)
    print(f"총 작업 수: {num_tasks}개")
    print(f"총 실행 시간: {total_time:.4f}초")
    print(f"평균 작업 시간: {total_time/num_tasks:.4f}초")
    print(f"순수 작업 시간: {num_tasks * 0.1:.1f}초 (0.1초 × {num_tasks})")
    print(f"루프 생성 오버헤드: {total_time - (num_tasks * 0.1):.4f}초")
    print(f"루프 생성 횟수: 1회 (재사용)")
    
    # 동기 방식과 비교
    try:
        with open("sync_result.txt", "r") as f:
            lines = f.readlines()
            sync_total_time = float(lines[0].strip())
            sync_overhead = float(lines[2].strip())
        
        async_overhead = total_time - (num_tasks * 0.1)
        
        print("\n" + "=" * 50)
        print("성능 비교 결과")
        print("=" * 50)
        print(f"동기 방식 총 시간: {sync_total_time:.4f}초")
        print(f"비동기 방식 총 시간: {total_time:.4f}초")
        
        if sync_total_time > total_time:
            improvement = ((sync_total_time - total_time) / sync_total_time) * 100
            time_saved = sync_total_time - total_time
            print(f"- 성능 향상: {improvement:.1f}% 빠름")
            print(f"- 절약 시간: {time_saved:.4f}초")
        
        print(f"\n오버헤드 분석:")
        print(f"- 동기 방식 오버헤드: {sync_overhead:.4f}초 (루프 {num_tasks}회 생성)")
        print(f"- 비동기 방식 오버헤드: {async_overhead:.4f}초 (루프 1회 생성)")
        print(f"- 오버헤드 감소: {sync_overhead - async_overhead:.4f}초")
        
        if sync_overhead > async_overhead:
            overhead_reduction = ((sync_overhead - async_overhead) / sync_overhead) * 100
            print(f"오버헤드 {overhead_reduction:.1f}% 감소!")
        
        print("\n결론:")
        print("- 비동기 방식(루프 재사용)이 더 효율적!")
        print("- 이벤트 루프 생성 비용이 성능에 큰 영향을 미침")
        
    except FileNotFoundError:
        print("\nsync_result.txt를 찾을 수 없습니다.")
        print("먼저 'python sync_loop_test.py'를 실행해주세요.")

# 메인 함수
async def main():
    print("이벤트 루프 재사용 테스트")
    print("테스트 방식: 5개 작업을 순차적으로 실행")
    print("특징: 하나의 이벤트 루프에서 모든 작업 처리")
    print()
    
    await async_style_execution()

if __name__ == "__main__":
    # 여기서 한 번만 이벤트 루프 생성!
    asyncio.run(main())
