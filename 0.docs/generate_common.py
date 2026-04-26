"""
PDF 생성 공통 모듈
- CSS 스타일, Mermaid 설정, Markdown 변환 등 공유 코드
- generate_pdf.py 와 generate_pdf_book.py 에서 import하여 사용
"""

import re

try:
    import markdown
except ImportError:
    markdown = None


# ─────────────────────────────────────────────
# CSS 스타일 (공통)
# ─────────────────────────────────────────────

BASE_CSS = """
@page {
    size: A4;
    margin: 25mm 20mm 30mm 20mm;
}

body {
    font-family: 'Noto Sans CJK KR', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #2d3436;
    max-width: 100%;
    margin: 0;
    padding: 0;
}

h1 {
    font-size: 24pt;
    color: #2d3436;
    border-bottom: 3px solid #6c5ce7;
    padding-bottom: 10px;
    margin-top: 0;
}

h2 {
    font-size: 16pt;
    color: #2d3436;
    border-bottom: 2px solid #dfe6e9;
    padding-bottom: 6px;
    margin-top: 30px;
    page-break-after: avoid;
}

h3 {
    font-size: 13pt;
    color: #636e72;
    margin-top: 20px;
    page-break-after: avoid;
}

h4 {
    font-size: 11pt;
    color: #636e72;
    margin-top: 15px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

th {
    background-color: #6c5ce7;
    color: white;
    padding: 8px 10px;
    text-align: left;
    font-weight: 600;
}

td {
    padding: 7px 10px;
    border-bottom: 1px solid #dfe6e9;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}

code {
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 9pt;
    background-color: #f1f2f6;
    padding: 2px 5px;
    border-radius: 3px;
}

pre {
    background-color: #2d3436;
    color: #dfe6e9;
    padding: 15px;
    border-radius: 8px;
    overflow-x: auto;
    font-size: 8.5pt;
    line-height: 1.5;
    page-break-inside: avoid;
}

pre code {
    background: none;
    padding: 0;
    color: inherit;
}

blockquote {
    border-left: 4px solid #6c5ce7;
    margin: 15px 0;
    padding: 10px 15px;
    background-color: #f8f7ff;
    font-size: 10pt;
    page-break-inside: avoid;
}

blockquote strong {
    color: #6c5ce7;
}

.mermaid {
    text-align: center;
    margin: 20px 0;
    page-break-inside: avoid;
    break-before: avoid;
    overflow: visible;
}

.mermaid svg {
    max-width: 100%;
    height: auto;
    font-family: 'Noto Sans CJK KR', 'Noto Sans KR', sans-serif;
}

.diagram-group {
    page-break-inside: avoid;
    break-inside: avoid;
}

ul, ol {
    padding-left: 25px;
}

li {
    margin-bottom: 4px;
}

hr {
    border: none;
    border-top: 1px solid #dfe6e9;
    margin: 30px 0;
}

img {
    max-width: 100%;
    height: auto;
}
"""


# ─────────────────────────────────────────────
# Mermaid JS 설정 (공통)
# ─────────────────────────────────────────────

def mermaid_js_block(escaped=False):
    """Mermaid 초기화 JS 반환.

    차트 크기 정책: 기본 사이즈 그대로 유지, 페이지 폭보다 큰 것만 CSS max-width로 축소.
    escaped=True: Python format string용 ({{ }})
    escaped=False: 일반 HTML용 ({ })
    """
    lb = "{{" if escaped else "{"
    rb = "}}" if escaped else "}"

    return f"""<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({lb}
    startOnLoad: true,
    theme: 'default',
    themeVariables: {lb}
      fontSize: '13px',
      fontFamily: "'Noto Sans CJK KR', 'Noto Sans KR', sans-serif"
    {rb},
    flowchart: {lb}
      htmlLabels: true,
      padding: 20,
      useMaxWidth: false,
      nodeSpacing: 30,
      rankSpacing: 40,
      wrappingWidth: 200
    {rb},
    sequence: {lb}
      useMaxWidth: false
    {rb},
    er: {lb}
      useMaxWidth: false
    {rb},
    pie: {lb}
      useMaxWidth: false
    {rb}
  {rb});
</script>"""


