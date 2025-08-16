import time
import json
import os
import sqlite3
from typing import Dict, List, Any
from datetime import datetime

class MemoryAgent:
    def __init__(self, storage_file: str = "memory_data.json", use_database: bool = False):
        """메모리 Agent 초기화"""
        self.memory = []
        self.max_memory_size = 100  # 최대 저장할 대화 수
        self.storage_file = storage_file
        self.use_database = use_database
        
        if use_database:
            self.db_file = "memory.db"
            self.init_database()
        else:
            # 저장된 메모리 로드
            self.load_memory()
    
    def init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 메모리 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    processed_at TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"데이터베이스 {self.db_file}가 초기화되었습니다.")
            
            # 기존 메모리 로드
            self.load_memory_from_db()
            
        except Exception as e:
            print(f"데이터베이스 초기화 오류: {e}")
    
    def save_memory_to_db(self):
        """메모리를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 기존 데이터 삭제 (최신 데이터만 유지)
            cursor.execute("DELETE FROM memory")
            
            # 새 데이터 삽입
            for entry in self.memory:
                cursor.execute('''
                    INSERT INTO memory (type, content, timestamp, processed_at)
                    VALUES (?, ?, ?, ?)
                ''', (entry['type'], entry['content'], entry['timestamp'], entry['processed_at']))
            
            conn.commit()
            conn.close()
            print(f"메모리가 데이터베이스에 저장되었습니다.")
            
        except Exception as e:
            print(f"데이터베이스 저장 오류: {e}")
    
    def load_memory_from_db(self):
        """데이터베이스에서 메모리 로드"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT type, content, timestamp, processed_at FROM memory ORDER BY timestamp")
            rows = cursor.fetchall()
            
            self.memory = []
            for row in rows:
                self.memory.append({
                    'type': row[0],
                    'content': row[1],
                    'timestamp': row[2],
                    'processed_at': row[3]
                })
            
            conn.close()
            print(f"메모리가 데이터베이스에서 로드되었습니다.")
            
        except Exception as e:
            print(f"데이터베이스 로드 오류: {e}")
            self.memory = []
        
    def save_memory(self):
        """메모리를 파일에 저장"""
        if self.use_database:
            self.save_memory_to_db()
        else:
            try:
                with open(self.storage_file, 'w', encoding='utf-8') as f:
                    json.dump(self.memory, f, ensure_ascii=False, indent=2)
                print(f"메모리가 {self.storage_file}에 저장되었습니다.")
            except Exception as e:
                print(f"메모리 저장 오류: {e}")
    
    def load_memory(self):
        """파일에서 메모리 로드"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
                print(f"메모리가 {self.storage_file}에서 로드되었습니다.")
        except Exception as e:
            print(f"메모리 로드 오류: {e}")
            self.memory = []
        
    def process(self, message: str, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """메시지를 처리하고 메모리에 저장"""
        # 현재 시간
        timestamp = time.time()
        
        # 메모리에 사용자 메시지 저장
        memory_entry = {
            'type': 'user_message',
            'content': message,
            'timestamp': timestamp,
            'processed_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        }
        
        self.memory.append(memory_entry)
        
        # 메모리 크기 제한
        if len(self.memory) > self.max_memory_size:
            self.memory = self.memory[-self.max_memory_size:]
        
        # 파일에 저장
        self.save_memory()
        
        # 컨텍스트 생성 (최근 5개 대화)
        recent_context = self._get_recent_context(5)
        
        return {
            'status': 'success',
            'context': recent_context,
            'memory_size': len(self.memory),
            'message': '메시지가 메모리에 저장되었습니다.'
        }
    
    def _get_recent_context(self, count: int = 5) -> str:
        """최근 대화 컨텍스트 반환"""
        recent_messages = self.memory[-count:] if len(self.memory) >= count else self.memory
        
        context_parts = []
        for entry in recent_messages:
            if entry['type'] == 'user_message':
                context_parts.append(f"사용자: {entry['content']}")
            elif entry['type'] == 'assistant_message':
                context_parts.append(f"어시스턴트: {entry['content']}")
        
        return "\n".join(context_parts)
    
    def add_assistant_response(self, response: str):
        """어시스턴트 응답을 메모리에 저장"""
        timestamp = time.time()
        
        memory_entry = {
            'type': 'assistant_message',
            'content': response,
            'timestamp': timestamp,
            'processed_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        }
        
        self.memory.append(memory_entry)
        
        # 메모리 크기 제한
        if len(self.memory) > self.max_memory_size:
            self.memory = self.memory[-self.max_memory_size:]
        
        # 파일에 저장
        self.save_memory()
    
    def search_memory(self, query: str) -> List[Dict[str, Any]]:
        """메모리에서 관련 내용 검색"""
        results = []
        query_lower = query.lower()
        
        for entry in self.memory:
            if query_lower in entry['content'].lower():
                results.append(entry)
        
        return results
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """메모리 통계 반환"""
        user_messages = [entry for entry in self.memory if entry['type'] == 'user_message']
        assistant_messages = [entry for entry in self.memory if entry['type'] == 'assistant_message']
        
        return {
            'total_entries': len(self.memory),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'max_memory_size': self.max_memory_size,
            'memory_usage_percent': (len(self.memory) / self.max_memory_size) * 100
        }
    
    def get_recent_messages(self, count: int = 5) -> List[str]:
        """최근 메시지들 반환"""
        recent_messages = []
        for entry in self.memory[-count:]:
            if entry['type'] == 'user_message':
                recent_messages.append(f"사용자: {entry['content']}")
            elif entry['type'] == 'assistant_message':
                recent_messages.append(f"AI: {entry['content'][:50]}...")
        return recent_messages
    
    def clear_memory(self):
        """메모리 초기화"""
        self.memory = []
        self.save_memory()
        return {'status': 'success', 'message': '메모리가 초기화되었습니다.'}
    
    # 새로운 확장 기능들
    def get_memory_by_date(self, start_date: str, end_date: str = None) -> List[Dict[str, Any]]:
        """특정 날짜 범위의 메모리 조회"""
        try:
            start_timestamp = datetime.strptime(start_date, '%Y-%m-%d').timestamp()
            end_timestamp = datetime.strptime(end_date, '%Y-%m-%d').timestamp() if end_date else time.time()
            
            filtered_memory = []
            for entry in self.memory:
                if start_timestamp <= entry['timestamp'] <= end_timestamp:
                    filtered_memory.append(entry)
            
            return filtered_memory
        except Exception as e:
            print(f"날짜별 메모리 조회 오류: {e}")
            return []
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """메모리 요약 정보 반환"""
        if not self.memory:
            return {'message': '저장된 메모리가 없습니다.'}
        
        # 가장 많이 언급된 키워드 찾기
        all_content = ' '.join([entry['content'] for entry in self.memory])
        words = all_content.split()
        word_count = {}
        for word in words:
            if len(word) > 1:  # 1글자 단어 제외
                word_count[word] = word_count.get(word, 0) + 1
        
        top_keywords = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_conversations': len(self.memory) // 2,  # 대화는 보통 2개씩
            'first_conversation': self.memory[0]['processed_at'] if self.memory else None,
            'last_conversation': self.memory[-1]['processed_at'] if self.memory else None,
            'top_keywords': top_keywords,
            'average_message_length': sum(len(entry['content']) for entry in self.memory) / len(self.memory)
        }
    
    def export_memory(self, filename: str = None) -> str:
        """메모리를 파일로 내보내기"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"memory_export_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
            return f"메모리가 {filename}로 내보내졌습니다."
        except Exception as e:
            return f"메모리 내보내기 오류: {e}"
    
    def import_memory(self, filename: str) -> str:
        """파일에서 메모리 가져오기"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_memory = json.load(f)
            
            # 기존 메모리와 병합
            self.memory.extend(imported_memory)
            
            # 중복 제거 (timestamp 기준)
            seen_timestamps = set()
            unique_memory = []
            for entry in self.memory:
                if entry['timestamp'] not in seen_timestamps:
                    seen_timestamps.add(entry['timestamp'])
                    unique_memory.append(entry)
            
            self.memory = unique_memory
            
            # 메모리 크기 제한
            if len(self.memory) > self.max_memory_size:
                self.memory = self.memory[-self.max_memory_size:]
            
            self.save_memory()
            return f"메모리가 {filename}에서 가져와졌습니다."
        except Exception as e:
            return f"메모리 가져오기 오류: {e}"
    
    # 메모리 관리 명령어들
    def backup_memory(self) -> str:
        """메모리 백업 생성"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"memory_backup_{timestamp}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
            
            return f"메모리 백업이 {backup_file}에 생성되었습니다."
        except Exception as e:
            return f"백업 생성 오류: {e}"
    
    def restore_memory(self, backup_file: str) -> str:
        """백업에서 메모리 복원"""
        try:
            if not os.path.exists(backup_file):
                return f"백업 파일 {backup_file}을 찾을 수 없습니다."
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                self.memory = json.load(f)
            
            self.save_memory()
            return f"메모리가 {backup_file}에서 복원되었습니다."
        except Exception as e:
            return f"메모리 복원 오류: {e}"
    
    def get_memory_analytics(self) -> Dict[str, Any]:
        """메모리 분석 정보 반환"""
        if not self.memory:
            return {'message': '분석할 메모리가 없습니다.'}
        
        # 시간대별 분석
        hour_counts = {}
        day_counts = {}
        
        for entry in self.memory:
            dt = datetime.fromtimestamp(entry['timestamp'])
            hour = dt.hour
            day = dt.strftime('%Y-%m-%d')
            
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
            day_counts[day] = day_counts.get(day, 0) + 1
        
        # 가장 활발한 시간대
        most_active_hour = max(hour_counts.items(), key=lambda x: x[1]) if hour_counts else None
        most_active_day = max(day_counts.items(), key=lambda x: x[1]) if day_counts else None
        
        # 메시지 길이 분석
        user_lengths = [len(entry['content']) for entry in self.memory if entry['type'] == 'user_message']
        assistant_lengths = [len(entry['content']) for entry in self.memory if entry['type'] == 'assistant_message']
        
        return {
            'total_messages': len(self.memory),
            'user_messages': len(user_lengths),
            'assistant_messages': len(assistant_lengths),
            'most_active_hour': most_active_hour,
            'most_active_day': most_active_day,
            'avg_user_message_length': sum(user_lengths) / len(user_lengths) if user_lengths else 0,
            'avg_assistant_message_length': sum(assistant_lengths) / len(assistant_lengths) if assistant_lengths else 0,
            'hourly_activity': hour_counts,
            'daily_activity': day_counts
        }
    
    def search_memory_advanced(self, query: str, search_type: str = 'content') -> List[Dict[str, Any]]:
        """고급 메모리 검색"""
        results = []
        query_lower = query.lower()
        
        for entry in self.memory:
            match = False
            
            if search_type == 'content':
                # 내용에서 검색
                if query_lower in entry['content'].lower():
                    match = True
            elif search_type == 'type':
                # 메시지 타입에서 검색
                if query_lower in entry['type'].lower():
                    match = True
            elif search_type == 'date':
                # 날짜에서 검색
                if query_lower in entry['processed_at']:
                    match = True
            elif search_type == 'all':
                # 모든 필드에서 검색
                for value in entry.values():
                    if query_lower in str(value).lower():
                        match = True
                        break
            
            if match:
                results.append(entry)
        
        return results
    
    def get_memory_by_type(self, message_type: str) -> List[Dict[str, Any]]:
        """특정 타입의 메모리 조회"""
        return [entry for entry in self.memory if entry['type'] == message_type]
    
    def get_conversation_threads(self) -> List[List[Dict[str, Any]]]:
        """대화 스레드별로 메모리 그룹화"""
        threads = []
        current_thread = []
        
        for entry in self.memory:
            if entry['type'] == 'user_message' and current_thread:
                # 새로운 사용자 메시지가 시작되면 새 스레드
                threads.append(current_thread)
                current_thread = []
            
            current_thread.append(entry)
        
        # 마지막 스레드 추가
        if current_thread:
            threads.append(current_thread)
        
        return threads
    
    def get_memory_size_info(self) -> Dict[str, Any]:
        """메모리 크기 정보 반환"""
        total_size = len(self.memory)
        user_size = len([e for e in self.memory if e['type'] == 'user_message'])
        assistant_size = len([e for e in self.memory if e['type'] == 'assistant_message'])
        
        return {
            'total_entries': total_size,
            'user_entries': user_size,
            'assistant_entries': assistant_size,
            'max_capacity': self.max_memory_size,
            'usage_percentage': (total_size / self.max_memory_size) * 100,
            'remaining_capacity': self.max_memory_size - total_size
        }
