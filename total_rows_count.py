import os
import dataset
from dotenv import load_dotenv
from redcapdatapurge.utils import calculate_total_rows_count

load_dotenv()

required_env_vars = ["DB_URL", "SUMMARY_OUTPUT_FILE",
                     "PURGE_QUERIES_OUTPUT_FILE", "RELATED_ITEM_IDS_OUTPUT_FILE"]
for var in required_env_vars:
    if not os.getenv(var):
        print(f"Required environment variable '{var}' is missing.")
        exit(1)

# Get values from .env config file
db_url = os.getenv("DB_URL")
db = dataset.connect(db_url)

total_rows_count = calculate_total_rows_count(db)
print("Total Rows Count (table: row count")
print("----------------------------------")

for table, row_count in total_rows_count.items():
    print(f"{table}: {row_count}")
