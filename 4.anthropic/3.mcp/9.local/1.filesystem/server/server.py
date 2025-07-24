from mcp.server.fastmcp import FastMCP
import os
import shutil
from pathlib import Path

# 작업 디렉토리 설정
WORK_DIR = Path("./workspace")
WORK_DIR.mkdir(exist_ok=True)

mcp = FastMCP("FileManager")

@mcp.tool()
def list_files() -> dict:
    """파일 목록을 조회합니다."""
    files = []
    for item in WORK_DIR.iterdir():
        files.append({
            "name": item.name,
            "type": "파일" if item.is_file() else "폴더",
            "size": item.stat().st_size if item.is_file() else None
        })
    return {"files": files, "count": len(files)}

@mcp.tool()
def read_file(filename: str) -> dict:
    """파일 내용을 읽습니다."""
    file_path = WORK_DIR / filename
    
    if not file_path.exists():
        return {"error": "파일이 없습니다"}
    
    try:
        content = file_path.read_text(encoding='utf-8')
        return {"filename": filename, "content": content}
    except:
        return {"error": "파일을 읽을 수 없습니다"}

@mcp.tool()
def rename_file(old_name: str, new_name: str) -> dict:
    """파일명을 변경합니다."""
    old_path = WORK_DIR / old_name
    new_path = WORK_DIR / new_name
    
    if not old_path.exists():
        return {"error": "원본 파일이 없습니다"}
    
    if new_path.exists():
        return {"error": "새 파일명이 이미 존재합니다"}
    
    old_path.rename(new_path)
    return {"message": f"{old_name} → {new_name} 변경 완료"}

@mcp.tool()
def copy_file(source: str, destination: str) -> dict:
    """파일을 복사합니다."""
    src_path = WORK_DIR / source
    dst_path = WORK_DIR / destination
    
    if not src_path.exists():
        return {"error": "원본 파일이 없습니다"}
    
    if dst_path.exists():
        return {"error": "대상 파일이 이미 존재합니다"}
    
    shutil.copy2(src_path, dst_path)
    return {"message": f"{source} → {destination} 복사 완료"}

if __name__ == "__main__":
    print("파일 관리 MCP 서버 시작")
    print(f"작업 폴더: {WORK_DIR.absolute()}")
    mcp.run()
