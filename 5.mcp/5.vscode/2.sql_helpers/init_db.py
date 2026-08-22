"""
샘플 SQLite DB 생성기 — sql-helper MCP 서버가 질의할 데이터를 만든다.

작은 쇼핑몰 스키마(4개 테이블)로, 조인·집계 질의가 재밌게 나오도록 구성했다.

    customers ─┐
               │ 1:N
             orders ─┐
                     │ 1:N
                order_items ──N:1── products

실행:
    python init_db.py            # ./sample.db 생성 (이미 있으면 덮어씀)
    python init_db.py --keep     # 있으면 그대로 두기

이 파일은 순수 표준 라이브러리(sqlite3)만 쓴다 — 추가 설치 불필요.
"""

import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "sample.db")

SCHEMA = """
CREATE TABLE customers (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    city        TEXT    NOT NULL,
    created_at  TEXT    NOT NULL          -- ISO 날짜
);

CREATE TABLE products (
    id        INTEGER PRIMARY KEY,
    name      TEXT    NOT NULL,
    category  TEXT    NOT NULL,
    price     INTEGER NOT NULL,           -- 원 단위(정수)
    stock     INTEGER NOT NULL
);

CREATE TABLE orders (
    id           INTEGER PRIMARY KEY,
    customer_id  INTEGER NOT NULL REFERENCES customers(id),
    order_date   TEXT    NOT NULL,
    status       TEXT    NOT NULL          -- paid / shipped / cancelled
);

CREATE TABLE order_items (
    id          INTEGER PRIMARY KEY,
    order_id    INTEGER NOT NULL REFERENCES orders(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER NOT NULL,
    unit_price  INTEGER NOT NULL           -- 주문 시점 단가(가격 변동 대비)
);
"""

CUSTOMERS = [
    # id, name, email, city, created_at
    (1, "김민수", "minsu@example.com", "서울", "2024-01-05"),
    (2, "이서연", "seoyeon@example.com", "부산", "2024-02-11"),
    (3, "박지훈", "jihoon@example.com", "서울", "2024-03-02"),
    (4, "최유진", "yujin@example.com", "대구", "2024-03-19"),
    (5, "정하늘", "haneul@example.com", "인천", "2024-04-07"),
    (6, "강도윤", "doyoon@example.com", "부산", "2024-05-21"),
]

PRODUCTS = [
    # id, name, category, price, stock
    (1, "무선 마우스", "전자기기", 25000, 120),
    (2, "기계식 키보드", "전자기기", 89000, 45),
    (3, "27인치 모니터", "전자기기", 320000, 18),
    (4, "USB-C 허브", "액세서리", 42000, 60),
    (5, "노트북 거치대", "액세서리", 35000, 80),
    (6, "블루투스 이어폰", "전자기기", 159000, 33),
    (7, "마우스패드", "액세서리", 12000, 200),
    (8, "웹캠 1080p", "전자기기", 68000, 25),
]

ORDERS = [
    # id, customer_id, order_date, status
    (1, 1, "2024-05-01", "shipped"),
    (2, 1, "2024-06-14", "paid"),
    (3, 2, "2024-05-03", "shipped"),
    (4, 3, "2024-05-20", "cancelled"),
    (5, 3, "2024-06-25", "paid"),
    (6, 4, "2024-06-02", "shipped"),
    (7, 5, "2024-06-30", "paid"),
    (8, 2, "2024-07-08", "paid"),
    (9, 6, "2024-07-15", "shipped"),
]

ORDER_ITEMS = [
    # id, order_id, product_id, quantity, unit_price
    (1, 1, 1, 2, 25000),
    (2, 1, 7, 1, 12000),
    (3, 2, 3, 1, 320000),
    (4, 3, 2, 1, 89000),
    (5, 3, 5, 1, 35000),
    (6, 4, 6, 1, 159000),     # 취소된 주문
    (7, 5, 4, 2, 42000),
    (8, 5, 8, 1, 68000),
    (9, 6, 1, 1, 25000),
    (10, 6, 2, 1, 89000),
    (11, 6, 3, 1, 320000),
    (12, 7, 6, 2, 159000),
    (13, 8, 7, 3, 12000),
    (14, 8, 5, 1, 35000),
    (15, 9, 8, 1, 68000),
    (16, 9, 4, 1, 42000),
]


def build():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", CUSTOMERS)
    conn.executemany("INSERT INTO products VALUES (?,?,?,?,?)", PRODUCTS)
    conn.executemany("INSERT INTO orders VALUES (?,?,?,?)", ORDERS)
    conn.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", ORDER_ITEMS)
    conn.commit()
    conn.close()


def main():
    if os.path.exists(DB_PATH):
        if "--keep" in sys.argv:
            print(f"이미 존재 → 그대로 둠: {DB_PATH}")
            return
        os.remove(DB_PATH)
        print(f"기존 DB 삭제: {DB_PATH}")
    build()
    print(f"샘플 DB 생성 완료: {DB_PATH}")
    print(f"  테이블: customers({len(CUSTOMERS)}) products({len(PRODUCTS)}) "
          f"orders({len(ORDERS)}) order_items({len(ORDER_ITEMS)})")
    print("  예) '도시별 총 매출' 은 customers ⋈ orders ⋈ order_items 조인으로 뽑힌다.")


if __name__ == "__main__":
    main()
