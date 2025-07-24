#!/usr/bin/env python3
"""
자연어 파일 관리 챗봇
OpenAI API를 사용하여 자연어 명령을 파일 시스템 작업으로 변환
"""

import os
import shutil
import glob
import json
import re
from typing import List, Dict, Any
import subprocess

# .env 파일 로드 (선택사항)
try:
    from dotenv import load_dotenv
    load_dotenv()
    HAS_DOTENV = True
    print("✓ python-dotenv 라이브러리 로드됨")
except ImportError:
    HAS_DOTENV = False
    print("⚠ python-dotenv 라이브러리 없음 (선택사항)")

try:
    from openai import OpenAI
    HAS_OPENAI = True
    print("✓ OpenAI 라이브러리 로드됨")
except ImportError:
    HAS_OPENAI = False
    print("⚠ OpenAI 라이브러리 없음 (AI 모드 비활성화)")

class FileSystemTools:
    """파일 시스템 작업 도구들"""
    
    def __init__(self, base_directory: str = None):
        self.base_directory = base_directory or os.getcwd()
        self.current_directory = self.base_directory
        
    def list_files(self, directory: str = None, pattern: str = "*") -> List[str]:
        """파일 목록 조회"""
        target_dir = directory or self.current_directory
        try:
            items = []
            for item in sorted(os.listdir(target_dir)):
                if pattern == "*" or pattern.lower() in item.lower():
                    item_path = os.path.join(target_dir, item)
                    if os.path.isfile(item_path):
                        size = os.path.getsize(item_path)
                        items.append(f"파일: {item} ({size:,} bytes)")
                    else:
                        items.append(f"폴더: {item}/")
            return items
        except Exception as e:
            return [f"오류: {str(e)}"]
    
    def copy_file(self, source: str, destination: str) -> str:
        """파일 복사"""
        try:
            src_path = os.path.join(self.current_directory, source)
            dst_path = os.path.join(self.current_directory, destination)
            
            if not os.path.exists(src_path):
                return f"원본 파일을 찾을 수 없습니다: {source}"
            
            shutil.copy2(src_path, dst_path)
            return f"파일 복사 완료: {source} -> {destination}"
        except Exception as e:
            return f"복사 실패: {str(e)}"
    
    def move_file(self, source: str, destination: str) -> str:
        """파일 이동"""
        try:
            src_path = os.path.join(self.current_directory, source)
            dst_path = os.path.join(self.current_directory, destination)
            
            if not os.path.exists(src_path):
                return f"원본 파일을 찾을 수 없습니다: {source}"
            
            shutil.move(src_path, dst_path)
            return f"파일 이동 완료: {source} -> {destination}"
        except Exception as e:
            return f"이동 실패: {str(e)}"
    
    def delete_file(self, filename: str) -> str:
        """파일 삭제"""
        try:
            file_path = os.path.join(self.current_directory, filename)
            if not os.path.exists(file_path):
                return f"파일을 찾을 수 없습니다: {filename}"
            
            if os.path.isfile(file_path):
                os.remove(file_path)
                return f"파일 삭제 완료: {filename}"
            else:
                shutil.rmtree(file_path)
                return f"폴더 삭제 완료: {filename}"
        except Exception as e:
            return f"삭제 실패: {str(e)}"
    
    def create_directory(self, dirname: str) -> str:
        """디렉토리 생성"""
        try:
            dir_path = os.path.join(self.current_directory, dirname)
            os.makedirs(dir_path, exist_ok=True)
            return f"폴더 생성 완료: {dirname}"
        except Exception as e:
            return f"폴더 생성 실패: {str(e)}"
    
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
                return f"디렉토리 변경: {new_path}"
            else:
                return f"디렉토리를 찾을 수 없습니다: {path}"
        except Exception as e:
            return f"디렉토리 변경 실패: {str(e)}"
    
    def search_files(self, pattern: str) -> List[str]:
        """파일 검색"""
        try:
            results = []
            search_pattern = os.path.join(self.current_directory, f"**/*{pattern}*")
            for file_path in glob.glob(search_pattern, recursive=True):
                rel_path = os.path.relpath(file_path, self.current_directory)
                if os.path.isfile(file_path):
                    results.append(f"파일: {rel_path}")
                else:
                    results.append(f"폴더: {rel_path}/")
            return results if results else [f"'{pattern}'과 일치하는 파일/폴더가 없습니다"]
        except Exception as e:
            return [f"검색 실패: {str(e)}"]
    
    def batch_copy(self, source_pattern: str, name_template: str, start: int, end: int) -> List[str]:
        """배치 복사 (주차별 등)"""
        results = []
        matching_files = glob.glob(os.path.join(self.current_directory, source_pattern))
        
        if not matching_files:
            return [f"패턴에 맞는 파일이 없습니다: {source_pattern}"]
        
        for source_file in matching_files:
            filename = os.path.basename(source_file)
            results.append(f"원본 파일: {filename}")
            
            for i in range(start, end + 1):
                new_name = name_template.format(week=i, num=i)
                new_name = filename.replace("1주차", f"{i}주차") if "주차" in filename else new_name
                
                result = self.copy_file(filename, new_name)
                results.append(f"  {result}")
        
        return results

