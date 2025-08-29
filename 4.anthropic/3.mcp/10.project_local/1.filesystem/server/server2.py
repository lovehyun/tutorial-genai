# filesystem_server.py - 파일 시스템 접근 MCP 서버

import os
from pathlib import Path
from typing import List, Dict, Any
import mimetypes
import shutil
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# 작업 디렉토리 설정 (보안을 위해 특정 폴더로 제한)
WORKING_DIR = Path("./workspace")  # 현재 디렉토리의 workspace 폴더
WORKING_DIR.mkdir(exist_ok=True)   # 폴더가 없으면 생성

mcp = FastMCP("FileSystemServer")

def get_safe_path(relative_path: str) -> Path:
    """안전한 경로 반환 (디렉토리 탈출 방지)"""
    # 상대 경로를 절대 경로로 변환하고 WORKING_DIR 내부인지 확인
    try:
        full_path = (WORKING_DIR / relative_path).resolve()
        WORKING_DIR.resolve()  # 기준 디렉토리
        
        # WORKING_DIR 내부인지 확인
        if not str(full_path).startswith(str(WORKING_DIR.resolve())):
            raise ValueError("디렉토리 탈출 시도가 감지되었습니다")
        
        return full_path
    except Exception as e:
        raise ValueError(f"잘못된 경로입니다: {e}")

