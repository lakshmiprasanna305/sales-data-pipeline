import boto3
import os
import glob
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-2")
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "sales-pipeline-lakshmi")
REGION = os.getenv("AWS_REGION", "us-east-2")

def create_bucket():
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print("Bucket exists: " + BUCKET_NAME)
    except Exception as e:
        print("Creating bucket...")
        s3_client.create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={"LocationConstraint": REGION}
        )
        print("Bucket created!")

def upload_file(local_path):
    now = datetime.now()
    key = "raw/sales/year=" + str(now.year) + "/month=" + str(now.month) + "/day=" + str(now.day) + "/" + os.path.basename(local_path)
    s3_client.upload_file(local_path, BUCKET_NAME, key)
    print("Uploaded: " + key)

def list_files():
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="raw/")
    files = [obj["Key"] for obj in response.get("Contents", [])]
    print("Files in S3: " + str(len(files)))

create_bucket()
files = glob.glob("data/*.csv")
if files:
    latest = max(files)
    print("Uploading: " + latest)
    upload_file(latest)
    print("Done!")
    list_files()
else:
    print("No CSV files found! Run generate_sales_data.py first!")