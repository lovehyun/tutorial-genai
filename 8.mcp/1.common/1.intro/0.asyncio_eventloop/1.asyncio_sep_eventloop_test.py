# sync_loop_test.py - 동기 방식 (매번 새 이벤트 루프 생성)
"""
동기 방식 테스트 - asyncio.run() 반복 사용

핵심 특징:
- 각 작업마다 asyncio.run() 호출
- 매번 새로운 이벤트 루프 생성/삭제
- 순차적으로 5개 작업 실행 (한 번에 하나씩)

비교 대상: async_loop_test.py와 정확히 같은 작업량
"""

import asyncio
import time

# 비동기 작업 시뮬레이션
async def async_work(task_id: int):
    print(f" - 작업 {task_id} 시작")
    await asyncio.sleep(0.1)  # 0.1초 대기
    print(f" - 작업 {task_id} 완료")
    return f"결과_{task_id}"

# 동기 스타일 실행 방식
def sync_style_execution():
    # 핵심: 각 작업마다 asyncio.run() 호출
    # 매번 새로운 이벤트 루프 생성
    print("=" * 50)
    print("동기 방식: 매번 새 루프 생성")
    print("=" * 50)
    
    num_tasks = 5
    results = []
    
    # 전체 시간 측정
    total_start = time.time()
    
    # 각 작업을 개별적으로 실행
    for i in range(1, num_tasks + 1):
        print(f"\n[작업 {i}] 새로운 이벤트 루프 생성...")
        
        task_start = time.time()
        
        # 매번 asyncio.run() 호출 = 새 루프 생성!
        result = asyncio.run(async_work(i))
        results.append(result)
        
        task_end = time.time()
        task_time = task_end - task_start
        print(f"[작업 {i}] 소요시간: {task_time:.4f}초")
    
    total_end = time.time()
    total_time = total_end - total_start
    
    # 결과 출력
    print("\n" + "=" * 50)
    print("동기 방식 결과")
    print("=" * 50)
    print(f"총 작업 수: {num_tasks}개")
    print(f"총 실행 시간: {total_time:.4f}초")
    print(f"평균 작업 시간: {total_time/num_tasks:.4f}초")
    print(f"순수 작업 시간: {num_tasks * 0.1:.1f}초 (0.1초 × {num_tasks})")
    print(f"루프 생성 오버헤드: {total_time - (num_tasks * 0.1):.4f}초")
    print(f"루프 생성 횟수: {num_tasks}회")
    
    # 결과 저장
    with open("sync_result.txt", "w") as f:
        f.write(f"{total_time:.4f}\n")
        f.write(f"{num_tasks}\n")
        f.write(f"{total_time - (num_tasks * 0.1):.4f}\n")
    
    print(f"\n결과가 'sync_result.txt'에 저장됨")

if __name__ == "__main__":
    print("이벤트 루프 생성 오버헤드 테스트")
    print("테스트 방식: 5개 작업을 순차적으로 실행")
    print("특징: 각 작업마다 새로운 이벤트 루프 생성")
    print()
    
    sync_style_execution()
