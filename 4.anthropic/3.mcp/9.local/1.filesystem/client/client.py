import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

async def main():
    # MCP 서버 연결
    server_params = StdioServerParameters(command="python", args=["server/server.py"])
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("파일 관리 MCP 클라이언트")
            print("=" * 40)
            
            while True:
                print("\n명령어:")
                print("1. 파일 목록")
                print("2. 파일 읽기") 
                print("3. 파일명 변경")
                print("4. 파일 복사")
                print("5. 종료")
                
                choice = input("\n선택: ").strip()
                
                if choice == "1":
                    # 파일 목록
                    result = await session.call_tool("list_files")
                    data = json.loads(result.content[0].text)
                    
                    print(f"\n파일 목록 ({data['count']}개)")
                    print("-" * 30)
                    for file in data['files']:
                        size = f"({file['size']} bytes)" if file['size'] else ""
                        print(f"{file['type']}: {file['name']} {size}")
                
                elif choice == "2":
                    # 파일 읽기
                    filename = input("파일명: ")
                    result = await session.call_tool("read_file", {"filename": filename})
                    data = json.loads(result.content[0].text)
                    
                    if "error" in data:
                        print(f"오류: {data['error']}")
                    else:
                        print(f"\n{data['filename']} 내용:")
                        print("-" * 30)
                        print(data['content'])
                
                elif choice == "3":
                    # 파일명 변경
                    old_name = input("현재 파일명: ")
                    new_name = input("새 파일명: ")
                    result = await session.call_tool("rename_file", {
                        "old_name": old_name, 
                        "new_name": new_name
                    })
                    data = json.loads(result.content[0].text)
                    
                    if "error" in data:
                        print(f"오류: {data['error']}")
                    else:
                        print(f"완료: {data['message']}")
                
                elif choice == "4":
                    # 파일 복사
                    source = input("원본 파일명: ")
                    destination = input("복사할 파일명: ")
                    result = await session.call_tool("copy_file", {
                        "source": source,
                        "destination": destination
                    })
                    data = json.loads(result.content[0].text)
                    
                    if "error" in data:
                        print(f"오류: {data['error']}")
                    else:
                        print(f"완료: {data['message']}")
                
                elif choice == "5":
                    print("종료합니다")
                    break
                
                else:
                    print("잘못된 선택입니다")

if __name__ == "__main__":
    asyncio.run(main())
