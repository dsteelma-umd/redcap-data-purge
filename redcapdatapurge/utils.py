def calculate_total_rows_count(db):
    """
    Returns a dictionary of the tables in the database, with
    the count of the number of rows.
    """
    total_rows_count = {}
    for table in db.tables:
        table_class = db.load_table(table)
        total_rows_count[table] = table_class.count()
    return total_rows_count
