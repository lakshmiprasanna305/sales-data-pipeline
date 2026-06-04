import pandas as pd
import os
import glob
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

INPUT_PATH = "data/*.csv"
OUTPUT_PATH = "data/processed/"

def read_raw_data():
    files = glob.glob(INPUT_PATH)
    if not files:
        print("No CSV files found!")
        return None
    latest = max(files)
    print("Reading: " + latest)
    df = pd.read_csv(latest)
    print("Raw records: " + str(len(df)))
    return df

def transform_data(df):
    print("Applying transformations...")
    # Remove duplicates
    df = df.drop_duplicates(subset=["order_id"])
    print("After dedup: " + str(len(df)))
    # Remove nulls
    df = df.dropna(subset=["order_id", "total_amount"])
    # Remove negative amounts
    df = df[df["total_amount"] > 0]
    # Add derived columns
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    df["day"] = df["order_date"].dt.day
    df["revenue_tier"] = pd.cut(
        df["total_amount"],
        bins=[0, 50, 200, float("inf")],
        labels=["low", "medium", "high"]
    )
    df["processed_at"] = datetime.now().isoformat()
    # Standardize text
    df["status"] = df["status"].str.lower().str.strip()
    df["category"] = df["category"].str.lower().str.strip()
    print("Transformed records: " + str(len(df)))
    return df

def save_processed_data(df):
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    filename = OUTPUT_PATH + "processed_sales_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
    df.to_csv(filename, index=False)
    print("Saved to: " + filename)
    return filename

def run_quality_checks(df):
    print("Running quality checks...")
    checks = {
        "no_null_order_ids": df["order_id"].isnull().sum() == 0,
        "no_negative_amounts": (df["total_amount"] > 0).all(),
        "no_duplicates": df["order_id"].duplicated().sum() == 0,
        "row_count_ok": len(df) > 0,
    }
    for check, result in checks.items():
        status = "PASSED" if result else "FAILED"
        print(check + ": " + status)
    return all(checks.values())

if __name__ == "__main__":
    print("Starting ETL job...")
    df = read_raw_data()
    if df is not None:
        df = transform_data(df)
        passed = run_quality_checks(df)
        if passed:
            output_file = save_processed_data(df)
            print("ETL job completed successfully!")
            print("Output: " + output_file)
        else:
            print("Quality checks failed!")