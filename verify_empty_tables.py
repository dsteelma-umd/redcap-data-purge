import os
import dataset
from dotenv import load_dotenv
from redcapdatapurge.utils import calculate_total_rows_count

load_dotenv()


def verify_empty_tables(table_row_count):
    """
    Verifies that the expected tables have no entries, as they are not
    processed by the script.
    """
    expected_empty_tables = {
        'redcap_external_modules_log',
        'redcap_external_modules_log_parameters',
        'redcap_instrument_zip',
        'redcap_instrument_zip_authors',
        'redcap_ip_banned',
        'redcap_projects_external',
        'redcap_pub_articles',
        'redcap_pub_authors',
        'redcap_pub_matches',
        'redcap_pub_mesh_terms',
        'redcap_user_whitelist'
    }

    for t in expected_empty_tables:
        try:
            count_for_table = table_row_count[t]
            if count_for_table is None:
                print(f"ERROR: Expected empty table '{t}' not found in row count.")
                exit(1)
            if count_for_table != 0:
                print(f"Error: Expected empty table '{t}' had {count_for_table} rows.")
                exit(1)
        except KeyError:
            print(f"ERROR: Expected empty table '{t}' not found in row count.")
            exit(1)

    return True


required_env_vars = ["DB_URL"]
for var in required_env_vars:
    if not os.getenv(var):
        print(f"Required environment variable '{var}' is missing.")
        exit(1)

db_url = os.getenv("DB_URL")
db = dataset.connect(db_url)

total_rows_count = calculate_total_rows_count(db)
if verify_empty_tables(total_rows_count):
    print("SUCCESS. All expected empty tables are actually empty.")
