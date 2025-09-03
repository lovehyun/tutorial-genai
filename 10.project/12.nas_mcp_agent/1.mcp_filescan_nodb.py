# mcp_filescan_no_db.py
# pip install mcp chardet python-dotenv

import os, sys, fnmatch, json
import chardet
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()
ROOT = Path(os.getenv("SCAN_ROOT", r"Z:\\")).resolve()  # Z: 드라이브 기본

mcp = FastMCP("NAS-NoDB-Scanner")

ALLOWED_EXT = { "pdf","docx","doc","xlsx","xls","pptx","ppt",
                "txt","md","csv","json","yaml","yml","html","htm","rtf",
                "odt","ods","odp" }
TEXT_LIKE = { "txt","md","csv","json","yaml","yml","html","htm","rtf" }

def _iter_files(base: Path, max_items: int = 10000, ext_filter=None, name_glob=None):
    n = 0
    for p in base.rglob("*"):
        try:
            if not p.is_file(): 
                continue
            ext = p.suffix.lower().lstrip(".")
            if ext_filter and ext not in ext_filter: 
                continue
            if name_glob and not fnmatch.fnmatch(p.name, name_glob): 
                continue
            stat = p.stat()
            yield {
                "path": str(p),
                "name": p.name,
                "ext": ext,
                "size": stat.st_size,
                "mtime": stat.st_mtime,
            }
            n += 1
            if n >= max_items:
                break
        except Exception:
            continue

def _head_text(path: Path, max_bytes=512_000, n=40):
    try:
        data = path.read_bytes()[:max_bytes]
        enc = (chardet.detect(data).get("encoding") or "utf-8").lower()
        text = data.decode(enc, errors="ignore")
        return "\n".join(text.splitlines()[:max(1, n)])
    except Exception as e:
        return f"(미리보기 실패: {e})"

@mcp.tool()
def scan(dir: str = "", limit: int = 2000, types: str = "pdf,docx,md,txt", name_glob: str = "") -> str:
    """
    Z: 기준으로 하위 파일을 즉시 풀스캔(무DB)하여 나열합니다.
    - dir: ROOT 하위 경로. 예: '팀문서/보고서'
    - limit: 최대 나열 개수(기본 2000)
    - types: 쉼표구분 확장자 필터(비우면 전체)
    - name_glob: 와일드카드. 예: '*보고서*.pdf'
    """
    base = (ROOT / dir).resolve()
    if not str(base).startswith(str(ROOT)) or not base.exists():
        return json.dumps({"error":"경로 없음 또는 ROOT 바깥 접근 불가"}, ensure_ascii=False)
    ext_filter = {t.strip().lstrip(".").lower() for t in types.split(",") if t.strip()} or None
    rows = list(_iter_files(base, max_items=int(limit), ext_filter=ext_filter, name_glob=name_glob or None))
    return json.dumps(rows, ensure_ascii=False)

@mcp.tool()
def head(path: str, n: int = 40) -> str:
    """
    텍스트형 파일 앞부분 미리보기.
    """
    p = Path(path)
    ext = p.suffix.lower().lstrip(".")
    if ext not in TEXT_LIKE:
        return "(텍스트 미리보기를 지원하지 않는 확장자)"
    return _head_text(p, n=n)

if __name__ == "__main__":
    print(f"[start] ROOT={ROOT}")
    mcp.run()
