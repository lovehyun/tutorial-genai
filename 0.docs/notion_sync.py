#!/usr/bin/env python3
"""
Notion 페이지 동기화 도구
- 페이지 목록 조회 / 매핑 생성 / 검색
- update-mermaid: Mermaid 다이어그램만 업데이트
- update: 기존 페이지 전체 내용 교체
- create: 새 페이지 생성

사용법:
    python notion_sync.py list
    python notion_sync.py generate-map
    python notion_sync.py update-mermaid [모듈명]
    python notion_sync.py update [모듈명]
    python notion_sync.py create [모듈명]
    python notion_sync.py search "클라우드"

필요 패키지:
    pip install notion-client python-dotenv
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: 'python-dotenv' 패키지가 필요합니다.")
    print("  pip install python-dotenv")
    sys.exit(1)

try:
    from notion_client import Client
except ImportError:
    print("ERROR: 'notion-client' 패키지가 필요합니다.")
    print("  pip install notion-client")
    sys.exit(1)


DOCS_ROOT = Path(__file__).parent
MAPPING_FILE = DOCS_ROOT / "notion_mapping.json"


# ─────────────────────────────────────────────
# 환경 설정
# ─────────────────────────────────────────────

def load_config() -> dict:
    env_path = DOCS_ROOT / ".env"
    if not env_path.exists():
        print("ERROR: .env 파일이 없습니다.")
        print(f"  cp {env_path.parent}/.env.example {env_path}")
        sys.exit(1)

    load_dotenv(env_path)
    api_key = os.getenv("NOTION_API_KEY", "")
    parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID", "")

    if not api_key or api_key.startswith("ntn_xxx"):
        print("ERROR: NOTION_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    return {"api_key": api_key, "parent_page_id": parent_page_id}


def get_client(config: dict) -> Client:
    return Client(auth=config["api_key"])


def load_mapping() -> dict:
    if not MAPPING_FILE.exists():
        print("ERROR: notion_mapping.json이 없습니다.")
        print("  먼저 실행: python notion_sync.py generate-map")
        sys.exit(1)
    return json.loads(MAPPING_FILE.read_text(encoding="utf-8"))


def save_mapping(mapping: dict) -> None:
    MAPPING_FILE.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ─────────────────────────────────────────────
# Notion 트리 조회
# ─────────────────────────────────────────────

def get_page_title(page: dict) -> str:
    props = page.get("properties", {})
    for prop in props.values():
        if prop.get("type") == "title":
            title_arr = prop.get("title", [])
            if title_arr:
                return "".join(t.get("plain_text", "") for t in title_arr)
    if page.get("type") == "child_page":
        return page.get("child_page", {}).get("title", "(제목 없음)")
    return "(제목 없음)"


def get_child_pages(notion: Client, page_id: str) -> list:
    pages = []
    try:
        response = notion.blocks.children.list(block_id=page_id, page_size=100)
    except Exception as e:
        print(f"  WARNING: 하위 페이지 조회 실패 ({page_id}) - {e}")
        return pages
    for block in response.get("results", []):
        if block.get("type") == "child_page":
            pages.append({
                "id": block["id"],
                "title": block["child_page"]["title"],
                "has_children": block.get("has_children", False),
            })
    return pages


def get_all_blocks(notion: Client, page_id: str) -> list:
    """페이지의 모든 블록을 가져오기 (페이지네이션 포함)"""
    blocks = []
    cursor = None
    while True:
        kwargs = {"block_id": page_id, "page_size": 100}
        if cursor:
            kwargs["start_cursor"] = cursor
        response = notion.blocks.children.list(**kwargs)
        blocks.extend(response.get("results", []))
        if not response.get("has_more"):
            break
        cursor = response.get("next_cursor")
    return blocks


def list_child_pages_recursive(notion: Client, page_id: str, indent: int = 0) -> list:
    results = []
    prefix = "  " * indent
    try:
        response = notion.blocks.children.list(block_id=page_id, page_size=100)
    except Exception as e:
        print(f"{prefix}ERROR: 페이지 조회 실패 - {e}")
        return results

    for block in response.get("results", []):
        block_type = block.get("type", "")
        if block_type == "child_page":
            title = block["child_page"]["title"]
            block_id = block["id"]
            results.append({"id": block_id, "title": title, "indent": indent})
            print(f"{prefix}📄 {title}")
            print(f"{prefix}   ID: {block_id}")
            if block.get("has_children"):
                results.extend(list_child_pages_recursive(notion, block_id, indent + 1))
        elif block_type == "child_database":
            title = block["child_database"]["title"]
            print(f"{prefix}🗄️  [DB] {title}")
            print(f"{prefix}   ID: {block['id']}")
    return results


def list_pages(notion: Client, page_id: str) -> None:
    print(f"\n페이지 목록 조회: {page_id}\n{'─' * 50}")
    try:
        page_info = notion.pages.retrieve(page_id=page_id)
        print(f"📁 {get_page_title(page_info)} (루트)\n   ID: {page_id}\n")
    except Exception:
        print(f"📁 (루트 페이지)\n   ID: {page_id}\n")
    results = list_child_pages_recursive(notion, page_id)
    print(f"\n{'─' * 50}\n총 {len(results)}개 항목")


# ─────────────────────────────────────────────
# MD → Notion 블록 변환
# ─────────────────────────────────────────────

def parse_inline(text: str) -> list:
    """인라인 마크다운을 Notion rich_text 배열로 변환"""
    rich_text = []
    # 패턴: **bold**, *italic*, `code`, [text](url)
    pattern = re.compile(
        r'(\*\*(.+?)\*\*)'       # bold
        r'|(\*(.+?)\*)'          # italic
        r'|(`(.+?)`)'            # code
        r'|(\[(.+?)\]\((.+?)\))' # link
    )

    last_end = 0
    for m in pattern.finditer(text):
        # 매치 전 일반 텍스트
        if m.start() > last_end:
            plain = text[last_end:m.start()]
            if plain:
                rich_text.append({"type": "text", "text": {"content": plain}})

        if m.group(2):  # bold
            rich_text.append({
                "type": "text",
                "text": {"content": m.group(2)},
                "annotations": {"bold": True},
            })
        elif m.group(4):  # italic
            rich_text.append({
                "type": "text",
                "text": {"content": m.group(4)},
                "annotations": {"italic": True},
            })
        elif m.group(6):  # code
            rich_text.append({
                "type": "text",
                "text": {"content": m.group(6)},
                "annotations": {"code": True},
            })
        elif m.group(8):  # link
            rich_text.append({
                "type": "text",
                "text": {"content": m.group(8), "link": {"url": m.group(9)}},
            })

        last_end = m.end()

    # 남은 텍스트
    if last_end < len(text):
        remaining = text[last_end:]
        if remaining:
            rich_text.append({"type": "text", "text": {"content": remaining}})

    if not rich_text:
        rich_text.append({"type": "text", "text": {"content": text}})

    return rich_text


def make_text(content: str) -> list:
    """단순 텍스트 → rich_text 배열"""
    return [{"type": "text", "text": {"content": content}}]


def md_to_notion_blocks(md_text: str) -> list:
    """마크다운 텍스트를 Notion API 블록 배열로 변환"""
    blocks = []
    lines = md_text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # 빈 줄
        if not line.strip():
            i += 1
            continue

        # 수평선
        if re.match(r'^---+\s*$', line):
            blocks.append({"type": "divider", "divider": {}})
            i += 1
            continue

        # 제목 (Notion은 heading 1~3만 지원, h4+는 h3 볼드로 변환)
        h_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if h_match:
            level = min(len(h_match.group(1)), 3)  # h4~h6 → h3
            text = h_match.group(2).strip()
            h_type = f"heading_{level}"
            rich_text = parse_inline(text)
            # h4+ 는 볼드 처리로 시각적 구분
            if len(h_match.group(1)) > 3:
                for rt in rich_text:
                    rt.setdefault("annotations", {})["bold"] = True
            blocks.append({
                "type": h_type,
                h_type: {"rich_text": rich_text},
            })
            i += 1
            continue

        # 코드 블록 (mermaid 포함)
        code_match = re.match(r'^```(\w*)', line)
        if code_match:
            lang = code_match.group(1) or "plain text"
            # Notion API 지원 언어로 매핑
            LANG_MAP = {
                "text": "plain text", "txt": "plain text",
                "http": "plain text", "nginx": "plain text",
                "ini": "plain text", "cfg": "plain text",
                "gitignore": "plain text", "dockerignore": "plain text",
                "cypher": "plain text", "sh": "bash",
                "dockerfile": "docker", "yml": "yaml",
                "ts": "typescript", "js": "javascript",
                "py": "python", "rb": "ruby",
                "rs": "rust", "kt": "kotlin",
            }
            lang = LANG_MAP.get(lang, lang)
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # ``` 닫기 건너뜀

            code_content = "\n".join(code_lines)
            # Notion 코드 블록 텍스트 제한: 2000자
            if len(code_content) > 2000:
                code_content = code_content[:1997] + "..."

            blocks.append({
                "type": "code",
                "code": {
                    "rich_text": make_text(code_content),
                    "language": lang,
                },
            })
            continue

        # 블록쿼트
        if line.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].startswith("> "):
                quote_lines.append(lines[i][2:])
                i += 1
            blocks.append({
                "type": "quote",
                "quote": {"rich_text": parse_inline(" ".join(quote_lines))},
            })
            continue

        # 테이블
        if "|" in line and i + 1 < len(lines) and re.match(r'^\|[-|: ]+\|$', lines[i + 1].strip()):
            table_rows = []
            # 헤더
            header_cells = [c.strip() for c in line.strip().strip("|").split("|")]
            table_rows.append(header_cells)
            i += 2  # 헤더 + 구분선 건너뜀

            while i < len(lines) and "|" in lines[i] and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                table_rows.append(cells)
                i += 1

            col_count = len(header_cells)
            notion_rows = []
            for row in table_rows:
                # 열 수 맞추기
                while len(row) < col_count:
                    row.append("")
                row = row[:col_count]
                notion_rows.append({
                    "type": "table_row",
                    "table_row": {
                        "cells": [parse_inline(cell) for cell in row],
                    },
                })

            blocks.append({
                "type": "table",
                "table": {
                    "table_width": col_count,
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": notion_rows,
                },
            })
            continue

        # 번호 목록 (들여쓰기 포함)
        num_match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', line)
        if num_match:
            blocks.append({
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": parse_inline(num_match.group(3))},
            })
            i += 1
            continue

        # 불릿 목록 (들여쓰기 포함)
        bullet_match = re.match(r'^(\s*)[-*]\s+(.+)$', line)
        if bullet_match:
            blocks.append({
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": parse_inline(bullet_match.group(2))},
            })
            i += 1
            continue

        # 일반 단락
        blocks.append({
            "type": "paragraph",
            "paragraph": {"rich_text": parse_inline(line)},
        })
        i += 1

    return blocks


def extract_mermaid_from_md(md_text: str) -> list:
    """MD 텍스트에서 mermaid 코드 블록만 추출"""
    pattern = r'```mermaid\n(.*?)```'
    return [m.strip() for m in re.findall(pattern, md_text, flags=re.DOTALL)]


# ─────────────────────────────────────────────
# update-mermaid 명령
# ─────────────────────────────────────────────

def find_mermaid_blocks_in_notion(notion: Client, page_id: str) -> list:
    """Notion 페이지에서 mermaid 코드 블록의 ID 목록 반환"""
    all_blocks = get_all_blocks(notion, page_id)
    mermaid_blocks = []
    for block in all_blocks:
        if block.get("type") == "code":
            lang = block["code"].get("language", "")
            if lang == "mermaid":
                mermaid_blocks.append({
                    "id": block["id"],
                    "content": "".join(
                        t.get("plain_text", "")
                        for t in block["code"].get("rich_text", [])
                    ),
                })
    return mermaid_blocks


def update_mermaid_block(notion: Client, block_id: str, new_content: str) -> None:
    """Notion의 mermaid 코드 블록 내용 업데이트"""
    if len(new_content) > 2000:
        new_content = new_content[:1997] + "..."

    notion.blocks.update(
        block_id=block_id,
        code={
            "rich_text": make_text(new_content),
            "language": "mermaid",
        },
    )


def simple_diff(old: str, new: str, label: str) -> str:
    """간단한 diff 출력 (변경된 줄만)"""
    old_lines = old.strip().splitlines()
    new_lines = new.strip().splitlines()
    output = [f"    ┌─ {label}"]

    max_lines = max(len(old_lines), len(new_lines))
    for i in range(max_lines):
        old_line = old_lines[i] if i < len(old_lines) else ""
        new_line = new_lines[i] if i < len(new_lines) else ""
        if old_line != new_line:
            if old_line:
                output.append(f"    │ - {old_line}")
            if new_line:
                output.append(f"    │ + {new_line}")

    output.append(f"    └─")
    return "\n".join(output)


def cmd_update_mermaid(notion: Client, mapping: dict, target: str = None, dry_run: bool = False, verbose: bool = False) -> None:
    """Mermaid 블록만 업데이트"""
    print(f"\n{'═' * 50}")
    print("Mermaid 다이어그램 업데이트" + (" (DRY RUN)" if dry_run else ""))
    print(f"{'═' * 50}\n")

    updated = 0
    skipped = 0
    errors = 0

    for dir_name, section in mapping.items():
        if target and dir_name != target:
            continue
        if not section.get("notion_id"):
            continue

        print(f"📁 {dir_name} ({section.get('notion_title', '')})")

        for fname, fdata in section["files"].items():
            if fdata.get("action") not in ("update",) or not fdata.get("notion_id"):
                continue

            md_path = DOCS_ROOT / dir_name / fname
            if not md_path.exists():
                continue

            md_text = md_path.read_text(encoding="utf-8")
            local_mermaids = extract_mermaid_from_md(md_text)

            if not local_mermaids:
                continue

            notion_mermaids = find_mermaid_blocks_in_notion(notion, fdata["notion_id"])

            matched = min(len(local_mermaids), len(notion_mermaids))
            changed = 0

            for j in range(matched):
                local_code = local_mermaids[j]
                notion_code = notion_mermaids[j]["content"]

                if local_code.strip() != notion_code.strip():
                    if verbose:
                        print(simple_diff(notion_code, local_code, f"mermaid #{j+1}"))
                    if not dry_run:
                        try:
                            update_mermaid_block(notion, notion_mermaids[j]["id"], local_code)
                            changed += 1
                            time.sleep(0.35)  # Rate limit
                        except Exception as e:
                            print(f"    ERROR: {fname} mermaid #{j+1} - {e}")
                            errors += 1
                    else:
                        changed += 1

            diff_count = len(local_mermaids) - len(notion_mermaids)
            status_parts = []
            if changed:
                status_parts.append(f"{changed}개 업데이트")
                updated += changed
            if diff_count > 0:
                status_parts.append(f"{diff_count}개 Notion에 없음")
                skipped += diff_count
            if diff_count < 0:
                status_parts.append(f"{-diff_count}개 Notion에만 존재")

            if status_parts:
                print(f"  {'🔄' if changed else '  '} {fname}: {', '.join(status_parts)}")
            else:
                print(f"    {fname}: 변경 없음")

    print(f"\n{'═' * 50}")
    print(f"결과: {updated}개 업데이트, {skipped}개 스킵, {errors}개 오류")


# ─────────────────────────────────────────────
# update 명령 (전체 내용 교체)
# ─────────────────────────────────────────────

def delete_all_blocks(notion: Client, page_id: str) -> int:
    """페이지의 모든 블록 삭제 (rate limit 자동 재시도)"""
    blocks = get_all_blocks(notion, page_id)
    count = 0
    for block in blocks:
        for attempt in range(3):
            try:
                notion.blocks.delete(block_id=block["id"])
                count += 1
                break
            except Exception as e:
                if "rate" in str(e).lower() and attempt < 2:
                    time.sleep(1)
                    continue
                break
    return count


def append_blocks_chunked(notion: Client, page_id: str, blocks: list) -> int:
    """블록을 100개씩 나눠서 추가 (API 제한)"""
    total = 0
    for i in range(0, len(blocks), 100):
        chunk = blocks[i:i+100]
        try:
            notion.blocks.children.append(block_id=page_id, children=chunk)
            total += len(chunk)
            time.sleep(0.35)
        except Exception as e:
            print(f"    ERROR: 블록 추가 실패 (#{i}~{i+len(chunk)}) - {e}")
    return total


def fmt_duration(seconds: float) -> str:
    """초를 읽기 쉬운 형태로 변환"""
    if seconds < 60:
        return f"{seconds:.1f}초"
    m, s = divmod(seconds, 60)
    return f"{int(m)}분 {s:.1f}초"


def cmd_update(notion: Client, mapping: dict, target: str = None, file_filter: str = None, dry_run: bool = False) -> None:
    """기존 페이지 전체 내용 교체 (블록 삭제 → 새 블록 추가)"""
    print(f"\n{'═' * 50}")
    print("페이지 내용 업데이트" + (" (DRY RUN)" if dry_run else ""))
    print(f"{'═' * 50}\n")

    updated = 0
    total_start = time.time()
    page_stats = []  # (제목, 블록수, 소요시간)

    for dir_name, section in mapping.items():
        if target and dir_name != target:
            continue
        if not section.get("notion_id"):
            continue

        print(f"📁 {dir_name} ({section.get('notion_title', '')})")

        for fname, fdata in section["files"].items():
            if fdata.get("action") != "update" or not fdata.get("notion_id"):
                continue
            if file_filter and file_filter not in fname:
                continue

            md_path = DOCS_ROOT / dir_name / fname
            if not md_path.exists():
                print(f"  ⚠️  {fname}: 로컬 파일 없음")
                continue

            md_text = md_path.read_text(encoding="utf-8")
            blocks = md_to_notion_blocks(md_text)

            if dry_run:
                print(f"  🔄 {fname} → {len(blocks)}개 블록 (dry-run)")
                page_stats.append((fname, len(blocks), 0))
                updated += 1
                continue

            page_start = time.time()
            print(f"  🔄 {fname}: 삭제...", end="", flush=True)
            deleted = delete_all_blocks(notion, fdata["notion_id"])
            print(f"({deleted}) → 추가...", end="", flush=True)
            added = append_blocks_chunked(notion, fdata["notion_id"], blocks)
            elapsed = time.time() - page_start
            print(f"({added}) ✓  [{fmt_duration(elapsed)}]")
            page_stats.append((fname, added, elapsed))
            updated += 1
            time.sleep(0.3)

    total_elapsed = time.time() - total_start

    # 요약 테이블
    print(f"\n{'═' * 60}")
    print(f" {'파일':<40} {'블록':>5} {'소요시간':>10}")
    print(f"{'─' * 60}")
    cumulative = 0
    for name, blocks_count, elapsed in page_stats:
        cumulative += elapsed
        print(f" {name:<40} {blocks_count:>5} {fmt_duration(elapsed):>10}")
    print(f"{'─' * 60}")
    print(f" {'합계':<40} {sum(b for _, b, _ in page_stats):>5} {fmt_duration(total_elapsed):>10}")
    print(f"{'═' * 60}")
    print(f"\n총 {updated}개 페이지 업데이트 완료 (총 {fmt_duration(total_elapsed)})")


# ─────────────────────────────────────────────
# create 명령 (새 페이지 생성)
# ─────────────────────────────────────────────

def get_title_from_md(md_text: str) -> str:
    """마크다운 첫 번째 # 제목 추출"""
    for line in md_text.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def create_notion_page(notion: Client, parent_id: str, title: str, blocks: list) -> str:
    """Notion에 새 페이지 생성하고 블록 추가, 페이지 ID 반환"""
    # 페이지 생성 (children에 최대 100개 블록)
    first_chunk = blocks[:100]
    page = notion.pages.create(
        parent={"page_id": parent_id},
        properties={"title": [{"text": {"content": title}}]},
        children=first_chunk,
    )
    page_id = page["id"]

    # 나머지 블록 추가
    if len(blocks) > 100:
        append_blocks_chunked(notion, page_id, blocks[100:])

    return page_id


