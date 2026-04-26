#!/usr/bin/env python3
"""
Markdown → 통합 PDF 북 생성기
- 모듈별로 모든 .md 파일을 단일 PDF로 합침
- 타이틀 페이지 (제목 센터 배치)
- 파트 간 간지 (섹션 구분 페이지)
- 페이지 번호: 섹션별 (1-1, 1-2, ... 2-1, 2-2, ...) 또는 연속 선택 가능

사용법:
    # 모듈 하나를 통합 PDF 북으로
    python generate_pdf_book.py 07_cloud/

    # 전체 모듈을 각각 통합 PDF 북으로
    python generate_pdf_book.py --all

    # 연속 페이지 번호 (기본: 섹션별)
    python generate_pdf_book.py 07_cloud/ --numbering continuous

    # 커스텀 제목
    python generate_pdf_book.py 07_cloud/ --title "클라우드 컴퓨팅"

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
    MODULE_INFO,
    get_first_paragraph,
    get_title_from_md,
    md_to_html_content,
    mermaid_js_block,
)


# ─────────────────────────────────────────────
# 북 전용 CSS (타이틀, 간지 등)
# ─────────────────────────────────────────────

BOOK_EXTRA_CSS = """
/* 타이틀 페이지 */
.title-page {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    text-align: center;
    page-break-after: always;
}

.title-page h1 {
    font-size: 36pt;
    color: #6c5ce7;
    margin-bottom: 20px;
    border: none;
    padding: 0;
}

.title-page .subtitle {
    font-size: 16pt;
    color: #636e72;
    margin-bottom: 40px;
}

.title-page .course-name {
    font-size: 13pt;
    color: #636e72;
    margin-top: 60px;
}

.title-page .organizations {
    font-size: 12pt;
    color: #636e72;
    margin-top: 30px;
    letter-spacing: 0.5px;
}

