import json
from .redcapdb import RedCapDB
from .export import print_rels, print_tables_with_project_id, serialize_rels, print_primary_keys, print_full_summary_to_file
from . import utils

def main():

    # TODO: Get values from config file / command-line instead
    db_url = 'mysql://redcap:<PASSWORD>@127.0.0.1/redcap'
    summary_file = ''
    purge_queries_file = ''
    related_item_ids_file = ''

    db = RedCapDB(db_url)
    db.calculate_total_rows_count()

    usernames = ['dyarnell', 'dmilton', 'sbobbin', 'jbueno', 'balbert', 'rwashing', 'sy344', 'dmilton2', 'adenaiye', 'vdemaio', 'imoleayof19', 'amarafox', 'tgold', 'stefanos', 'Ali98', 'lynch17', 'magidya', 'mmistret', 'tomiokanlawon', 'abhipat', 'micah38', 'melaynap', 'shirarubin37', 'jsolow', 'cstipa', 'msuh1145', 'sswanzy04', 'Lwakefie', 'jmarron', 'fhong', 'gmagno', 'rezeugoh', 'dmilton_api', 'jgerman', 'calilung']
    project_ids = [35, 36, 38, 39, 40, 41, 42, 47, 48, 49, 50, 52, 54, 55, 58, 60, 61, 63, 64, 65, 66, 67, 68, 73, 82, 89, 90, 92, 94, 99, 100, 101, 110, 117, 118, 119, 120, 123, 124, 179, 180, 311]

    # Load related_item_ids from file
    # with open('related_item_ids_35_311.json', 'r') as fp:
    #     related_item_ids = json.load(fp)
    #     db.related_item_ids = {}
    #     for table in related_item_ids:
    #         db.related_item_ids[table] = set(related_item_ids[table])
    
    # project_ids    = [35,311]
    for project_id in project_ids:
        db.identify_dependents_by_project_id(project_id)
    #     db.print_related_items()
    # db.print_related_items_count()

    for username in usernames:
        db.identify_dependents_by_username(username)

    purge_queries = db.calculate_purge_queries()

    with open(related_item_ids_file, 'w') as fp:
        json.dump(db.related_item_ids, fp, default=utils.set_as_list)

    with open(purge_queries_file, 'w') as fp:
        fp.write('\n'.join(purge_queries))

    print_full_summary_to_file(db, project_ids, summary_file)
    
    # with open('related_item_ids_tmp.json', 'r') as fp:
    #     related_item_ids = json.load(fp)
    #     status = compare_related_item_ids(db.related_item_ids, related_item_ids)
    #     print(f'Attempt status: {status}')

    # Verify usernames exist

if __name__ == '__main__':
    main()