def cmd_create(notion: Client, mapping: dict, target: str = None, dry_run: bool = False) -> None:
    """새 페이지 생성"""
    print(f"\n{'═' * 50}")
    print("새 페이지 생성" + (" (DRY RUN)" if dry_run else ""))
    print(f"{'═' * 50}\n")

    created = 0
    parent_page_id = load_config()["parent_page_id"]

    for dir_name, section in mapping.items():
        if target and dir_name != target:
            continue

        has_creates = any(
            f.get("action") == "create" for f in section["files"].values()
        )
        if not has_creates:
            continue

        # 섹션 페이지가 없으면 먼저 생성
        section_id = section.get("notion_id")
        if not section_id:
            section_title = dir_name.split("_", 1)[-1] if "_" in dir_name else dir_name
            # MODULE_INFO에서 한글 제목 가져오기
            module_titles = {
                "00_OT": "0.오리엔테이션",
                "01_genai_intro": "1.생성형AI(입문)",
                "02_web_basics": "2.웹개발기초",
                "03_python_webdev": "3.Python 웹개발",
                "04_database": "4.데이터베이스",
                "05_genai_advanced": "5.생성형AI(심화)",
                "06_genai_applied": "6.생성형AI(응용)",
                "07_cloud": "7.클라우드",
                "08_team_project": "8.팀프로젝트",
            }
            section_title = module_titles.get(dir_name, section_title)

            if dry_run:
                print(f"📁 {dir_name} → 섹션 페이지 생성: '{section_title}' (dry-run)")
            else:
                print(f"📁 {dir_name} → 섹션 페이지 생성: '{section_title}'...", end="", flush=True)
                page = notion.pages.create(
                    parent={"page_id": parent_page_id},
                    properties={"title": [{"text": {"content": section_title}}]},
                )
                section_id = page["id"]
                section["notion_id"] = section_id
                section["notion_title"] = section_title
                section["action"] = "update"
                print(f" ✓ (ID: {section_id})")
                time.sleep(0.5)
        else:
            print(f"📁 {dir_name} ({section.get('notion_title', '')})")

        for fname, fdata in section["files"].items():
            if fdata.get("action") != "create":
                continue

            md_path = DOCS_ROOT / dir_name / fname
            if not md_path.exists():
                print(f"  ⚠️  {fname}: 로컬 파일 없음")
                continue

            md_text = md_path.read_text(encoding="utf-8")
            title = get_title_from_md(md_text)
            blocks = md_to_notion_blocks(md_text)

            if dry_run:
                print(f"  🆕 {fname} → '{title}' ({len(blocks)}개 블록) (dry-run)")
                created += 1
                continue

            print(f"  🆕 {fname} → '{title}'...", end="", flush=True)
            try:
                new_page_id = create_notion_page(notion, section_id, title, blocks)
                fdata["notion_id"] = new_page_id
                fdata["notion_title"] = title
                fdata["status"] = "matched"
                fdata["action"] = "update"
                print(f" ✓ ({len(blocks)}개 블록)")
                created += 1
                time.sleep(0.5)
            except Exception as e:
                print(f" ERROR: {e}")

    # 매핑 파일 업데이트 (새로 생성된 ID 반영)
    if not dry_run and created > 0:
        save_mapping(mapping)
        print(f"\n📄 notion_mapping.json 업데이트됨")

    print(f"\n{'═' * 50}")
    print(f"총 {created}개 페이지 생성 완료")


