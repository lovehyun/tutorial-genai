#!/usr/bin/env python3
"""
Markdown → PDF 핸드아웃 생성기
- Mermaid 다이어그램을 시각화하여 PDF에 포함
- 커스텀 헤더/푸터 (copyright GenAI Labs + 페이지 번호)
- 한국어 폰트 지원 (Noto Sans CJK)

사용법:
    # 단일 파일 변환
    python generate_pdf.py 07_cloud/01_cloud_computing_fundamentals.md

    # 모듈 전체 변환
    python generate_pdf.py 07_cloud/

    # 전체 변환
    python generate_pdf.py --all

    # 커스텀 헤더
    python generate_pdf.py 07_cloud/ --header "2026 생성형 AI 에이전틱 웹 서비스 개발자 양성과정"

    # 출력 디렉토리 지정
    python generate_pdf.py 07_cloud/ --output ./pdf_output

필요 패키지:
    pip install playwright markdown pymdown-extensions
    playwright install chromium
"""

import argparse
import asyncio
import sys
from pathlib import Path

from generate_common import (
    BASE_CSS,
    DEFAULT_COURSE_NAME,
    MODULE_DISPLAY_NAMES,
    get_title_from_md,
    md_to_html_content,
    mermaid_js_block,
)


# ─────────────────────────────────────────────
# HTML 템플릿
# ─────────────────────────────────────────────

def build_single_html(md_text: str, title: str) -> str:
    """마크다운 텍스트를 완전한 HTML 문서로 변환"""
    content = md_to_html_content(md_text)
    mermaid_js = mermaid_js_block(escaped=False)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{title}</title>
{mermaid_js}
<style>
{BASE_CSS}

h1 {{
    page-break-before: avoid;
}}

h2 {{
    page-break-before: auto;
}}
</style>
</head>
<body>
{content}
</body>
</html>
"""


HEADER_TEMPLATE = """
<div style="font-size: 9px; width: 100%; padding: 5px 20px; border-bottom: 1px solid #dfe6e9; display: flex; justify-content: space-between; align-items: center; font-family: 'Noto Sans CJK KR', sans-serif; color: #636e72;">
    <span>{header_left}</span>
    <span>{header_right}</span>
</div>
"""

FOOTER_TEMPLATE = """
<div style="font-size: 9px; width: 100%; padding: 5px 20px; border-top: 1px solid #dfe6e9; display: flex; justify-content: space-between; align-items: center; font-family: 'Noto Sans CJK KR', sans-serif; color: #636e72;">
    <span>&copy; GenAI Labs</span>
    <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
</div>
"""


# ─────────────────────────────────────────────
# PDF 생성 (Playwright)
# ─────────────────────────────────────────────

async def html_to_pdf(
    html_content: str,
    output_path: Path,
    header_left: str = "생성형 AI 풀스택 개발 과정",
    header_right: str = "",
) -> None:
    """HTML을 PDF로 변환 (Playwright Chromium 사용)"""

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERROR: 'playwright' 패키지가 필요합니다.")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1200, "height": 800})

        await page.set_content(html_content, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        header_html = HEADER_TEMPLATE.format(
            header_left=header_left,
            header_right=header_right,
        )

        await page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template=header_html,
            footer_template=FOOTER_TEMPLATE,
            margin={
                "top": "25mm",
                "bottom": "25mm",
                "left": "20mm",
                "right": "20mm",
            },
        )

        await browser.close()


# ─────────────────────────────────────────────
# 파일 처리
# ─────────────────────────────────────────────

async def process_file(
    md_path: Path,
    output_dir: Path,
    header: str,
) -> None:
    """단일 마크다운 파일을 PDF로 변환"""

    print(f"  변환 중: {md_path.name}", end="", flush=True)

    md_text = md_path.read_text(encoding="utf-8")
    title = get_title_from_md(md_text)

    module_dir = md_path.parent
    header_right = MODULE_DISPLAY_NAMES.get(module_dir.name, module_dir.name)

    html_content = build_single_html(md_text, title=title)

    pdf_filename = md_path.stem + ".pdf"
    output_path = output_dir / pdf_filename

    await html_to_pdf(
        html_content=html_content,
        output_path=output_path,
        header_left=header,
        header_right=header_right,
    )

    print(f" → {output_path.name} ✓")


async def process_directory(
    dir_path: Path,
    output_dir: Path,
    header: str,
) -> None:
    """디렉토리 내 모든 .md 파일을 PDF로 변환"""

    md_files = sorted(dir_path.glob("*.md"))

    if not md_files:
        print(f"  경고: {dir_path}에 .md 파일이 없습니다.")
        return

    module_output = output_dir / dir_path.name
    module_output.mkdir(parents=True, exist_ok=True)

    print(f"\n📁 {dir_path.name} ({len(md_files)}개 파일)")

    for md_file in md_files:
        await process_file(md_file, module_output, header)


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Markdown → PDF 핸드아웃 생성기 (Mermaid 다이어그램 포함)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python generate_pdf.py 07_cloud/01_cloud_computing_fundamentals.md
  python generate_pdf.py 07_cloud/
  python generate_pdf.py --all
  python generate_pdf.py 07_cloud/ --header "AI 개발 과정" --output ./handouts
        """,
    )

    parser.add_argument("path", nargs="?", help="변환할 .md 파일 또는 모듈 디렉토리 경로")
    parser.add_argument("--all", action="store_true", help="모든 모듈 디렉토리를 변환")
    parser.add_argument("--header", default=DEFAULT_COURSE_NAME, help="PDF 헤더에 표시할 텍스트")
    parser.add_argument("--output", "-o", default=None, help="PDF 출력 디렉토리 (기본: ./pdf_output)")

    args = parser.parse_args()

    docs_root = Path(__file__).parent
    output_dir = Path(args.output) if args.output else docs_root / "pdf_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.all:
        module_dirs = sorted([
            d for d in docs_root.iterdir()
            if d.is_dir() and not d.name.startswith('.') and d.name != "pdf_output"
        ])

        print(f"전체 변환 시작 ({len(module_dirs)}개 모듈)")
        print(f"출력 디렉토리: {output_dir}")

        async def run_all():
            for module_dir in module_dirs:
                await process_directory(module_dir, output_dir, args.header)

        asyncio.run(run_all())

    elif args.path:
        target = docs_root / args.path if not Path(args.path).is_absolute() else Path(args.path)

        if target.is_file() and target.suffix == ".md":
            print(f"단일 파일 변환: {target.name}")
            print(f"출력 디렉토리: {output_dir}")
            asyncio.run(process_file(target, output_dir, args.header))

        elif target.is_dir():
            print(f"모듈 변환: {target.name}")
            print(f"출력 디렉토리: {output_dir}")
            asyncio.run(process_directory(target, output_dir, args.header))

        else:
            print(f"ERROR: '{args.path}'은(는) 유효한 .md 파일 또는 디렉토리가 아닙니다.")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    print(f"\n완료! PDF 파일 위치: {output_dir}")


if __name__ == "__main__":
    main()
