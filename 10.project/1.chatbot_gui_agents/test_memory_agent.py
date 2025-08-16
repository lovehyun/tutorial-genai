#!/usr/bin/env python3
"""
메모리 Agent 테스트 스크립트
"""

from agents.memory_agent import MemoryAgent
import time

def test_memory_agent():
    """메모리 Agent 기능 테스트"""
    print("🧠 메모리 Agent 테스트 시작\n")
    
    # 메모리 Agent 초기화 (파일 저장 방식)
    memory_agent = MemoryAgent(storage_file="test_memory.json")
    
    # 1. 기본 메시지 저장 테스트
    print("1️⃣ 기본 메시지 저장 테스트")
    result = memory_agent.process("안녕하세요! 오늘 날씨가 좋네요.", [])
    print(f"   결과: {result['message']}")
    print(f"   메모리 크기: {result['memory_size']}")
    
    # 2. 어시스턴트 응답 저장
    print("\n2️⃣ 어시스턴트 응답 저장 테스트")
    memory_agent.add_assistant_response("안녕하세요! 네, 정말 좋은 날씨네요. 무엇을 도와드릴까요?")
    
    # 3. 추가 대화 저장
    print("\n3️⃣ 추가 대화 저장 테스트")
    memory_agent.process("파이썬에 대해 알려주세요.", [])
    memory_agent.add_assistant_response("파이썬은 간단하고 강력한 프로그래밍 언어입니다.")
    
    memory_agent.process("계산 기능도 있나요?", [])
    memory_agent.add_assistant_response("네, 파이썬에는 다양한 수학 함수와 라이브러리가 있습니다.")
    
    # 4. 메모리 통계 확인
    print("\n4️⃣ 메모리 통계 확인")
    stats = memory_agent.get_memory_stats()
    print(f"   총 메시지: {stats['total_entries']}")
    print(f"   사용자 메시지: {stats['user_messages']}")
    print(f"   어시스턴트 메시지: {stats['assistant_messages']}")
    print(f"   사용률: {stats['memory_usage_percent']:.1f}%")
    
    # 5. 최근 메시지 확인
    print("\n5️⃣ 최근 메시지 확인")
    recent = memory_agent.get_recent_messages(3)
    for i, msg in enumerate(recent, 1):
        print(f"   {i}. {msg}")
    
    # 6. 메모리 검색 테스트
    print("\n6️⃣ 메모리 검색 테스트")
    search_results = memory_agent.search_memory("파이썬")
    print(f"   '파이썬' 검색 결과: {len(search_results)}개")
    for result in search_results:
        print(f"   - {result['type']}: {result['content'][:30]}...")
    
    # 7. 메모리 요약 정보
    print("\n7️⃣ 메모리 요약 정보")
    summary = memory_agent.get_memory_summary()
    print(f"   총 대화 수: {summary['total_conversations']}")
    print(f"   첫 대화: {summary['first_conversation']}")
    print(f"   마지막 대화: {summary['last_conversation']}")
    print(f"   평균 메시지 길이: {summary['average_message_length']:.1f}자")
    
    # 8. 고급 검색 테스트
    print("\n8️⃣ 고급 검색 테스트")
    advanced_results = memory_agent.search_memory_advanced("날씨", "content")
    print(f"   '날씨' 고급 검색 결과: {len(advanced_results)}개")
    
    # 9. 메모리 분석
    print("\n9️⃣ 메모리 분석")
    analytics = memory_agent.get_memory_analytics()
    print(f"   총 메시지: {analytics['total_messages']}")
    print(f"   사용자 메시지: {analytics['user_messages']}")
    print(f"   어시스턴트 메시지: {analytics['assistant_messages']}")
    if analytics['most_active_hour']:
        print(f"   가장 활발한 시간: {analytics['most_active_hour'][0]}시")
    
    # 10. 메모리 크기 정보
    print("\n🔟 메모리 크기 정보")
    size_info = memory_agent.get_memory_size_info()
    print(f"   총 항목: {size_info['total_entries']}")
    print(f"   최대 용량: {size_info['max_capacity']}")
    print(f"   사용률: {size_info['usage_percentage']:.1f}%")
    print(f"   남은 용량: {size_info['remaining_capacity']}")
    
    # 11. 백업 테스트
    print("\n1️⃣1️⃣ 백업 테스트")
    backup_result = memory_agent.backup_memory()
    print(f"   {backup_result}")
    
    # 12. 내보내기 테스트
    print("\n1️⃣2️⃣ 내보내기 테스트")
    export_result = memory_agent.export_memory("test_export.json")
    print(f"   {export_result}")
    
    print("\n✅ 메모리 Agent 테스트 완료!")

def test_database_memory_agent():
    """데이터베이스 메모리 Agent 테스트"""
    print("\n🗄️ 데이터베이스 메모리 Agent 테스트 시작\n")
    
    # 데이터베이스 메모리 Agent 초기화
    db_memory_agent = MemoryAgent(use_database=True)
    
    # 테스트 메시지 저장
    db_memory_agent.process("데이터베이스 테스트 메시지입니다.", [])
    db_memory_agent.add_assistant_response("데이터베이스에 성공적으로 저장되었습니다.")
    
    # 통계 확인
    stats = db_memory_agent.get_memory_stats()
    print(f"   데이터베이스 메모리 크기: {stats['total_entries']}")
    
    print("✅ 데이터베이스 메모리 Agent 테스트 완료!")

if __name__ == "__main__":
    test_memory_agent()
    test_database_memory_agent()