# ─────────────────────────────────────────────
# 매핑 생성
# ─────────────────────────────────────────────

def extract_number(name: str) -> int:
    m = re.match(r'^(\d+)', name.lstrip('0') or '0')
    if m:
        return int(m.group(1))
    m = re.match(r'^(\d+)', name)
    if m:
        return int(m.group(1))
    return 999


def get_local_dirs() -> list:
    dirs = []
    for d in sorted(DOCS_ROOT.iterdir()):
        if d.is_dir() and not d.name.startswith('.') and d.name not in ("pdf_output", "__pycache__"):
            md_files = sorted(d.glob("*.md"))
            if md_files:
                dirs.append({"name": d.name, "files": [f.name for f in md_files]})
    return dirs


def match_by_position(local_items: list, notion_items: list) -> list:
    pairs = []
    local_sorted = sorted(local_items, key=lambda x: extract_number(x))
    notion_sorted = sorted(notion_items, key=lambda x: extract_number(x.get("title", "")))

    for i, local_name in enumerate(local_sorted):
        if i < len(notion_sorted):
            pairs.append({"local": local_name, "notion_id": notion_sorted[i]["id"], "notion_title": notion_sorted[i]["title"]})
        else:
            pairs.append({"local": local_name, "notion_id": None, "notion_title": None})

    for j in range(len(local_sorted), len(notion_sorted)):
        pairs.append({"local": None, "notion_id": notion_sorted[j]["id"], "notion_title": notion_sorted[j]["title"]})

    return pairs


