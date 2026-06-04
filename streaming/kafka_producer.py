import json
import time
import random
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_generator.generate_sales_data import generate_sales_record

def simulate_kafka_producer(orders_per_second=5, duration_seconds=10):
    print("=" * 50)
    print("KAFKA PRODUCER STARTING")
    print("Streaming " + str(orders_per_second) + " orders/second")
    print("Duration: " + str(duration_seconds) + " seconds")
    print("=" * 50)
    
    total_sent = 0
    messages = []
    end_time = time.time() + duration_seconds
    
    while time.time() < end_time:
        batch = []
        for _ in range(orders_per_second):
            record = generate_sales_record()
            record["total_amount"] = round(
                record["quantity"] * record["unit_price"], 2
            )
            record["event_time"] = datetime.now().isoformat()
            record["partition"] = random.randint(0, 2)
            message = {
                "topic": "sales-orders",
                "partition": record["partition"],
                "offset": total_sent,
                "key": record["order_id"],
                "value": record,
                "timestamp": datetime.now().isoformat()
            }
            batch.append(message)
            messages.append(message)
            total_sent += 1
        
        batch_revenue = sum(m["value"]["total_amount"] for m in batch)
        print("Sent " + str(orders_per_second) + " orders | " +
              "Total: " + str(total_sent) + " | " +
              "Batch Revenue: $" + str(round(batch_revenue, 2)))
        time.sleep(1)
    
    print("=" * 50)
    print("STREAMING COMPLETE!")
    print("Total orders streamed: " + str(total_sent))
    total_revenue = sum(m["value"]["total_amount"] for m in messages)
    print("Total revenue streamed: $" + str(round(total_revenue, 2)))
    
    os.makedirs("data", exist_ok=True)
    output_file = "data/streamed_orders_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
    with open(output_file, "w") as f:
        json.dump(messages, f, indent=2)
    print("Saved to: " + output_file)
    print("=" * 50)
    return messages

if __name__ == "__main__":
    simulate_kafka_producer(orders_per_second=5, duration_seconds=10)