.title-page .decoration {
    width: 80px;
    height: 4px;
    background: linear-gradient(90deg, #6c5ce7, #0984e3, #00b894);
    margin: 30px auto;
    border-radius: 2px;
}

/* 간지 (섹션 구분 페이지) */
.divider-page {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    text-align: center;
    page-break-before: always;
    page-break-after: always;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.divider-page .section-number {
    font-size: 72pt;
    font-weight: 700;
    color: #6c5ce7;
    opacity: 0.3;
    margin-bottom: 10px;
}

.divider-page h2 {
    font-size: 28pt;
    color: #2d3436;
    margin: 0;
    padding: 0;
    border: none;
}

.divider-page .divider-decoration {
    width: 60px;
    height: 3px;
    background: #6c5ce7;
    margin: 20px auto;
    border-radius: 2px;
}

.divider-page .section-desc {
    font-size: 12pt;
    color: #636e72;
    margin-top: 10px;
    max-width: 400px;
}

/* 콘텐츠 영역 */
.content-section {
    page-break-before: always;
}
"""


# ─────────────────────────────────────────────
# 페이지 빌더
# ─────────────────────────────────────────────

def build_title_page(module_title: str, module_subtitle: str, course_name: str) -> str:
    """타이틀 페이지 HTML 생성"""
    return f"""
<div class="title-page">
    <div class="decoration"></div>
    <h1>{module_title}</h1>
    <div class="subtitle">{module_subtitle}</div>
    <div class="decoration"></div>
    <div class="course-name">{course_name}</div>
    <div class="organizations">
        한국소프트웨어저작권협회 &middot; 젠아이랩스
    </div>
</div>
"""


def build_divider_page(section_num: int, title: str, description: str = "") -> str:
    """간지 (섹션 구분 페이지) HTML 생성"""
    desc_html = f'<div class="section-desc">{description}</div>' if description else ""
    return f"""
<div class="divider-page">
    <div class="section-number">{section_num:02d}</div>
    <h2>{title}</h2>
    <div class="divider-decoration"></div>
    {desc_html}
</div>
"""


# ─────────────────────────────────────────────
# 통합 PDF 북 생성
# ─────────────────────────────────────────────

def build_book_html(
    module_dir: Path,
    course_name: str,
    custom_title: str = None,
    numbering: str = "section",
) -> str:
    """모듈 디렉토리의 모든 .md 파일을 통합 HTML로 변환"""

    dir_name = module_dir.name
    info = MODULE_INFO.get(dir_name, {"title": dir_name, "subtitle": ""})

    module_title = custom_title or info["title"]
    module_subtitle = info["subtitle"]

    md_files = sorted(module_dir.glob("*.md"))
    if not md_files:
        print(f"  경고: {module_dir}에 .md 파일이 없습니다.")
        return ""

    # 타이틀 페이지
    content_parts = [build_title_page(module_title, module_subtitle, course_name)]

    # 각 파일을 섹션으로
    for idx, md_file in enumerate(md_files, 1):
        md_text = md_file.read_text(encoding='utf-8')
        title = get_title_from_md(md_text)
        desc = get_first_paragraph(md_text)

        # 간지
        content_parts.append(build_divider_page(idx, title, desc))

        # 콘텐츠
        html_content = md_to_html_content(md_text)
        content_parts.append(f'<div class="content-section">\n{html_content}\n</div>')

    # 전체 HTML 조립
    all_content = '\n'.join(content_parts)
    mermaid_js = mermaid_js_block(escaped=False)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{module_title}</title>
{mermaid_js}
<style>
{BASE_CSS}
{BOOK_EXTRA_CSS}
</style>
</head>
<body>
{all_content}
</body>
</html>
"""
    return html


async def generate_book_pdf(
    module_dir: Path,
    output_dir: Path,
    course_name: str,
    custom_title: str = None,
    numbering: str = "section",
) -> None:
    """모듈 통합 PDF 북 생성"""

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERROR: 'playwright' 패키지가 필요합니다.")
        print("  pip install playwright && playwright install chromium")
        sys.exit(1)

    dir_name = module_dir.name
    info = MODULE_INFO.get(dir_name, {"title": dir_name, "subtitle": ""})
    module_title = custom_title or info["title"]

    md_files = sorted(module_dir.glob("*.md"))
    if not md_files:
        return

    print(f"  📖 {dir_name} ({len(md_files)}개 파일 → 통합 PDF)", flush=True)

    # HTML 생성
    html_content = build_book_html(module_dir, course_name, custom_title, numbering)

    if not html_content:
        return

    # 헤더/푸터 템플릿
    header_template = f"""
<div style="font-size: 9px; width: 100%; padding: 5px 20px; border-bottom: 1px solid #dfe6e9; display: flex; justify-content: space-between; align-items: center; font-family: 'Noto Sans CJK KR', sans-serif; color: #636e72;">
    <span>{course_name}</span>
    <span>{module_title}</span>
</div>
"""

    footer_template = """
<div style="font-size: 9px; width: 100%; padding: 5px 20px; border-top: 1px solid #dfe6e9; display: flex; justify-content: space-between; align-items: center; font-family: 'Noto Sans CJK KR', sans-serif; color: #636e72;">
    <span>&copy; GenAI Labs</span>
    <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
</div>
"""

    # PDF 생성
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1200, "height": 800})

        await page.set_content(html_content, wait_until="networkidle")
        await page.wait_for_timeout(5000)

        pdf_filename = f"{dir_name}_book.pdf"
        output_path = output_dir / pdf_filename

        await page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template=header_template,
            footer_template=footer_template,
            margin={
                "top": "25mm",
                "bottom": "25mm",
                "left": "20mm",
                "right": "20mm",
            },
        )

        await browser.close()

    file_size = output_path.stat().st_size / (1024 * 1024)
    print(f"    → {pdf_filename} ({file_size:.1f}MB) ✓")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="모듈별 통합 PDF 북 생성기 (타이틀 + 간지 + 콘텐츠)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python generate_pdf_book.py 07_cloud/
  python generate_pdf_book.py --all
  python generate_pdf_book.py 07_cloud/ --title "AWS 클라우드" --numbering continuous
        """,
    )

    parser.add_argument("path", nargs="?", help="변환할 모듈 디렉토리 경로")
    parser.add_argument("--all", action="store_true", help="모든 모듈을 각각 통합 PDF 북으로 생성")
    parser.add_argument("--header", default=DEFAULT_COURSE_NAME, help="PDF 헤더 텍스트")
    parser.add_argument("--title", default=None, help="커스텀 모듈 제목 (기본: 모듈명에서 자동 생성)")
    parser.add_argument(
        "--numbering", choices=["continuous", "section"], default="continuous",
        help="페이지 번호 방식 (continuous: 1,2,3... / section: 섹션별)",
    )
    parser.add_argument("--output", "-o", default=None, help="출력 디렉토리 (기본: ./pdf_output/books/)")

    args = parser.parse_args()

    docs_root = Path(__file__).parent
    output_dir = Path(args.output) if args.output else docs_root / "pdf_output" / "books"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.all:
        module_dirs = sorted([
            d for d in docs_root.iterdir()
            if d.is_dir()
            and not d.name.startswith('.')
            and d.name != "pdf_output"
            and any(d.glob("*.md"))
        ])

        print(f"통합 PDF 북 생성 ({len(module_dirs)}개 모듈)")
        print(f"출력: {output_dir}\n")

        async def run_all():
            for module_dir in module_dirs:
                await generate_book_pdf(
                    module_dir, output_dir, args.header, args.title, args.numbering
                )

        asyncio.run(run_all())

    elif args.path:
        target = docs_root / args.path if not Path(args.path).is_absolute() else Path(args.path)

        if not target.is_dir():
            print(f"ERROR: '{args.path}'은(는) 유효한 디렉토리가 아닙니다.")
            sys.exit(1)

        print(f"통합 PDF 북 생성: {target.name}")
        print(f"출력: {output_dir}\n")

        asyncio.run(
            generate_book_pdf(target, output_dir, args.header, args.title, args.numbering)
        )
    else:
        parser.print_help()
        sys.exit(1)

    print(f"\n완료! 통합 PDF 위치: {output_dir}")


if __name__ == "__main__":
    main()