def generate_mapping(notion: Client, parent_page_id: str) -> dict:
    print("Notion 페이지 트리 조회 중...")
    notion_sections = get_child_pages(notion, parent_page_id)
    print(f"  → {len(notion_sections)}개 섹션 발견\n")

    local_dirs = get_local_dirs()
    print(f"로컬 디렉토리 {len(local_dirs)}개 발견\n")

    section_pairs = match_by_position([d["name"] for d in local_dirs], notion_sections)
    mapping = {}

    for pair in section_pairs:
        local_dir = pair["local"]
        notion_id = pair["notion_id"]
        notion_title = pair["notion_title"]
        if not local_dir:
            continue

        print(f"📁 {local_dir} ↔ {notion_title or '(매칭 없음)'}")

        section_data = {
            "notion_id": notion_id,
            "notion_title": notion_title,
            "action": "update" if notion_id else "skip",
            "files": {},
        }

        if notion_id:
            notion_children = get_child_pages(notion, notion_id)
            notion_child_pages = [c for c in notion_children if re.match(r'^\d', c["title"])]
            local_dir_info = next((d for d in local_dirs if d["name"] == local_dir), None)
            local_files = local_dir_info["files"] if local_dir_info else []
            file_pairs = match_by_position(local_files, notion_child_pages)

            for fp in file_pairs:
                if fp["local"]:
                    status = "matched" if fp["notion_id"] else "local_only"
                    icon = "  ✅" if fp["notion_id"] else "  ⚠️ "
                    print(f"{icon} {fp['local']} ↔ {fp['notion_title'] or '(Notion에 없음)'}")
                    section_data["files"][fp["local"]] = {
                        "notion_id": fp["notion_id"],
                        "notion_title": fp["notion_title"],
                        "status": status,
                        "action": "update" if fp["notion_id"] else "create",
                    }
        else:
            local_dir_info = next((d for d in local_dirs if d["name"] == local_dir), None)
            if local_dir_info:
                for f in local_dir_info["files"]:
                    section_data["files"][f] = {
                        "notion_id": None, "notion_title": None,
                        "status": "local_only", "action": "skip",
                    }
                    print(f"  ⚠️  {f} ↔ (Notion에 없음)")

        mapping[local_dir] = section_data
        print()

    return mapping


