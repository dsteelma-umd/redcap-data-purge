import os
import dataset
from dotenv import load_dotenv
from redcapdatapurge.utils import calculate_total_rows_count

load_dotenv()


def retrieve_files_list(db):
    """
    Returns a list of all files in the "redcap_docs_to_edocs" and
    "redcap_sendit_docs" tables.
    """
    files_tables_with_filename_field = [
        {'table': 'redcap_edocs_metadata', 'field': 'stored_name'},
        {'table': 'redcap_sendit_docs', 'field': 'doc_name'},
    ]

    # Use Set to eliminate any duplicates
    file_set = set()

    for t in files_tables_with_filename_field:
        table = t['table']
        field = t['field']

        rows = db[table].all()
        for r in rows:
            file_set.add(r[field])

    # Return as list
    return list(file_set)


required_env_vars = ["DB_URL"]
for var in required_env_vars:
    if not os.getenv(var):
        print(f"Required environment variable '{var}' is missing.")
        exit(1)

db_url = os.getenv("DB_URL")
db = dataset.connect(db_url)

file_list = retrieve_files_list(db)

# Dump list to standard out
for file in file_list:
    print(file)
