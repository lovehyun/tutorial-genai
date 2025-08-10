# filesystem_client.py - 파일 시스템 MCP 클라이언트

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

class FileSystemMCPClient:
    """파일 시스템 MCP 클라이언트"""
    
    def __init__(self):
        self.session = None
        
    async def connect(self):
        """MCP 서버에 연결"""
        server_params = StdioServerParameters(
            command="python", 
            args=["server/server.py"]
        )
        
        self.server_connection = stdio_client(server_params)
        read, write = await self.server_connection.__aenter__()
        
        self.session = ClientSession(read, write)
        await self.session.__aenter__()
        await self.session.initialize()
        
        print("파일 시스템 MCP 서버에 연결되었습니다.")
        
        # 사용 가능한 도구 목록 조회
        tools = await self.session.list_tools()
        print(f"사용 가능한 도구: {len(tools.tools)}개")
        for tool in tools.tools:
            print(f"  - {tool.name}: {tool.description}")
    
    async def close(self):
        """연결 종료"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if hasattr(self, 'server_connection'):
            await self.server_connection.__aexit__(None, None, None)
    
    async def list_files(self, directory="."):
        """디렉토리 내용 조회"""
        result = await self.session.call_tool("list_files", {"directory": directory})
        return json.loads(result.content[0].text)
    
    async def read_file(self, file_path, encoding="utf-8"):
        """파일 읽기"""
        result = await self.session.call_tool("read_file", {
            "file_path": file_path,
            "encoding": encoding
        })
        return json.loads(result.content[0].text)
    
    async def write_file(self, file_path, content, encoding="utf-8", overwrite=False):
        """파일 쓰기"""
        result = await self.session.call_tool("write_file", {
            "file_path": file_path,
            "content": content,
            "encoding": encoding,
            "overwrite": overwrite
        })
        return json.loads(result.content[0].text)
    
    async def create_directory(self, directory_path):
        """디렉토리 생성"""
        result = await self.session.call_tool("create_directory", {
            "directory_path": directory_path
        })
        return json.loads(result.content[0].text)
    
    async def delete_file(self, file_path, force=False):
        """파일/디렉토리 삭제"""
        result = await self.session.call_tool("delete_file", {
            "file_path": file_path,
            "force": force
        })
        return json.loads(result.content[0].text)
    
    async def search_files(self, pattern, directory=".", file_type="all"):
        """파일 검색"""
        result = await self.session.call_tool("search_files", {
            "pattern": pattern,
            "directory": directory,
            "file_type": file_type
        })
        return json.loads(result.content[0].text)
    
    async def get_file_info(self, file_path):
        """파일 정보 조회"""
        result = await self.session.call_tool("get_file_info", {
            "file_path": file_path
        })
        return json.loads(result.content[0].text)

async def demo():
    """파일 시스템 MCP 데모"""
    client = FileSystemMCPClient()
    
    try:
        await client.connect()
        
        print("\n" + "="*60)
        print("파일 시스템 MCP 데모 시작")
        print("="*60)
        
        # 1. 현재 디렉토리 내용 조회
        print("\n1. 현재 디렉토리 내용 조회:")
        files = await client.list_files(".")
        if "error" in files:
            print(f"오류: {files['error']}")
        else:
            print(f"디렉토리: {files['directory']}")
            print(f"파일 수: {files['file_count']}, 디렉토리 수: {files['directory_count']}")
            for item in files['files'][:5]:  # 처음 5개만 표시
                print(f"  {item['type']}: {item['name']} ({item.get('size', 'N/A')} bytes)")
        
        # 2. 테스트 파일 생성
        print("\n2. 테스트 파일 생성:")
        test_content = """# 테스트 파일
이것은 MCP로 생성된 테스트 파일입니다.
현재 시간: 2025-07-21