def cmd_generate_map(notion: Client, parent_page_id: str) -> None:
    print(f"\n{'═' * 50}\n로컬 MD ↔ Notion 페이지 매핑 생성\n{'═' * 50}\n")
    mapping = generate_mapping(notion, parent_page_id)

    total = sum(len(s["files"]) for s in mapping.values())
    actions = {"update": 0, "create": 0, "skip": 0}
    for s in mapping.values():
        for f in s["files"].values():
            actions[f.get("action", "skip")] += 1

    save_mapping(mapping)

    print(f"{'═' * 50}")
    print(f"매핑 결과: 총 {total}개 파일")
    print(f"  🔄 update: {actions['update']}개  🆕 create: {actions['create']}개  ⏸️  skip: {actions['skip']}개")
    print(f"\n📄 매핑 파일: {MAPPING_FILE}")


# ─────────────────────────────────────────────
# 검색
# ─────────────────────────────────────────────

def search_pages(notion: Client, query: str) -> None:
    print(f"\n'{query}' 검색 결과\n{'─' * 50}")
    response = notion.search(query=query, filter={"property": "object", "value": "page"}, page_size=20)
    results = response.get("results", [])

    if not results:
        print("검색 결과가 없습니다.")
        return

    for page in results:
        title = get_page_title(page)
        print(f"📄 {title}\n   ID: {page['id']}\n   수정일: {page.get('last_edited_time', '')[:10]}\n")

    print(f"{'─' * 50}\n총 {len(results)}개 결과")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Notion 페이지 동기화 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python notion_sync.py list                           # 페이지 목록
  python notion_sync.py generate-map                   # 매핑 생성
  python notion_sync.py update-mermaid                 # 전체 Mermaid 업데이트
  python notion_sync.py update-mermaid 00_OT           # 특정 모듈 Mermaid만
  python notion_sync.py update 00_OT                   # 특정 모듈 전체 업데이트
  python notion_sync.py create 03_python_webdev        # 새 모듈 페이지 생성
  python notion_sync.py update --dry-run               # 실제 실행 없이 확인
  python notion_sync.py search "클라우드"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="실행할 명령")

    # list
    p_list = subparsers.add_parser("list", help="페이지 목록 조회")
    p_list.add_argument("--page-id", default=None)

    # generate-map
    subparsers.add_parser("generate-map", help="로컬 ↔ Notion 매핑 생성")

    # update-mermaid
    p_mermaid = subparsers.add_parser("update-mermaid", help="Mermaid 다이어그램만 업데이트")
    p_mermaid.add_argument("target", nargs="?", default=None, help="모듈명 (예: 00_OT)")
    p_mermaid.add_argument("--dry-run", action="store_true", help="실제 실행 없이 변경 내용만 확인")
    p_mermaid.add_argument("--verbose", "-v", action="store_true", help="변경될 내용의 diff 표시")

    # update
    p_update = subparsers.add_parser("update", help="기존 페이지 전체 내용 교체")
    p_update.add_argument("target", nargs="?", default=None, help="모듈명 (예: 00_OT)")
    p_update.add_argument("--file", "-f", default=None, help="특정 파일만 (예: 08_github_and_git_auth.md)")
    p_update.add_argument("--dry-run", action="store_true")

    # create
    p_create = subparsers.add_parser("create", help="새 페이지 생성")
    p_create.add_argument("target", nargs="?", default=None, help="모듈명")
    p_create.add_argument("--dry-run", action="store_true")

    # search
    p_search = subparsers.add_parser("search", help="워크스페이스 검색")
    p_search.add_argument("query")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    config = load_config()
    notion = get_client(config)

    if args.command == "list":
        page_id = args.page_id or config["parent_page_id"]
        if not page_id:
            print("ERROR: 페이지 ID가 필요합니다.")
            sys.exit(1)
        list_pages(notion, page_id)

    elif args.command == "generate-map":
        if not config["parent_page_id"]:
            print("ERROR: NOTION_PARENT_PAGE_ID가 필요합니다.")
            sys.exit(1)
        cmd_generate_map(notion, config["parent_page_id"])

    elif args.command == "update-mermaid":
        mapping = load_mapping()
        cmd_update_mermaid(notion, mapping, args.target, args.dry_run, getattr(args, 'verbose', False))

    elif args.command == "update":
        mapping = load_mapping()
        cmd_update(notion, mapping, args.target, getattr(args, 'file', None), args.dry_run)

    elif args.command == "create":
        mapping = load_mapping()
        cmd_create(notion, mapping, args.target, args.dry_run)

    elif args.command == "search":
        search_pages(notion, args.query)


if __name__ == "__main__":
    main()