class NaturalLanguageFileManager:
    """자연어 파일 관리 시스템"""
    
    def __init__(self, openai_api_key: str = None, base_directory: str = None):
        self.file_tools = FileSystemTools(base_directory)
        self.openai_api_key = openai_api_key
        
        if HAS_OPENAI and openai_api_key:
            try:
                self.client = OpenAI(api_key=openai_api_key)
                self.use_ai = True
                print("✓ OpenAI AI 모드 활성화됨")
            except Exception as e:
                self.client = None
                self.use_ai = False
                print(f"✗ OpenAI 클라이언트 초기화 실패: {e}")
        else:
            self.client = None
            self.use_ai = False
            if not HAS_OPENAI:
                print("ℹ OpenAI 라이브러리가 없어 기본 패턴 매칭 모드로 실행됩니다")
            elif not openai_api_key:
                print("ℹ API 키가 없어 기본 패턴 매칭 모드로 실행됩니다")
    
    def parse_command_with_ai(self, user_input: str) -> Dict[str, Any]:
        """OpenAI를 사용한 자연어 명령 파싱"""
        system_prompt = """
당신은 자연어 명령을 파일 시스템 작업으로 변환하는 AI입니다.
사용자의 명령을 분석하여 JSON 형태로만 응답하세요. 다른 설명은 하지 마세요.

가능한 작업:
- list_files: 파일 목록 조회
- copy_file: 파일 복사 (source, destination 필요)
- move_file: 파일 이동 (source, destination 필요)
- delete_file: 파일 삭제 (filename 필요)
- create_directory: 폴더 생성 (dirname 필요)
- change_directory: 디렉토리 변경 (path 필요)
- search_files: 파일 검색 (pattern 필요)
- batch_copy: 배치 복사 (source_pattern, start, end 필요)
- help: 도움말 표시

응답은 반드시 이 JSON 형태로만 하세요:
{
  "action": "작업명",
  "parameters": {
    "param1": "값1"
  }
}

예시:
사용자: "파일 목록 보여줘" -> {"action": "list_files", "parameters": {}}
사용자: "hwp 파일 찾아줘" -> {"action": "search_files", "parameters": {"pattern": "hwp"}}
사용자: "뭘 할 수 있어?" -> {"action": "help", "parameters": {}}
"""
        
        try:
            print(f"[AI 요청] {user_input}")
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            print(f"[AI 응답] {content}")
            
            # JSON 파싱 시도
            try:
                result = json.loads(content)
                print(f"[파싱 성공] {result}")
                return result
            except json.JSONDecodeError:
                # JSON이 아닌 경우, 텍스트에서 JSON 추출 시도
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    print(f"[JSON 추출 시도] {json_str}")
                    result = json.loads(json_str)
                    print(f"[추출 성공] {result}")
                    return result
                else:
                    print(f"[JSON 추출 실패] 응답에서 JSON을 찾을 수 없음")
                    return {"action": "error", "message": f"AI가 JSON 형태로 응답하지 않음: {content}"}
                    
        except json.JSONDecodeError as e:
            print(f"[JSON 파싱 에러] {str(e)}")
            return {"action": "error", "message": f"JSON 파싱 실패: {str(e)}"}
        except Exception as e:
            print(f"[AI 호출 에러] {str(e)}")
            return {"action": "error", "message": f"AI 파싱 실패: {str(e)}"}
    
    def parse_command_basic(self, user_input: str) -> Dict[str, Any]:
        """기본 패턴 매칭을 사용한 명령 파싱"""
        user_input = user_input.lower().strip()
        
        # 파일 목록
        if any(word in user_input for word in ['목록', 'list', 'ls', '파일', '폴더']):
            return {"action": "list_files", "parameters": {}}
        
        # 디렉토리 변경
        elif user_input.startswith(('cd ', '이동 ', '가자 ', '들어가')):
            path_match = re.search(r'(?:cd|이동|가자|들어가)\s+(.+)', user_input)
            path = path_match.group(1) if path_match else ''
            return {"action": "change_directory", "parameters": {"path": path}}
        
        # 파일 복사
        elif any(word in user_input for word in ['복사', 'copy']):
            if '주차' in user_input:
                return {"action": "batch_copy", "parameters": {"source_pattern": "*1주차*", "start": 2, "end": 12}}
            else:
                return {"action": "copy_file", "parameters": {"source": "", "destination": ""}}
        
        # 파일 검색
        elif any(word in user_input for word in ['찾', 'search', '검색']):
            pattern_match = re.search(r'(?:찾|search|검색).*?([^\s]+)', user_input)
            pattern = pattern_match.group(1) if pattern_match else ''
            return {"action": "search_files", "parameters": {"pattern": pattern}}
        
        # 폴더 생성
        elif any(word in user_input for word in ['폴더', '디렉토리', 'mkdir']) and any(word in user_input for word in ['만들', '생성', 'create']):
            name_match = re.search(r'(?:폴더|디렉토리)\s*([^\s]+)', user_input)
            name = name_match.group(1) if name_match else ''
            return {"action": "create_directory", "parameters": {"dirname": name}}
        
        # 파일 삭제
        elif any(word in user_input for word in ['삭제', 'delete', 'remove', 'rm']):
            file_match = re.search(r'(?:삭제|delete|remove|rm)\s+(.+)', user_input)
            filename = file_match.group(1) if file_match else ''
            return {"action": "delete_file", "parameters": {"filename": filename}}
        
        else:
            return {"action": "unknown", "message": "명령을 이해하지 못했습니다."}
    
    def execute_command(self, command_dict: Dict[str, Any]) -> List[str]:
        """명령 실행"""
        action = command_dict.get("action")
        params = command_dict.get("parameters", {})
        
        if action == "list_files":
            return self.file_tools.list_files(params.get("directory"), params.get("pattern", "*"))
        
        elif action == "copy_file":
            source = params.get("source", "")
            destination = params.get("destination", "")
            if not source or not destination:
                return ["복사할 원본 파일과 대상 파일명을 지정해주세요."]
            return [self.file_tools.copy_file(source, destination)]
        
        elif action == "move_file":
            source = params.get("source", "")
            destination = params.get("destination", "")
            return [self.file_tools.move_file(source, destination)]
        
        elif action == "delete_file":
            filename = params.get("filename", "")
            if not filename:
                return ["삭제할 파일명을 지정해주세요."]
            return [self.file_tools.delete_file(filename)]
        
        elif action == "create_directory":
            dirname = params.get("dirname", "")
            if not dirname:
                return ["생성할 폴더명을 지정해주세요."]
            return [self.file_tools.create_directory(dirname)]
        
        elif action == "change_directory":
            path = params.get("path", "")
            if not path:
                return ["이동할 경로를 지정해주세요."]
            return [self.file_tools.change_directory(path)]
        
        elif action == "search_files":
            pattern = params.get("pattern", "")
            if not pattern:
                return ["검색할 패턴을 지정해주세요."]
            return self.file_tools.search_files(pattern)
        
        elif action == "batch_copy":
            return self.file_tools.batch_copy(
                params.get("source_pattern", "*1주차*"),
                params.get("name_template", "{week}주차"),
                params.get("start", 2),
                params.get("end", 12)
            )
        
        elif action == "help":
            return [
                "파일 관리 챗봇에서 할 수 있는 작업:",
                "- 파일 목록: '파일 목록', '현재 폴더에 뭐가 있어?'",
                "- 파일 검색: 'hwp 파일 찾아줘', '보고서 검색'",
                "- 파일 복사: 'A.txt를 B.txt로 복사해', '1주차 파일을 12주차까지 복사'",
                "- 폴더 이동: '상위 폴더로 가자', 'Documents로 이동'",
                "- 폴더 생성: 'backup 폴더 만들어줘'",
                "- 파일 삭제: 'temp.txt 삭제해줘'"
            ]
        
        else:
            return [command_dict.get("message", "알 수 없는 명령입니다.")]
    
    def process_input(self, user_input: str) -> List[str]:
        """사용자 입력 처리"""
        print(f"\n[명령 처리 시작] '{user_input}'")
        
        if self.use_ai:
            print("[모드] AI 모드로 처리 중...")
            command_dict = self.parse_command_with_ai(user_input)
        else:
            print("[모드] 기본 패턴 매칭으로 처리 중...")
            command_dict = self.parse_command_basic(user_input)
        
        print(f"[명령 해석] {command_dict}")
        
        results = self.execute_command(command_dict)
        print(f"[실행 완료] {len(results)}개 결과")
        
        return results

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("자연어 파일 관리 챗봇")
    print("=" * 60)
    
    # 라이브러리 상태 표시
    print("\n[라이브러리 상태]")
    print(f"python-dotenv: {'✓ 사용가능' if HAS_DOTENV else '✗ 미설치'}")
    print(f"OpenAI: {'✓ 사용가능' if HAS_OPENAI else '✗ 미설치'}")
    
    # API 키 확인
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"OpenAI API 키: ✓ 환경변수에서 발견 (sk-...{api_key[-4:]})")
    else:
        print("OpenAI API 키: ✗ 환경변수에 없음")
    
    # API 키 설정 (선택사항)
    if not api_key and HAS_OPENAI:
        user_key = input("\nOpenAI API 키를 입력하세요 (선택사항, 엔터시 기본 모드): ").strip()
        if user_key:
            api_key = user_key
    
    # 작업 디렉토리 설정
    work_dir = input("작업할 디렉토리 경로 (엔터시 현재 디렉토리): ").strip()
    if not work_dir:
        work_dir = os.getcwd()
    
    print(f"\n[초기화 중...]")
    # 파일 매니저 초기화
    manager = NaturalLanguageFileManager(api_key, work_dir)
    
    print(f"\n시작됨. 작업 디렉토리: {manager.file_tools.current_directory}")
    print(f"모드: {'AI 모드' if manager.use_ai else '기본 패턴 매칭 모드'}")
    print("자연어로 명령하세요. 종료하려면 'exit' 입력\n")
    
    while True:
        try:
            current_dir = os.path.basename(manager.file_tools.current_directory)
            user_input = input(f"[{current_dir}] > ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', '종료', 'bye']:
                print("프로그램을 종료합니다.")
                break
            
            # 명령 처리
            results = manager.process_input(user_input)
            
            # 결과 출력
            for result in results:
                print(f"  {result}")
            print()
            
        except KeyboardInterrupt:
            print("\n\nCtrl+C로 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"오류: {str(e)}")

if __name__ == "__main__":
    main()
