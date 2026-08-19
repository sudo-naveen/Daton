import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "daton.db")

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS sales")
    cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            region TEXT NOT NULL,
            category TEXT NOT NULL,
            units_sold INTEGER NOT NULL,
            revenue REAL NOT NULL,
            sale_date DATE NOT NULL
        )
    """)

    cursor.execute("DROP TABLE IF EXISTS employees")
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            salary REAL NOT NULL,
            hire_date DATE NOT NULL,
            performance_rating REAL
        )
    """)

    import csv
    sales_csv = os.path.join(os.path.dirname(__file__), "sample_sales.csv")
    with open(sales_csv, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute(
                "INSERT INTO sales (product_name, region, category, units_sold, revenue, sale_date) VALUES (?, ?, ?, ?, ?, ?)",
                (row["product_name"], row["region"], row["category"], int(row["units_sold"]), float(row["revenue"]), row["date"]),
            )

    emp_csv = os.path.join(os.path.dirname(__file__), "sample_employees.csv")
    with open(emp_csv, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute(
                "INSERT INTO employees (id, name, department, designation, salary, hire_date, performance_rating) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (int(row["employee_id"]), row["name"], row["department"], row["designation"], float(row["salary"]), row["hire_date"], float(row["performance_rating"])),
            )

    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH}")
    print(f"  - sales: {sum(1 for _ in open(sales_csv)) - 1} rows")
    print(f"  - employees: {sum(1 for _ in open(emp_csv)) - 1} rows")

if __name__ == "__main__":
    setup_database()