## 내용
- 파일 시스템 접근 테스트
- 한글 인코딩 테스트
- 여러 줄 텍스트 테스트
"""
        
        result = await client.write_file("test.md", test_content, overwrite=True)
        if "error" in result:
            print(f"오류: {result['error']}")
        else:
            print(f"파일 생성 성공: {result['message']}")
            print(f"크기: {result['size']} bytes, 줄 수: {result['line_count']}")
        
        # 3. 파일 읽기
        print("\n3. 생성된 파일 읽기:")
        content = await client.read_file("test.md")
        if "error" in content:
            print(f"오류: {content['error']}")
        else:
            print(f"파일 타입: {content['file_type']}")
            print(f"크기: {content['size']} bytes")
            print(f"내용 (처음 200자):")
            print(content['content'][:200] + ("..." if len(content['content']) > 200 else ""))
        
        # 4. 디렉토리 생성
        print("\n4. 새 디렉토리 생성:")
        result = await client.create_directory("test_folder/subfolder")
        if "error" in result:
            print(f"오류: {result['error']}")
        else:
            print(f"디렉토리 생성 성공: {result['message']}")
        
        # 5. 파일을 새 디렉토리로 복사
        print("\n5. 파일을 새 디렉토리로 이동:")
        # 먼저 복사 기능이 있다면 사용하고, 없다면 쓰기로 대체
        try:
            # 파일을 새 위치에 쓰기
            result = await client.write_file("test_folder/copied_test.md", test_content, overwrite=True)
            if "error" in result:
                print(f"오류: {result['error']}")
            else:
                print(f"파일 복사 성공: {result['message']}")
        except Exception as e:
            print(f"복사 실패: {e}")
        
        # 6. 파일 검색
        print("\n6. .md 파일 검색:")
        search_result = await client.search_files("*.md")
        if "error" in search_result:
            print(f"오류: {search_result['error']}")
        else:
            print(f"검색 결과: {search_result['found_count']}개 파일 발견")
            for item in search_result['results']:
                print(f"  {item['path']} ({item.get('size', 'N/A')} bytes)")
        
        # 7. 파일 상세 정보 조회
        print("\n7. 파일 상세 정보:")
        info = await client.get_file_info("test.md")
        if "error" in info:
            print(f"오류: {info['error']}")
        else:
            print(f"파일명: {info['name']}")
            print(f"크기: {info['size']} bytes")
            print(f"수정 시간: {info['modified']}")
            print(f"권한: 읽기({info['permissions']['readable']}), 쓰기({info['permissions']['writable']})")
            if info.get('line_count'):
                print(f"줄 수: {info['line_count']}")
        
        # 8. 최종 디렉토리 상태 확인
        print("\n8. 최종 디렉토리 상태:")
        files = await client.list_files(".")
        if "error" not in files:
            print(f"총 {files['file_count']}개 파일, {files['directory_count']}개 디렉토리")
        
    except Exception as e:
        print(f"데모 실행 중 오류: {e}")
    finally:
        await client.close()

async def interactive_mode():
    """대화형 파일 탐색 모드"""
    client = FileSystemMCPClient()
    
    try:
        await client.connect()
        
        print("\n파일 시스템 대화형 모드")
        print("사용 가능한 명령어:")
        print("  ls [directory] - 디렉토리 내용 조회")
        print("  cat <file> - 파일 내용 보기")
        print("  write <file> <content> - 파일 쓰기")
        print("  mkdir <directory> - 디렉토리 생성")
        print("  rm <file> [force] - 파일/디렉토리 삭제")
        print("  find <pattern> - 파일 검색")
        print("  info <file> - 파일 정보")
        print("  quit - 종료")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\nfs> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                cmd = parts[0].lower()
                
                if cmd == "quit":
                    break
                
                elif cmd == "ls":
                    directory = parts[1] if len(parts) > 1 else "."
                    result = await client.list_files(directory)
                    if "error" in result:
                        print(f"오류: {result['error']}")
                    else:
                        print(f"\n디렉토리: {result['directory']}")
                        print(f"파일: {result['file_count']}개, 디렉토리: {result['directory_count']}개")
                        print("-" * 40)
                        for item in result['files']:
                            type_icon = "📁" if item['type'] == 'directory' else "📄"
                            size_info = f"({item.get('size', 'N/A')} bytes)" if item['type'] == 'file' else ""
                            print(f"{type_icon} {item['name']} {size_info}")
                
                elif cmd == "cat":
                    if len(parts) < 2:
                        print("사용법: cat <파일명>")
                        continue
                    
                    file_path = parts[1]
                    result = await client.read_file(file_path)
                    if "error" in result:
                        print(f"오류: {result['error']}")
                    else:
                        print(f"\n파일: {result['file_path']} ({result['size']} bytes)")
                        print("-" * 40)
                        print(result['content'])
                
                elif cmd == "write":
                    if len(parts) < 3:
                        print("사용법: write <파일명> <내용>")
                        print("여러 줄 입력하려면 'write <파일명> multi'를 사용하세요")
                        continue
                    
                    file_path = parts[1]
                    
                    if parts[2] == "multi":
                        print("여러 줄 입력 모드 (빈 줄로 종료):")
                        lines = []
                        while True:
                            line = input()
                            if line == "":
                                break
                            lines.append(line)
                        content = "\n".join(lines)
                    else:
                        content = " ".join(parts[2:])
                    
                    result = await client.write_file(file_path, content, overwrite=True)
                    if "error" in result:
                        print(f"오류: {result['error']}")
                    else:
                        print(f"파일 저장 완료: {result['message']}")
                
                elif cmd == "mkdir":
                    if len(parts) < 2:
                        print("사용법: mkdir <디렉토리명>")
                        continue
                    
                    directory_path = parts[1]
                    result = await client.create_directory(directory_path)
                    if "error" in result:
                        print(f"오류: {result['error']}")
                    else:
                        print(f"디렉토리 생성 완료: {result['message']}")
                
                elif cmd == "rm":
                    if len(parts) < 2:
                        print("사용법: rm <파일/디렉토리명> [force]")
                        continue
                    
                    file_path = parts[1]
                    force = len(parts) > 2 and parts[2].lower() == "force"
                    
                    result = await client.delete_file(file_path, force=force)
                    if "error" in result:
                        print(f"오류: {result['error']}")
                    else:
                        print(f"삭제 완료: {result['message']}")
                
                elif cmd == "find":
                    if len(parts) < 2:
                        print("사용법: find <패턴>")
                        continue
                    
                    pattern = parts[1]
                    result = await client.search_files(pattern)
                    if "error" in result:
                        print(f"오류: {result['error']}")
                    else:
                        print(f"\n검색 결과: '{pattern}' - {result['found_count']}개 발견")
                        print("-" * 40)
                        for item in result['results']:
                            type_icon = "📁" if item['type'] == 'directory' else "📄"
                            size_info = f"({item.get('size', 'N/A')} bytes)" if item['type'] == 'file' else ""
                            print(f"{type_icon} {item['path']} {size_info}")
                
                elif cmd == "info":
                    if len(parts) < 2:
                        print("사용법: info <파일/디렉토리명>")
                        continue
                    
                    file_path = parts[1]
                    result = await client.get_file_info(file_path)
                    if "error" in result:
                        print(f"오류: {result['error']}")
                    else:
                        print(f"\n파일 정보: {result['name']}")
                        print("-" * 40)
                        print(f"경로: {result['path']}")
                        print(f"타입: {result['type']}")
                        print(f"크기: {result['size']} bytes")
                        print(f"생성: {result['created']}")
                        print(f"수정: {result['modified']}")
                        print(f"접근: {result['accessed']}")
                        print(f"권한: R({result['permissions']['readable']}) W({result['permissions']['writable']}) X({result['permissions']['executable']})")
                        
                        if result.get('line_count'):
                            print(f"줄 수: {result['line_count']}")
                        if result.get('mime_type'):
                            print(f"MIME 타입: {result['mime_type']}")
                        if result.get('item_count') is not None:
                            print(f"포함 항목: {result['item_count']}개")
                
                else:
                    print(f"알 수 없는 명령어: {cmd}")
                    print("도움말을 보려면 사용 가능한 명령어를 참조하세요.")
            
            except KeyboardInterrupt:
                print("\n대화형 모드를 종료합니다.")
                break
            except Exception as e:
                print(f"명령 실행 오류: {e}")
    
    except Exception as e:
        print(f"대화형 모드 오류: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    print("파일 시스템 MCP 클라이언트")
    print("실행 모드를 선택하세요:")
    print("1. 자동 데모")
    print("2. 대화형 파일 탐색")
    
    choice = input("선택 (1/2): ").strip()
    
    if choice == "2":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(demo())
