#!/usr/bin/env python3
"""
MCP 파일시스템 채팅 클라이언트
실행: python mcp-client.py
"""

import asyncio
import json
import subprocess
import os
from typing import Dict, List
import time

class MCPFileSystemClient:
    def __init__(self, work_directory: str = None):
        self.work_directory = work_directory or os.getcwd()
        self.mcp_process = None
        self.current_directory = self.work_directory
        
    async def start_mcp_server(self):
        """MCP 파일시스템 서버 시작"""
        try:
            # npx @modelcontextprotocol/server-filesystem 실행
            self.mcp_process = subprocess.Popen([
                'npx', '@modelcontextprotocol/server-filesystem', self.work_directory
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
            text=True, bufsize=1)
            
            print(f"✓ MCP 서버가 시작되었습니다. 작업 디렉토리: {self.work_directory}")
            return True
        except Exception as e:
            print(f"✗ MCP 서버 시작 실패: {e}")
            return False
            
    def stop_mcp_server(self):
        """MCP 서버 종료"""
        if self.mcp_process:
            self.mcp_process.terminate()
            self.mcp_process.wait()
            
    async def send_mcp_request(self, method: str, params: Dict = None) -> Dict:
        """MCP 서버에 요청 전송"""
        if not self.mcp_process:
            return {"error": "MCP 서버가 실행되지 않았습니다"}
            
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": method,
            "params": params or {}
        }
        
        try:
            request_json = json.dumps(request) + '\n'
            self.mcp_process.stdin.write(request_json)
            self.mcp_process.stdin.flush()
            
            # 응답 읽기 (간단한 구현)
            response_line = self.mcp_process.stdout.readline()
            if response_line:
                return json.loads(response_line.strip())
        except Exception as e:
            return {"error": f"MCP 요청 실패: {e}"}
            
        return {"error": "응답을 받지 못했습니다"}
    
    def list_files(self, directory: str = None) -> List[str]:
        """파일 목록 조회 (로컬 구현)"""
        target_dir = directory or self.current_directory
        try:
            files = []
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if os.path.isfile(item_path):
                    files.append(f"📄 {item}")
                else:
                    files.append(f"📁 {item}/")
            return files
        except Exception as e:
            return [f"❌ 오류: {e}"]
    
    def copy_file(self, source: str, destination: str) -> str:
        """파일 복사"""
        try:
            import shutil
            source_path = os.path.join(self.current_directory, source)
            dest_path = os.path.join(self.current_directory, destination)
            
            if not os.path.exists(source_path):
                return f"❌ 원본 파일을 찾을 수 없습니다: {source}"
                
            shutil.copy2(source_path, dest_path)
            return f"✅ 파일 복사 완료: {source} → {destination}"
        except Exception as e:
            return f"❌ 복사 실패: {e}"
    
    def copy_files_by_pattern(self, pattern: str, start_week: int, end_week: int) -> List[str]:
        """패턴 기반 파일 복사 (주차별)"""
        import glob
        results = []
        
        # 패턴에 맞는 파일 찾기
        search_pattern = os.path.join(self.current_directory, pattern)
        matching_files = glob.glob(search_pattern)
        
        if not matching_files:
            return [f"❌ 패턴에 맞는 파일을 찾을 수 없습니다: {pattern}"]
        
        for file_path in matching_files:
            filename = os.path.basename(file_path)
            results.append(f"📄 원본 파일 발견: {filename}")
            
            # 주차별 복사
            for week in range(start_week, end_week + 1):
                new_filename = filename.replace("1주차", f"{week}주차")
                result = self.copy_file(filename, new_filename)
                results.append(f"  {result}")
                
        return results
    
    def rename_file(self, old_name: str, new_name: str) -> str:
        """파일 이름 변경"""
        try:
            old_path = os.path.join(self.current_directory, old_name)
            new_path = os.path.join(self.current_directory, new_name)
            
            if not os.path.exists(old_path):
                return f"❌ 파일을 찾을 수 없습니다: {old_name}"
                
            os.rename(old_path, new_path)
            return f"✅ 파일명 변경 완료: {old_name} → {new_name}"
        except Exception as e:
            return f"❌ 이름 변경 실패: {e}"
    
    def change_directory(self, path: str) -> str:
        """디렉토리 변경"""
        try:
            if os.path.isabs(path):
                new_path = path
            else:
                new_path = os.path.join(self.current_directory, path)
                
            new_path = os.path.abspath(new_path)
            
            if os.path.exists(new_path) and os.path.isdir(new_path):
                self.current_directory = new_path
                return f"✅ 디렉토리 변경: {new_path}"
            else:
                return f"❌ 디렉토리를 찾을 수 없습니다: {path}"
        except Exception as e:
            return f"❌ 디렉토리 변경 실패: {e}"
    
    ####################
    # 메인 함수
    ####################
    def process_command(self, user_input: str) -> List[str]:
        """사용자 명령 처리"""
        user_input = user_input.strip().lower()
        
        # 파일 목록 조회
        if any(cmd in user_input for cmd in ['파일', '목록', 'list', 'ls', 'dir']):
            files = self.list_files()
            return [f"📂 현재 디렉토리: {self.current_directory}"] + files
        
        # 디렉토리 변경
        elif user_input.startswith(('cd ', '이동 ')):
            path = user_input.split(' ', 1)[1] if ' ' in user_input else ''
            result = self.change_directory(path)
            return [result]
        
        # 주차별 파일 복사
        elif any(keyword in user_input for keyword in ['주차', '복사', 'copy']):
            if '1주차' in user_input and ('12주차' in user_input or '2-12' in user_input):
                results = self.copy_files_by_pattern("*1주차*.hwp", 2, 12)
                return results
            elif '복사' in user_input:
                return ["📝 사용법: '1주차 파일을 12주차까지 복사해줘' 형태로 입력하세요"]
        
        # 파일 이름 변경
        elif '이름변경' in user_input or 'rename' in user_input:
            return ["📝 사용법: 'rename 원본파일명 새파일명' 형태로 입력하세요"]
        
        # 도움말
        elif user_input in ['help', '도움말', '?']:
            return [
                "MCP 파일시스템 채팅 클라이언트 명령어:",
                "  - 파일목록, list, ls, dir - 현재 폴더 파일 목록",
                "  - cd <경로> - 디렉토리 변경",
                "  - 1주차 파일을 12주차까지 복사해줘 - 주차별 파일 복사",
                "  - rename <원본> <새이름> - 파일 이름 변경",
                "  - exit, quit - 프로그램 종료",
                "  - help, 도움말 - 이 도움말 표시"
            ]
        
        # 종료
        elif user_input in ['exit', 'quit', '종료', 'bye']:
            return ["프로그램을 종료합니다."]
        
        # 기본 응답
        else:
            return [
                f"🤔 명령을 이해하지 못했습니다: '{user_input}'",
                "💡 'help' 또는 '도움말'을 입력하여 사용 가능한 명령을 확인하세요."
            ]