# ─────────────────────────────────────────────
# Markdown 변환 유틸리티 (공통)
# ─────────────────────────────────────────────

def convert_mermaid_blocks(md_text: str) -> str:
    """```mermaid 블록을 <div class="mermaid"> 태그로 변환"""
    def replace_mermaid(match):
        code = match.group(1).strip()
        return f'<div class="mermaid">\n{code}\n</div>'

    pattern = r'```mermaid\n(.*?)```'
    return re.sub(pattern, replace_mermaid, md_text, flags=re.DOTALL)


def get_title_from_md(md_text: str) -> str:
    """마크다운 첫 번째 # 제목 추출"""
    for line in md_text.split('\n'):
        if line.startswith('# '):
            return line[2:].strip()
    return "Untitled"


def get_first_paragraph(md_text: str) -> str:
    """마크다운 첫 번째 > 블록쿼트(부제목) 추출"""
    for line in md_text.split('\n'):
        if line.startswith('> '):
            text = line[2:].strip()
            if len(text) > 120:
                text = text[:117] + "..."
            return text
    return ""


MD_EXTENSIONS = ['tables', 'fenced_code', 'codehilite', 'toc', 'nl2br']
MD_EXTENSION_CONFIGS = {
    'codehilite': {'css_class': 'highlight', 'guess_lang': False},
}


def md_to_html_content(md_text: str) -> str:
    """마크다운을 HTML 콘텐츠로 변환 (head/body 없이)"""
    if markdown is None:
        raise ImportError("'markdown' 패키지가 필요합니다. pip install markdown pymdown-extensions")

    md_text = convert_mermaid_blocks(md_text)

    return markdown.markdown(
        md_text,
        extensions=MD_EXTENSIONS,
        extension_configs=MD_EXTENSION_CONFIGS,
    )


# ─────────────────────────────────────────────
# 모듈 정보 (공통)
# ─────────────────────────────────────────────

MODULE_INFO = {
    "00_OT": {
        "title": "오리엔테이션",
        "subtitle": "개발 환경 설정과 과정 소개",
    },
    "01_genai_intro": {
        "title": "생성형 AI 입문",
        "subtitle": "생성형 AI의 기초 개념과 활용",
    },
    "02_web_basics": {
        "title": "웹 기초",
        "subtitle": "HTML, CSS, JavaScript와 웹 아키텍처",
    },
    "03_python_webdev": {
        "title": "Python 웹 개발",
        "subtitle": "Python 기초부터 FastAPI까지",
    },
    "04_database": {
        "title": "데이터베이스",
        "subtitle": "RDBMS, NoSQL, 벡터 데이터베이스",
    },
    "05_genai_advanced": {
        "title": "생성형 AI 심화",
        "subtitle": "LLM API, RAG, LangChain, 에이전트",
    },
    "06_genai_applied": {
        "title": "생성형 AI 응용",
        "subtitle": "실전 AI 서비스 설계와 구현",
    },
    "07_cloud": {
        "title": "클라우드",
        "subtitle": "AWS 인프라와 배포 아키텍처",
    },
    "08_team_project": {
        "title": "팀 프로젝트",
        "subtitle": "프로젝트 관리, 협업, CI/CD",
    },
}

MODULE_DISPLAY_NAMES = {
    "00_OT": "OT",
    "01_genai_intro": "01. GenAI 입문",
    "02_web_basics": "02. 웹 기초",
    "03_python_webdev": "03. Python 웹개발",
    "04_database": "04. 데이터베이스",
    "05_genai_advanced": "05. GenAI 심화",
    "06_genai_applied": "06. GenAI 응용",
    "07_cloud": "07. 클라우드",
    "08_team_project": "08. 팀 프로젝트",
}

DEFAULT_COURSE_NAME = "2026 생성형 AI 에이전틱 웹 서비스 개발자 양성과정"