@mcp.tool()
def list_files(directory: str = ".") -> List[Dict[str, Any]]:
    """디렉토리의 파일 목록을 조회합니다."""
    try:
        target_dir = get_safe_path(directory)
        
        if not target_dir.exists():
            return {"error": f"디렉토리가 존재하지 않습니다: {directory}"}
        
        if not target_dir.is_dir():
            return {"error": f"파일입니다. 디렉토리가 아닙니다: {directory}"}
        
        files = []
        for item in target_dir.iterdir():
            try:
                stat = item.stat()
                file_info = {
                    "name": item.name,
                    "path": str(item.relative_to(WORKING_DIR)),
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "readable": os.access(item, os.R_OK),
                    "writable": os.access(item, os.W_OK)
                }
                
                if item.is_file():
                    file_info["mime_type"] = mimetypes.guess_type(item)[0]
                
                files.append(file_info)
            except Exception as e:
                files.append({
                    "name": item.name,
                    "error": f"정보를 읽을 수 없습니다: {e}"
                })
        
        return {
            "directory": directory,
            "absolute_path": str(target_dir),
            "file_count": len([f for f in files if f.get("type") == "file"]),
            "directory_count": len([f for f in files if f.get("type") == "directory"]),
            "files": sorted(files, key=lambda x: (x.get("type", ""), x.get("name", "")))
        }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def read_file(file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """파일 내용을 읽어옵니다."""
    try:
        target_file = get_safe_path(file_path)
        
        if not target_file.exists():
            return {"error": f"파일이 존재하지 않습니다: {file_path}"}
        
        if not target_file.is_file():
            return {"error": f"디렉토리입니다. 파일이 아닙니다: {file_path}"}
        
        # 파일 크기 체크 (10MB 제한)
        file_size = target_file.stat().st_size
        if file_size > 10 * 1024 * 1024:  # 10MB
            return {"error": f"파일이 너무 큽니다 (10MB 초과): {file_size} bytes"}
        
        # 텍스트 파일인지 확인
        mime_type = mimetypes.guess_type(target_file)[0]
        if mime_type and not mime_type.startswith('text/'):
            # 바이너리 파일은 기본 정보만 반환
            return {
                "file_path": file_path,
                "file_type": "binary",
                "mime_type": mime_type,
                "size": file_size,
                "message": "바이너리 파일입니다. 내용을 읽을 수 없습니다."
            }
        
        # 텍스트 파일 읽기
        try:
            content = target_file.read_text(encoding=encoding)
            return {
                "file_path": file_path,
                "file_type": "text",
                "mime_type": mime_type,
                "size": file_size,
                "encoding": encoding,
                "line_count": len(content.splitlines()),
                "content": content
            }
        except UnicodeDecodeError:
            # 인코딩 오류 시 다른 인코딩 시도
            for alt_encoding in ['cp949', 'euc-kr', 'latin1']:
                try:
                    content = target_file.read_text(encoding=alt_encoding)
                    return {
                        "file_path": file_path,
                        "file_type": "text",
                        "size": file_size,
                        "encoding": alt_encoding,
                        "line_count": len(content.splitlines()),
                        "content": content,
                        "note": f"원래 인코딩({encoding})으로 읽기 실패, {alt_encoding}으로 읽음"
                    }
                except UnicodeDecodeError:
                    continue
            
            return {"error": f"텍스트 파일을 읽을 수 없습니다. 인코딩 문제: {file_path}"}
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def write_file(file_path: str, content: str, encoding: str = "utf-8", overwrite: bool = False) -> Dict[str, Any]:
    """파일에 내용을 씁니다."""
    try:
        target_file = get_safe_path(file_path)
        
        # 파일이 이미 존재하고 overwrite=False인 경우
        if target_file.exists() and not overwrite:
            return {"error": f"파일이 이미 존재합니다. overwrite=true로 설정하세요: {file_path}"}
        
        # 디렉토리 생성 (필요한 경우)
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 파일 쓰기
        target_file.write_text(content, encoding=encoding)
        
        # 결과 확인
        file_size = target_file.stat().st_size
        return {
            "file_path": file_path,
            "size": file_size,
            "encoding": encoding,
            "line_count": len(content.splitlines()),
            "message": "파일이 성공적으로 저장되었습니다."
        }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_directory(directory_path: str) -> Dict[str, Any]:
    """새 디렉토리를 생성합니다."""
    try:
        target_dir = get_safe_path(directory_path)
        
        if target_dir.exists():
            return {"error": f"디렉토리가 이미 존재합니다: {directory_path}"}
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        return {
            "directory_path": directory_path,
            "absolute_path": str(target_dir),
            "message": "디렉토리가 성공적으로 생성되었습니다."
        }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_file(file_path: str, force: bool = False) -> Dict[str, Any]:
    """파일을 삭제합니다."""
    try:
        target_path = get_safe_path(file_path)
        
        if not target_path.exists():
            return {"error": f"파일/디렉토리가 존재하지 않습니다: {file_path}"}
        
        if target_path.is_file():
            target_path.unlink()
            return {
                "file_path": file_path,
                "type": "file",
                "message": "파일이 성공적으로 삭제되었습니다."
            }
        elif target_path.is_dir():
            if not force:
                return {"error": f"디렉토리를 삭제하려면 force=true를 설정하세요: {file_path}"}
            
            shutil.rmtree(target_path)
            return {
                "directory_path": file_path,
                "type": "directory",
                "message": "디렉토리가 성공적으로 삭제되었습니다."
            }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def copy_file(source_path: str, destination_path: str, overwrite: bool = False) -> Dict[str, Any]:
    """파일을 복사합니다."""
    try:
        source = get_safe_path(source_path)
        destination = get_safe_path(destination_path)
        
        if not source.exists():
            return {"error": f"원본 파일이 존재하지 않습니다: {source_path}"}
        
        if destination.exists() and not overwrite:
            return {"error": f"대상 파일이 이미 존재합니다. overwrite=true로 설정하세요: {destination_path}"}
        
        # 디렉토리 생성 (필요한 경우)
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        if source.is_file():
            shutil.copy2(source, destination)
            return {
                "source_path": source_path,
                "destination_path": destination_path,
                "type": "file",
                "size": destination.stat().st_size,
                "message": "파일이 성공적으로 복사되었습니다."
            }
        elif source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=overwrite)
            return {
                "source_path": source_path,
                "destination_path": destination_path,
                "type": "directory",
                "message": "디렉토리가 성공적으로 복사되었습니다."
            }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def move_file(source_path: str, destination_path: str, overwrite: bool = False) -> Dict[str, Any]:
    """파일/디렉토리를 이동합니다."""
    try:
        source = get_safe_path(source_path)
        destination = get_safe_path(destination_path)
        
        if not source.exists():
            return {"error": f"원본이 존재하지 않습니다: {source_path}"}
        
        if destination.exists() and not overwrite:
            return {"error": f"대상이 이미 존재합니다. overwrite=true로 설정하세요: {destination_path}"}
        
        # 디렉토리 생성 (필요한 경우)
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # 기존 대상 파일 삭제 (overwrite=True인 경우)
        if destination.exists() and overwrite:
            if destination.is_file():
                destination.unlink()
            else:
                shutil.rmtree(destination)
        
        shutil.move(str(source), str(destination))
        
        return {
            "source_path": source_path,
            "destination_path": destination_path,
            "message": "성공적으로 이동되었습니다."
        }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def search_files(pattern: str, directory: str = ".", file_type: str = "all") -> List[Dict[str, Any]]:
    """파일을 검색합니다."""
    try:
        target_dir = get_safe_path(directory)
        
        if not target_dir.exists() or not target_dir.is_dir():
            return {"error": f"디렉토리가 존재하지 않습니다: {directory}"}
        
        results = []
        
        # 재귀적으로 파일 검색
        for item in target_dir.rglob(pattern):
            try:
                if file_type == "files" and not item.is_file():
                    continue
                elif file_type == "directories" and not item.is_dir():
                    continue
                
                stat = item.stat()
                result = {
                    "name": item.name,
                    "path": str(item.relative_to(WORKING_DIR)),
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
                
                if item.is_file():
                    result["mime_type"] = mimetypes.guess_type(item)[0]
                
                results.append(result)
                
            except Exception as e:
                results.append({
                    "name": item.name if hasattr(item, 'name') else str(item),
                    "error": f"정보를 읽을 수 없습니다: {e}"
                })
        
        return {
            "pattern": pattern,
            "directory": directory,
            "file_type": file_type,
            "found_count": len(results),
            "results": sorted(results, key=lambda x: x.get("path", ""))
        }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_file_info(file_path: str) -> Dict[str, Any]:
    """파일/디렉토리의 상세 정보를 조회합니다."""
    try:
        target_path = get_safe_path(file_path)
        
        if not target_path.exists():
            return {"error": f"파일/디렉토리가 존재하지 않습니다: {file_path}"}
        
        stat = target_path.stat()
        
        info = {
            "path": file_path,
            "absolute_path": str(target_path),
            "name": target_path.name,
            "type": "directory" if target_path.is_dir() else "file",
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "permissions": {
                "readable": os.access(target_path, os.R_OK),
                "writable": os.access(target_path, os.W_OK),
                "executable": os.access(target_path, os.X_OK)
            }
        }
        
        if target_path.is_file():
            info["mime_type"] = mimetypes.guess_type(target_path)[0]
            
            # 텍스트 파일인 경우 추가 정보
            mime_type = info["mime_type"]
            if mime_type and mime_type.startswith('text/'):
                try:
                    content = target_path.read_text(encoding='utf-8')
                    info["line_count"] = len(content.splitlines())
                    info["character_count"] = len(content)
                    info["encoding"] = "utf-8"
                except UnicodeDecodeError:
                    info["encoding"] = "unknown"
        
        elif target_path.is_dir():
            # 디렉토리인 경우 내용물 개수
            try:
                items = list(target_path.iterdir())
                info["item_count"] = len(items)
                info["file_count"] = len([item for item in items if item.is_file()])
                info["directory_count"] = len([item for item in items if item.is_dir()])
            except PermissionError:
                info["item_count"] = "권한 없음"
        
        return info
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(f"파일 시스템 MCP 서버 시작...")
    print(f"작업 디렉토리: {WORKING_DIR.absolute()}")
    print(f"사용 가능한 도구:")
    print(f"  - list_files: 디렉토리 내용 조회")
    print(f"  - read_file: 파일 읽기")
    print(f"  - write_file: 파일 쓰기")
    print(f"  - create_directory: 디렉토리 생성")
    print(f"  - delete_file: 파일/디렉토리 삭제")
    print(f"  - copy_file: 파일/디렉토리 복사")
    print(f"  - move_file: 파일/디렉토리 이동")
    print(f"  - search_files: 파일 검색")
    print(f"  - get_file_info: 파일 정보 조회")
    
    mcp.run()
    