#!/usr/bin/env python3
"""
파일 서버 테스트 스크립트
"""

import subprocess
import json
import asyncio
import os
from pathlib import Path

async def test_file_server():
    """파일 서버 테스트"""
    print("🧪 파일 서버 테스트 시작")
    
    # 현재 디렉토리 정보 확인
    current_dir = Path.cwd()
    answers_dir = current_dir / "answers"
    
    print(f"📁 현재 디렉토리: {current_dir}")
    print(f"📁 answers 디렉토리: {answers_dir}")
    print(f"📁 answers 존재 여부: {answers_dir.exists()}")
    
    if answers_dir.exists():
        txt_files = list(answers_dir.glob("*.txt"))
        print(f"📄 .txt 파일 수: {len(txt_files)}")
        print(f"📄 파일 목록: {[f.name for f in txt_files]}")
        
        all_files = list(answers_dir.iterdir())
        print(f"📄 전체 파일: {[f.name for f in all_files]}")
    
    # 테스트 케이스들
    test_cases = [
        ("get_system_info", {}),
        ("read_exam_config", {}),
        ("list_answer_files", {"pattern": "*.txt"}),
    ]
    
    # 환경 변수 직접 설정하여 테스트
    test_env = os.environ.copy()
    test_env['EXAM_DIRECTORY'] = str(answers_dir)
    test_env['EXAM_CONFIG_PATH'] = str(current_dir / "exam_config.yaml")
    
    for tool_name, arguments in test_cases:
        print(f"\n📋 테스트: {tool_name}")
        
        try:
            # 명령행 인수 구성
            cmd = ["python", "file_server.py", tool_name]
            for key, value in arguments.items():
                cmd.extend([f"--{key}", str(value)])
            
            print(f"🔧 실행 명령: {' '.join(cmd)}")
            
            # 서버 호출 (환경변수 설정)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=test_env
            )
            
            stdout, stderr = process.communicate(timeout=10)
            
            if stderr:
                print(f"❌ 오류: {stderr}")
            else:
                try:
                    result = json.loads(stdout)
                    if result.get("success"):
                        print(f"✅ 성공: {tool_name}")
                        
                        if tool_name == "list_answer_files":
                            print(f"   📂 디렉토리: {result.get('directory', 'Unknown')}")
                            print(f"   📂 디렉토리 존재: {result.get('directory_exists', 'Unknown')}")
                            print(f"   📄 파일 수: {result.get('total_count', 0)}개")
                            print(f"   📄 전체 파일: {result.get('all_files_in_directory', [])}")
                            print(f"   🔍 패턴: {result.get('pattern_used', 'Unknown')}")
                            
                        elif tool_name == "get_system_info":
                            system = result.get('system', {})
                            print(f"   🖥️  플랫폼: {system.get('platform', 'Unknown')}")
                            print(f"   📁 작업 디렉토리: {system.get('working_directory', 'Unknown')}")
                            print(f"   📁 설정된 답안 디렉토리: {system.get('exam_directory', 'Unknown')}")
                            print(f"   📁 답안 디렉토리 존재: {system.get('exam_directory_exists', 'Unknown')}")
                            print(f"   🔧 환경변수 EXAM_DIRECTORY: {system.get('env_exam_directory', 'None')}")
                            print(f"   📄 실제 txt 파일들: {system.get('actual_txt_files', [])}")
                            print(f"   📄 실제 전체 파일들: {system.get('actual_all_files', [])}")
                            
                        elif tool_name == "read_exam_config":
                            print(f"   📋 설정 파일: {result.get('config_path', 'Unknown')}")
                            
                    else:
                        print(f"⚠️  실패: {result.get('error', '알 수 없는 오류')}")
                        
                except json.JSONDecodeError:
                    print(f"📄 원시 응답: {stdout}")
                    
        except subprocess.TimeoutExpired:
            print(f"⏰ 타임아웃: {tool_name}")
        except Exception as e:
            print(f"❌ 예외: {e}")

if __name__ == "__main__":
    asyncio.run(test_file_server())
