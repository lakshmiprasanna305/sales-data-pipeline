import sqlite3
import pandas as pd
import os
import glob
from datetime import datetime

DB_PATH = "data/sales_warehouse.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    print("Connected to database: " + DB_PATH)
    return conn

def create_tables(conn):
    print("Creating tables...")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fact_sales (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT,
            customer_name TEXT,
            customer_email TEXT,
            product_id TEXT,
            product_name TEXT,
            category TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_amount REAL,
            order_date TEXT,
            status TEXT,
            payment_method TEXT,
            country TEXT,
            city TEXT,
            year INTEGER,
            month INTEGER,
            day INTEGER,
            revenue_tier TEXT,
            processed_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_summary (
            summary_date TEXT PRIMARY KEY,
            total_orders INTEGER,
            total_revenue REAL,
            avg_order_value REAL
        )
    """)
    conn.commit()
    print("Tables created!")

def load_data(conn):
    files = glob.glob("data/processed/*.csv")
    if not files:
        print("No processed files found!")
        print("Run glue_etl_job.py first!")
        return 0
    latest = max(files)
    print("Loading: " + latest)
    df = pd.read_csv(latest)
    df.to_sql("fact_sales", conn, if_exists="replace", index=False)
    print("Loaded " + str(len(df)) + " records into fact_sales!")
    return len(df)

def run_analytics(conn):
    print("Running analytics queries...")
    queries = {
        "Total Revenue": "SELECT ROUND(SUM(total_amount), 2) FROM fact_sales",
        "Total Orders": "SELECT COUNT(*) FROM fact_sales",
        "Avg Order Value": "SELECT ROUND(AVG(total_amount), 2) FROM fact_sales",
        "Top Category": "SELECT category, COUNT(*) as orders FROM fact_sales GROUP BY category ORDER BY orders DESC LIMIT 1",
        "Revenue by Status": "SELECT status, ROUND(SUM(total_amount), 2) as revenue FROM fact_sales GROUP BY status",
    }
    for name, query in queries.items():
        result = conn.execute(query).fetchall()
        print(name + ": " + str(result))

def create_daily_summary(conn):
    print("Creating daily summary...")
    conn.execute("DELETE FROM daily_summary")
    conn.execute("""
        INSERT INTO daily_summary
        SELECT
            order_date,
            COUNT(*) as total_orders,
            ROUND(SUM(total_amount), 2) as total_revenue,
            ROUND(AVG(total_amount), 2) as avg_order_value
        FROM fact_sales
        GROUP BY order_date
    """)
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM daily_summary").fetchone()[0]
    print("Daily summary created: " + str(count) + " rows!")

if __name__ == "__main__":
    print("Starting data warehouse loader...")
    conn = get_connection()
    create_tables(conn)
    records = load_data(conn)
    if records > 0:
        run_analytics(conn)
        create_daily_summary(conn)
        print("Warehouse loaded successfully!")
    conn.close()
    print("Done!")
    