def print_banner():
    """프로그램 시작 배너"""
    print("=" * 60)
    print(" === MCP 파일시스템 채팅 클라이언트 ===")
    print("=" * 60)
    print("💬 자연어로 파일 시스템을 제어하세요!")
    print("📁 현재 작업 디렉토리에서 파일 복사, 이름 변경 등이 가능합니다.")
    print("❓ 'help' 또는 '도움말'을 입력하면 사용법을 확인할 수 있습니다.")
    print("=" * 60)

async def main():
    """메인 실행 함수"""
    print_banner()
    
    # 작업 디렉토리 설정
    work_dir = input("🎯 작업할 디렉토리 경로를 입력하세요 (엔터시 현재 디렉토리): ").strip()
    if not work_dir:
        work_dir = os.getcwd()
    
    # MCP 클라이언트 초기화
    client = MCPFileSystemClient(work_dir)
    
    print(f"\n🏁 MCP 클라이언트가 시작되었습니다!")
    print(f"📂 작업 디렉토리: {client.current_directory}")
    print("💬 명령을 입력하세요 ('exit'로 종료):\n")
    
    try:
        while True:
            # 사용자 입력 받기
            user_input = input(f"[{os.path.basename(client.current_directory)}] > ").strip()
            
            if not user_input:
                continue
                
            # 명령 처리
            results = client.process_command(user_input)
            
            # 결과 출력
            for result in results:
                print(f"   {result}")
            print()
            
            # 종료 체크
            if user_input.lower() in ['exit', 'quit', '종료', 'bye']:
                break
                
    except KeyboardInterrupt:
        print("\n\n👋 Ctrl+C로 프로그램을 종료합니다.")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
    finally:
        client.stop_mcp_server()
        print("🔚 MCP 서버가 종료되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
