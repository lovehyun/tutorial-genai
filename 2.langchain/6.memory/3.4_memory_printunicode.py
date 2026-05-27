# dump_history.py
import sys, io, argparse
from langchain_community.chat_message_histories import FileChatMessageHistory, SQLChatMessageHistory
from sqlalchemy import create_engine

ROLE_MAP = {"human": "User", "ai": "AI", "system": "System"}

def force_utf8_stdout():
    """Windows 콘솔 포함 표준출력을 UTF-8로 강제."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

def dump_file_history(path: str):
    hist = FileChatMessageHistory(path)
    print(f"=== FileChatMessageHistory: {path} ===")
    if not hist.messages:
        print("(빈 히스토리)")
        return
    for i, m in enumerate(hist.messages, 1):
        role = ROLE_MAP.get(m.type, m.type)
        print(f"{i:02d}. [{role}] {m.content}")

def dump_sql_history(db_url: str, session_id: str):
    engine = create_engine(db_url)
    hist = SQLChatMessageHistory(session_id=session_id, connection=engine)
    print(f"=== SQLChatMessageHistory: {db_url} / session_id={session_id} ===")
    if not hist.messages:
        print("(빈 히스토리)")
        return
    for i, m in enumerate(hist.messages, 1):
        role = ROLE_MAP.get(m.type, m.type)
        print(f"{i:02d}. [{role}] {m.content}")

def build_parser():
    p = argparse.ArgumentParser(
        description="LangChain ChatMessageHistory dumper (UTF-8 safe)."
    )
    # --file / --db 둘 다 선택 가능하게 하고 기본값 부여
    p.add_argument("--file", nargs="?", const="history.json", default=None,
                   help="FileChatMessageHistory JSON 경로 (기본: history.json)")
    p.add_argument("--db", nargs="?", const="sqlite:///chat_history.db", default=None,
                   help="SQL DB URL (기본: sqlite:///chat_history.db)")
    p.add_argument("--session", default="default",
                   help="SQL 모드에서 사용할 session_id (기본: default)")
    return p

def main():
    force_utf8_stdout()
    args = build_parser().parse_args()

    # 우선순위: --file > --db > 기본 파일
    if args.file:
        dump_file_history(args.file)
    elif args.db:
        dump_sql_history(args.db, args.session)
    else:
        dump_file_history("history.json")

if __name__ == "__main__":
    main()
