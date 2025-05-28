#!/usr/bin/env python3
"""
간단한 MCP 파일 서버 - 직접 호출 방식
윈도우/리눅스 등 다양한 환경에서 동작
"""

import asyncio
import json
import os
import sys
import io
import yaml
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
import aiofiles
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 강제로 stdout 인코딩을 utf-8로 설정
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

class SimpleFileServer:
    def __init__(self):
        # 환경변수 다시 로드 (여러 번 시도)
        load_dotenv()
        
        # 환경변수에서 경로 읽기 (기본값도 함께)
        exam_dir = os.getenv('EXAM_DIRECTORY')
        config_file = os.getenv('EXAM_CONFIG_PATH')
        
        # 환경변수가 없으면 기본값 사용
        if not exam_dir:
            exam_dir = './answers'
        if not config_file:
            config_file = './exam_config.yaml'
            
        self.base_directory = Path(exam_dir)
        self.config_path = Path(config_file)
        
        # 상대경로인 경우 현재 디렉토리 기준으로 변경
        if not self.base_directory.is_absolute():
            self.base_directory = Path.cwd() / self.base_directory
        if not self.config_path.is_absolute():
            self.config_path = Path.cwd() / self.config_path
        
        # 디렉토리 생성 (없으면)
        self.base_directory.mkdir(parents=True, exist_ok=True)
    
    async def read_exam_config(self) -> Dict[str, Any]:
        """시험 설정 파일 읽기"""
        try:
            if not self.config_path.exists():
                return {"error": f"설정 파일이 존재하지 않습니다: {self.config_path}"}
            
            async with aiofiles.open(self.config_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                config = yaml.safe_load(content)
                return {
                    "success": True,
                    "config": config,
                    "config_path": str(self.config_path)
                }
        except Exception as e:
            return {"error": f"설정 파일 읽기 오류: {e}"}
    
    async def list_answer_files(self, pattern: str = "*.txt") -> Dict[str, Any]:
        """답안 파일 목록 조회"""
        try:
            # 디렉토리 존재 확인
            if not self.base_directory.exists():
                return {
                    "error": f"답안 디렉토리가 존재하지 않습니다: {self.base_directory}",
                    "directory": str(self.base_directory),
                    "working_dir": str(Path.cwd())
                }
            
            files = list(self.base_directory.glob(pattern))
            file_info = []
            
            for file_path in files:
                stat = file_path.stat()
                file_info.append({
                    "filename": file_path.name,
                    "full_path": str(file_path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
            
            # 추가 디버그 정보
            all_files = list(self.base_directory.iterdir()) if self.base_directory.exists() else []
            txt_files_direct = [f for f in all_files if f.name.endswith('.txt')]
            
            return {
                "success": True,
                "files": file_info,
                "total_count": len(file_info),
                "directory": str(self.base_directory),
                "directory_exists": self.base_directory.exists(),
                "all_files_in_directory": [f.name for f in all_files],
                "txt_files_direct": [f.name for f in txt_files_direct],
                "pattern_used": pattern,
                "glob_result_count": len(files),
                "env_exam_directory": os.getenv('EXAM_DIRECTORY'),
                "current_working_dir": str(Path.cwd())
            }
        except Exception as e:
            return {"error": f"파일 목록 조회 오류: {e}"}
    
    async def read_answer_file(self, filename: str) -> Dict[str, Any]:
        """특정 답안 파일 읽기"""
        try:
            file_path = self.base_directory / filename
            
            if not file_path.exists():
                return {"error": f"파일이 존재하지 않습니다: {filename}"}
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                
            return {
                "success": True,
                "filename": filename,
                "content": content,
                "size": len(content),
                "full_path": str(file_path)
            }
        except Exception as e:
            return {"error": f"파일 읽기 오류: {e}"}
    
    async def save_grading_result(self, results: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """채점 결과 저장"""
        try:
            output_path = self.base_directory / filename

            # 문자열인 경우 파이썬 dict로 안전하게 변환
            if isinstance(results, str):
                try:
                    results = ast.literal_eval(results)  # 안전한 문자열 → dict 변환
                except Exception as eval_err:
                    return {"error": f"문자열을 dict로 변환 중 오류: {eval_err}"}

            # JSON으로 저장 (한글 포함, 들여쓰기 포함)
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(results, ensure_ascii=False, indent=2))
                
            return {
                "success": True,
                "saved_to": str(output_path),
                "filename": filename
            }
        except Exception as e:
            return {"error": f"결과 저장 오류: {e}"}
    
    async def get_system_info(self) -> Dict[str, Any]:
        """시스템 정보 조회"""
        import platform
        
        # 실제 파일 확인
        txt_files = []
        all_files = []
        try:
            if self.base_directory.exists():
                txt_files = [f.name for f in self.base_directory.glob("*.txt")]
                all_files = [f.name for f in self.base_directory.iterdir()]
        except Exception as e:
            txt_files = [f"오류: {e}"]
            all_files = [f"오류: {e}"]
        
        return {
            "success": True,
            "system": {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "python_version": sys.version,
                "working_directory": str(Path.cwd()),
                "exam_directory": str(self.base_directory),
                "exam_directory_exists": self.base_directory.exists(),
                "config_path": str(self.config_path),
                "config_exists": self.config_path.exists(),
                "env_exam_directory": os.getenv('EXAM_DIRECTORY'),
                "env_config_path": os.getenv('EXAM_CONFIG_PATH'),
                "actual_txt_files": txt_files,
                "actual_all_files": all_files
            }
        }
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """도구 호출 처리"""
        try:
            if tool_name == "read_exam_config":
                return await self.read_exam_config()
            elif tool_name == "list_answer_files":
                pattern = arguments.get("pattern", "*.txt")
                return await self.list_answer_files(pattern)
            elif tool_name == "read_answer_file":
                filename = arguments["filename"]
                return await self.read_answer_file(filename)
            elif tool_name == "save_grading_result":
                results = arguments["results"]
                filename = arguments.get("filename", "grading_results.json")
                return await self.save_grading_result(results, filename)
            elif tool_name == "get_system_info":
                return await self.get_system_info()
            else:
                return {"error": f"알 수 없는 도구: {tool_name}"}
        except Exception as e:
            return {"error": f"도구 실행 오류: {e}"}

async def main():
    """메인 함수 - 명령행 인수 우선 처리"""
    # 환경변수 다시 로드
    load_dotenv()
    
    server = SimpleFileServer()
    
    try:
        # 명령행 인수가 있으면 우선 처리
        if len(sys.argv) > 1:
            tool_name = sys.argv[1]
            arguments = {}
            
            # 추가 인수들을 arguments로 파싱
            for i in range(2, len(sys.argv), 2):
                if i + 1 < len(sys.argv):
                    key = sys.argv[i].lstrip('--')
                    value = sys.argv[i + 1]
                    arguments[key] = value
            
            result = await server.handle_tool_call(tool_name, arguments)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        
        # stdin에서 입력 읽기 (타임아웃 설정)
        try:
            # 비동기적으로 stdin 읽기 시도
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, sys.stdin.read)
            
            try:
                input_data = await asyncio.wait_for(future, timeout=1.0)
                input_data = input_data.strip()
            except asyncio.TimeoutError:
                print(json.dumps({"error": "입력 타임아웃"}, ensure_ascii=False))
                return
            
            if not input_data:
                print(json.dumps({"error": "입력이 없습니다"}, ensure_ascii=False))
                return
                
        except Exception as e:
            print(json.dumps({"error": f"입력 읽기 오류: {e}"}, ensure_ascii=False))
            return
        
        # JSON-RPC 요청 파싱
        try:
            request = json.loads(input_data)
            tool_name = request["params"]["name"]
            arguments = request["params"]["arguments"]
            
            result = await server.handle_tool_call(tool_name, arguments)
            
            # JSON-RPC 응답 형식
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
                }
            }
            
            print(json.dumps(response, ensure_ascii=False))
            
        except json.JSONDecodeError:
            print(json.dumps({"error": "잘못된 JSON 형식"}, ensure_ascii=False))
            
    except Exception as e:
        error_response = {"error": f"서버 오류: {e}"}
        print(json.dumps(error_response, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())

# 답안 파일 목록 조회
# python file_server.py list_answer_files --pattern *.txt

# 특정 답안 파일 읽기
# python file_server.py read_answer_file --filename file001.txt

# 시험 설정 yaml 파일 읽기
# python file_server.py read_exam_config
