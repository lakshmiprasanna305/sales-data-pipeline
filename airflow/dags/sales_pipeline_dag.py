from datetime import datetime, timedelta
import subprocess
import sys
import os

# DAG Configuration
DAG_ID = "sales_data_pipeline"
SCHEDULE = "0 2 * * *"  # Run at 2 AM every day

default_args = {
    "owner": "lakshmi_prasanna",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

def task_generate_data():
    print("TASK 1: Generating sales data...")
    result = subprocess.run(
        [sys.executable, "data_generator/generate_sales_data.py"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        raise Exception("Data generation failed: " + result.stderr)
    print("TASK 1: Completed!")

def task_upload_to_s3():
    print("TASK 2: Uploading to S3...")
    result = subprocess.run(
        [sys.executable, "ingestion/upload_to_s3.py"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        raise Exception("S3 upload failed: " + result.stderr)
    print("TASK 2: Completed!")

def task_run_etl():
    print("TASK 3: Running ETL transformations...")
    result = subprocess.run(
        [sys.executable, "etl/glue_etl_job.py"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        raise Exception("ETL failed: " + result.stderr)
    print("TASK 3: Completed!")

def task_load_warehouse():
    print("TASK 4: Loading data warehouse...")
    result = subprocess.run(
        [sys.executable, "warehouse/redshift_loader.py"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        raise Exception("Warehouse load failed: " + result.stderr)
    print("TASK 4: Completed!")

def task_quality_check():
    print("TASK 5: Running quality checks...")
    import sqlite3
    conn = sqlite3.connect("data/sales_warehouse.db")
    count = conn.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    revenue = conn.execute("SELECT SUM(total_amount) FROM fact_sales").fetchone()[0]
    conn.close()
    print("Records in warehouse: " + str(count))
    print("Total revenue: $" + str(round(revenue, 2)))
    if count == 0:
        raise Exception("Quality check failed - no records!")
    print("TASK 5: All checks passed!")

def run_pipeline():
    print("=" * 50)
    print("SALES DATA PIPELINE STARTING")
    print("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 50)
    tasks = [
        ("Generate Data", task_generate_data),
        ("Upload to S3", task_upload_to_s3),
        ("Run ETL", task_run_etl),
        ("Load Warehouse", task_load_warehouse),
        ("Quality Check", task_quality_check),
    ]
    for task_name, task_func in tasks:
        print("Running: " + task_name + "...")
        try:
            task_func()
            print(task_name + " PASSED!")
        except Exception as e:
            print("ERROR in " + task_name + ": " + str(e))
            print("Pipeline failed at: " + task_name)
            return False
    print("=" * 50)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = run_pipeline()
    if success:
        print("All 5 tasks completed!")
    else:
        print("Pipeline failed!")