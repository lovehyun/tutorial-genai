# pip install mcp pymupdf docx2pdf
# docx 변환은 Windows + Word 설치 시에만 실제 동작(없으면 docx는 건너뜀)
#
# C:\devs\anaconda3\envs\py312_gpt\python.exe  C:\src\git\...file_converter_server.py
#
# MCP 애플리케이션 등록 설정파일
# - C:\Users\loveh\AppData\Roaming\Claude\claude_desktop_config.json
#
#    "file-converter": {
#      "command": "C:\\devs\\anaconda3\\envs\\py312_gpt\\python.exe",
#      "args": [
#        "C:\\src\\git\\lovehyun\\...(중략)...\\file_converter_server.py"
#      ],
#      "cwd": "C:\\src\\git\\lovehyun\\...(중략)"
#    }
# 
# MCP 애플리케이션 로그 확인   
# - C:\Users\loveh\AppData\Roaming\Claude\logs
"""
MCP 서버 (최신 FastMCP 스타일)
- Downloads 폴더의 PDF/TXT 파일에서 키워드 검색
- 옵션 convert_docx=True → DOCX를 PDF로 변환(CONVERTED/ 폴더 저장)
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP

# MCP 서버 인스턴스 생성 (이름은 "file-converter")
mcp = FastMCP("file-converter")

# === 유틸 함수들 ===

def downloads() -> Path:
    """기본 검색 경로: 사용자 홈의 Downloads 폴더"""
    return Path.home() / "Downloads"

def converted_dir(src: Path) -> Path:
    """CONVERTED 폴더 경로를 만들고 리턴"""
    out = src.parent / "CONVERTED"
    out.mkdir(exist_ok=True)
    return out

def read_pdf(path: Path) -> str:
    """PDF 텍스트 추출 (암호 / 보호 / 손상 PDF는 건너뜀)"""
    try:
        import fitz  # PyMuPDF
        with fitz.open(str(path)) as doc:
            # 암호 걸린 문서는 패스
            if getattr(doc, "needs_pass", False) or getattr(doc, "is_encrypted", False):
                return ""
            texts = []
            for page in doc:
                try:
                    texts.append(page.get_text("text") or "")
                except Exception:
                    # 특정 페이지 추출 실패는 스킵
                    pass
            return "\n".join(texts)
    except Exception:
        # 손상 / 비표준 PDF 등도 스킵
        return ""

def read_txt(path: Path) -> str:
    """TXT 파일 읽기 (UTF-8 기준, 실패 시 일부 무시)"""
    return path.read_text(encoding="utf-8", errors="ignore")

def try_convert_docx(path: Path) -> Optional[Path]:
    """
    DOCX → PDF 변환 시도
    - 변환 성공 시 CONVERTED/폴더에 저장 후 PDF 경로 리턴
    - 실패하면 None
    """
    if path.suffix.lower() != ".docx":
        return None
    try:
        from docx2pdf import convert
    except ImportError:
        return None
    out_pdf = converted_dir(path) / (path.stem + ".pdf")
    if out_pdf.exists():
        return out_pdf
    try:
        convert(str(path))              # Word 설치 필요
        made = path.with_suffix(".pdf") # 변환된 파일 (같은 폴더)
        if made.exists():
            made.replace(out_pdf)       # CONVERTED/로 이동
            return out_pdf
    except Exception:
        pass
    return None

def snippets(text: str, keyword: str, context: int = 50) -> List[str]:
    """본문에서 keyword 주변 문자열 추출 (앞뒤 50자)"""
    low, key = text.lower(), keyword.lower()
    res, i = [], 0
    while True:
        i = low.find(key, i)
        if i == -1:
            break
        s, e = max(0, i - context), min(len(text), i + len(keyword) + context)
        res.append(text[s:e].replace("\n", " "))
        if len(res) >= 3:   # 파일당 최대 3개 스니펫
            break
        i += len(keyword)
    return res

# === MCP Tool 정의 ===
@mcp.tool()
def find(query: str,
         root_dir: Optional[str] = None,
         convert_docx: bool = False,
         max_results: int = 10) -> Dict[str, Any]:
    """
    키워드 검색 툴
    - query: 검색어
    - root_dir: 검색 시작 폴더 (없으면 Downloads)
    - convert_docx: True면 DOCX → PDF 변환 후 검색
    - max_results: 반환할 최대 파일 수
    """
    base = Path(root_dir or downloads())
    results = []
    for p in base.rglob("*"):
        if not p.is_file():
            continue

        ext = p.suffix.lower()

        # DOCX → PDF 변환 처리
        if convert_docx and ext == ".docx":
            pdf = try_convert_docx(p)
            if pdf:
                p, ext = pdf, ".pdf"

        # PDF/TXT만 처리
        if ext not in {".pdf", ".txt"}:
            continue

        # 본문 읽기 & 스니펫 추출
        try:
            text = read_pdf(p) if ext == ".pdf" else read_txt(p)
            hits = snippets(text, query)
        except Exception:
            # 개별 파일 오류는 무시하고 계속
            hits = []
            
        if hits:
            results.append({"path": str(p), "snippets": hits})
            if len(results) >= max_results:
                break

    return {"ok": True, "hits": len(results), "results": results}

# === MCP 서버 실행 ===
if __name__ == "__main__":
    mcp.run()
