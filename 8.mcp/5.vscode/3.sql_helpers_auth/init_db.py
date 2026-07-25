"""
세 케이스가 쓰는 샘플 DB 두 개를 만든다 (표준 라이브러리 sqlite3 만 사용).

  shop.db  — 쇼핑몰(customers/products/orders/order_items). customers.email = PII 성격.
             → 케이스 2 에서 "analyst 는 customers 못 봄, admin 은 다 봄" 스코프 데모에 사용.
  hr.db    — 인사(departments/employees). salary = 민감.
             → 케이스 3 에서 "클라이언트가 shop.db 대신 hr.db 로 붙여봐" 데모에 사용.

실행:  python init_db.py        # 두 파일 모두 (덮어씀)
"""

import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
SHOP = os.path.join(HERE, "shop.db")
HR = os.path.join(HERE, "hr.db")

SHOP_SQL = """
CREATE TABLE customers   (id INTEGER PRIMARY KEY, name TEXT, email TEXT, city TEXT);
CREATE TABLE products    (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price INTEGER);
CREATE TABLE orders      (id INTEGER PRIMARY KEY, customer_id INTEGER, order_date TEXT, status TEXT);
CREATE TABLE order_items (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER, unit_price INTEGER);
"""
SHOP_DATA = {
    "customers": [(1, "김민수", "minsu@ex.com", "서울"), (2, "이서연", "seoyeon@ex.com", "부산"),
                  (3, "박지훈", "jihoon@ex.com", "서울"), (4, "최유진", "yujin@ex.com", "대구")],
    "products": [(1, "무선 마우스", "전자기기", 25000), (2, "기계식 키보드", "전자기기", 89000),
                 (3, "27인치 모니터", "전자기기", 320000), (4, "USB-C 허브", "액세서리", 42000)],
    "orders": [(1, 1, "2024-05-01", "shipped"), (2, 1, "2024-06-14", "paid"),
               (3, 2, "2024-05-03", "shipped"), (4, 3, "2024-06-25", "paid")],
    "order_items": [(1, 1, 1, 2, 25000), (2, 1, 4, 1, 42000), (3, 2, 3, 1, 320000),
                    (4, 3, 2, 1, 89000), (5, 4, 1, 1, 25000), (6, 4, 3, 1, 320000)],
}

HR_SQL = """
CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE employees   (id INTEGER PRIMARY KEY, name TEXT, dept_id INTEGER, salary INTEGER);
"""
HR_DATA = {
    "departments": [(1, "엔지니어링"), (2, "영업"), (3, "인사")],
    "employees": [(1, "홍길동", 1, 6200), (2, "성춘향", 1, 5800),
                  (3, "이몽룡", 2, 5000), (4, "변학도", 3, 4800)],
}


def build(path, schema, data):
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    conn.executescript(schema)
    for table, rows in data.items():
        ph = ",".join("?" * len(rows[0]))
        conn.executemany(f"INSERT INTO {table} VALUES ({ph})", rows)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    build(SHOP, SHOP_SQL, SHOP_DATA)
    build(HR, HR_SQL, HR_DATA)
    print(f"생성: {SHOP}  (customers/products/orders/order_items)")
    print(f"생성: {HR}    (departments/employees)")
