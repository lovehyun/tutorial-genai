"""
이 폴더의 .md 커리큘럼 문서를 PDF 로 내보낸다.
markdown -> HTML -> playwright(headless Chromium) 로 인쇄. 결과 PDF 는 .gitignore(*.pdf, 루트 공통)로 커밋 안 됨.

사용:
  pip install markdown playwright
  playwright install chromium   # 최초 1회

  python build_pdf.py                          # 기본: 1.mcp_practice_4hr.md
  python build_pdf.py 2.mcp_practice_8hr.md     # 다른 파일 지정
"""

import sys
import os
import markdown
from playwright.sync_api import sync_playwright

# Windows 콘솔(cp949)에서도 한글·특수문자 출력이 깨지거나 죽지 않게 UTF-8 로
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))

CSS = """
@page { size: A4; margin: 18mm 15mm; }
body {
  font-family: "Malgun Gothic", "Segoe UI", -apple-system, sans-serif;
  font-size: 10.5pt;
  line-height: 1.55;
  color: #1a1a1a;
}
h1 { font-size: 19pt; border-bottom: 3px solid #2563eb; padding-bottom: 6px; margin-top: 0; }
h2 { font-size: 14pt; color: #1e3a8a; margin-top: 22px; border-bottom: 1px solid #cbd5e1; padding-bottom: 3px; }
h3 {
  font-size: 11.5pt; color: #ffffff; background: #2563eb;
  margin: 18px 0 8px; padding: 6px 10px; border-radius: 3px;
}
table { border-collapse: collapse; width: 100%; margin: 10px 0 16px; font-size: 9pt; }
td, th { word-wrap: break-word; overflow-wrap: break-word; }

/* 3열 시간표(시간|내용|실행할 폴더/파일)만 폭 고정 — 4/5열 표(보너스, 모듈 카탈로그 등)는 auto 유지 */
table:has(> tbody > tr > td:nth-child(3):last-child) { table-layout: fixed; }
table:has(> tbody > tr > td:nth-child(3):last-child) td:nth-child(1),
table:has(> tbody > tr > td:nth-child(3):last-child) th:nth-child(1) { width: 15%; }
table:has(> tbody > tr > td:nth-child(3):last-child) td:nth-child(2),
table:has(> tbody > tr > td:nth-child(3):last-child) th:nth-child(2) { width: 33%; }
table:has(> tbody > tr > td:nth-child(3):last-child) td:nth-child(3),
table:has(> tbody > tr > td:nth-child(3):last-child) th:nth-child(3) { width: 52%; }

/* 4/5열 표(보너스, 모듈 카탈로그)의 짧은 순번/ID 첫 컬럼("5-1", "M16" 등)이 줄바꿈으로
   두 줄 쪼개지는 것 방지 — auto 레이아웃이 그 칸에 너무 좁은 폭을 배정할 때가 있음 */
table:not(:has(> tbody > tr > td:nth-child(3):last-child)) td:nth-child(1),
table:not(:has(> tbody > tr > td:nth-child(3):last-child)) th:nth-child(1) { white-space: nowrap; }
th, td { border: 1px solid #cbd5e1; padding: 5px 7px; text-align: left; vertical-align: top; }
th { background: #eef2ff; font-weight: 600; }
tr:nth-child(even) { background: #f8fafc; }
code { background: #f1f5f9; padding: 1px 4px; border-radius: 3px; font-family: Consolas, monospace; font-size: 9pt; }
pre code { display: block; padding: 8px; overflow-x: auto; }
blockquote { border-left: 3px solid #2563eb; margin: 10px 0; padding: 4px 12px; background: #f8fafc; color: #334155; }
a { color: #2563eb; text-decoration: none; }
hr { border: none; border-top: 1px solid #cbd5e1; margin: 18px 0; }
"""


def build(md_filename: str):
    src = os.path.join(HERE, md_filename)
    if not os.path.exists(src):
        print(f"파일 없음: {src}")
        sys.exit(1)

    text = open(src, encoding="utf-8").read()
    # 시각 구분용 "====...====" 줄은 PDF에선 불필요 → 제거
    text = "\n".join(line for line in text.splitlines() if not line.strip().startswith("===="))

    body_html = markdown.markdown(
        text, extensions=["tables", "fenced_code", "nl2br", "sane_lists"]
    )
    html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body_html}</body></html>"

    out = os.path.splitext(src)[0] + ".pdf"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        page.pdf(path=out, print_background=True)
        browser.close()

    print(f"생성됨: {out}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "1.mcp_practice_4hr.md"
    build(target)
