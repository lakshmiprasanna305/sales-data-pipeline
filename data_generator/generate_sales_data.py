from faker import Faker
import pandas as pd
import random
import os
from datetime import datetime

fake = Faker()

def generate_sales_record():
    return {
        "order_id": fake.uuid4(),
        "customer_id": fake.uuid4(),
        "customer_name": fake.name(),
        "customer_email": fake.email(),
        "product_id": f"PROD-{random.randint(1000, 9999)}",
        "product_name": fake.catch_phrase(),
        "category": random.choice(["Electronics","Clothing","Books","Food","Sports"]),
        "quantity": random.randint(1, 10),
        "unit_price": round(random.uniform(9.99, 999.99), 2),
        "order_date": fake.date_time_between(start_date="-1y").isoformat(),
        "status": random.choice(["completed","pending","cancelled"]),
        "payment_method": random.choice(["credit_card","paypal","bank_transfer"]),
        "country": fake.country(),
        "city": fake.city(),
    }

def generate_batch(num_records=1000):
    records = []
    for _ in range(num_records):
        record = generate_sales_record()
        record["total_amount"] = round(
            record["quantity"] * record["unit_price"], 2
        )
        records.append(record)
    return records

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    print("Generating 1000 sales records...")
    records = generate_batch(1000)
    df = pd.DataFrame(records)
    filename = f"data/sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"Done! Saved to {filename}")
    print(df.head())