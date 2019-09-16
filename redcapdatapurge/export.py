from pprint import pprint
import json

def get_rels(db):
    rels = {}
    keys = sorted(set.union(set(db.fwd_table_relations.keys()), set(db.rev_table_relations.keys())))
    for key in keys:
        rels[key] = {}
        rels[key]['forward'] = {}
        rels[key]['reverse'] = {}
        f_rels = db.fwd_table_relations.get(key) or []
        for f_rel in f_rels:
            rels[key]['forward'][f_rel] = f_rels[f_rel]
        r_rels = db.rev_table_relations.get(key) or []
        for r_rel in r_rels:
            rels[key]['reverse'][r_rel] = r_rels[r_rel]
    return rels

def print_rels(db):
    rels = get_rels(db)
    pprint(rels)
    print(f'Total tables: {len(rels.keys())}')

def serialize_rels(db):
    with open('table_rels.json', 'w') as fp:
       json.dump(get_rels(db), fp)

def print_tables_with_project_id(db):
    print(f'Num: {len(db.tables_with_project_id)}')
    pprint(db.tables_with_project_id)

def print_primary_keys(db):
    for tbl in db.primary_keys:
        # print(tbl, db.primary_keys[tbl])
        if not db.primary_keys[tbl]: print(tbl, db.primary_keys[tbl])

def print_full_summary_to_file(db, project_ids, filename):
    with open(filename, 'w') as fp:
        # Total Tables Count
        fp.write(f'Total Tables Count: {len(db.db.tables)}\n')
        fp.write(f'\n')

        # List out Tables
        for table in db.db.tables:
            fp.write(f'Table: {table}\n')
            fp.write(f'  total rows: {db.total_rows_count[table]}\n')
            total_related_rows = 0
            if len(db.related_item_ids[table]) > 0:
                values = ""
                for value in db.related_item_ids[table]:
                    q_value = value if isinstance(value, int) else f"'{value}'"
                    values = f'{values}, {q_value}' if values else q_value
                related_rows_query = f'SELECT COUNT(*) c FROM {table} WHERE {db.primary_keys[table]} IN ({values})'
                result = db.db.query(related_rows_query)
                total_related_rows = result.next()['c']

            fp.write(f'  total related rows: {total_related_rows}\n')
            fp.write(f'  total unrelated rows: {db.total_rows_count[table]-total_related_rows}\n')
            fp.write('\n')
            fp.write('\n')

        # List Usernames
        user_ids = list(db.related_item_ids['redcap_user_information'])
        user_ids_str = ','.join(str(x) for x in user_ids)
        query = f'SELECT username from redcap_user_information where ui_id IN ({user_ids_str})'
        results = db.db.query(query)
        fp.write('')
        fp.write('Usernames: \n')
        for row in results:
            fp.write(f'  {row["username"]}\n')
        

