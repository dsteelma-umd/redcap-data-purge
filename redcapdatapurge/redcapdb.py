import dataset

class RedCapDB():
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.db = dataset.connect(connection_string)

        self.current_project_id = None
        self.primary_keys = {}
        self.related_item_ids = {}
        self.tables_with_project_id = []
        self.unrelated_tables_with_project_id = []
        self.fwd_table_relations = {}
        self.rev_table_relations = {}
        self.track_traversal = {}
        self.purge_queries = []
        self.total_rows_count = {}

        for table in self.db.tables:
            self.track_traversal[table] = {}
            self.related_item_ids[table] = set()

            table_class = self.db.load_table(table)
            rev_rel = {}
            f'{table} -> {table_class} -> {table_class._table}'
            # print(f'{table} -> {table_class} -> {table_class._table}')
            for fk in table_class._table.foreign_keys:
                l_col = fk.constraint.column_keys[0]
                f_table = fk.column.table.name
                f_col = fk.column.name
                if l_col not in rev_rel: rev_rel[l_col] = []
                rev_rel[l_col].append([f_table, f_col])
                if f_table not in self.fwd_table_relations: self.fwd_table_relations[f_table] = {}
                if f_col not in self.fwd_table_relations[f_table]: self.fwd_table_relations[f_table][f_col] = []
                self.fwd_table_relations[f_table][f_col].append([table, l_col])
            self.rev_table_relations[table] = rev_rel
            if table not in self.fwd_table_relations: self.fwd_table_relations[table] = {}
            
            self.primary_keys[table] = [pk.key for pk in table_class._table.primary_key.columns]
            if 'project_id' in table_class.columns:
                self.tables_with_project_id.append(table)

        for pk_table in self.primary_keys:
            if pk_table in self.tables_with_project_id:  self.primary_keys[pk_table] = 'project_id'
            elif len(self.primary_keys[pk_table]) > 0: self.primary_keys[pk_table] = self.primary_keys[pk_table][0]
            else: self.primary_keys[pk_table] = None

        prj_rel_tbls = [rel[0] for rel in self.fwd_table_relations['redcap_projects']['project_id']]
        for tbl in self.tables_with_project_id:
            if tbl not in prj_rel_tbls:
                self.unrelated_tables_with_project_id.append(tbl)
        self.unrelated_tables_with_project_id.append('redcap_projects')

        self.configure_primary_key_overrides()
        self.initialize_skip_rules()

    def initialize_skip_rules(self):
        self.skip_traverse_rels = []
        self.skip_traverse_rels.append(['redcap_user_information', 'redcap_surveys_emails'])
        self.skip_traverse_rels.append(['redcap_user_information', 'redcap_data_quality_resolutions'])
        self.skip_traverse_rels.append(['redcap_user_information', 'redcap_folders'])
        self.skip_traverse_rels.append(['redcap_user_information', 'redcap_messages'])
        self.skip_traverse_rels.append(['redcap_user_information', 'redcap_messages_recipients'])
        self.skip_traverse_rels.append(['redcap_user_information', 'redcap_mobile_app_files'])
        self.skip_tables = ['redcap_log_view', 'redcap_log_view_requests', 'redcap_page_hits']
        self.skip_traverse_tables = ['redcap_events_metadata', 'redcap_surveys_emails']
        self.skip_reverese_traverse_tables = ['redcap_user_information']
        self.single_traverse_tables = ['redcap_messages_status']
        self.no_traverse = False

    def configure_primary_key_overrides(self):
        self.primary_keys['redcap_auth_history'] = 'username'
        self.primary_keys['redcap_ddp_log_view_data'] = 'ml_id'
        self.primary_keys['redcap_ehr_access_tokens'] = 'access_token'
        self.primary_keys['redcap_ehr_user_map'] = 'ehr_username'
        self.primary_keys['redcap_events_forms'] = 'event_id'
        self.primary_keys['redcap_events_repeat'] = 'event_id'
        self.primary_keys['redcap_ip_cache'] = 'ip_hash'
        self.primary_keys['redcap_reports_fields'] = 'report_id'
        self.primary_keys['redcap_surveys_login'] = 'response_id'
        self.primary_keys['redcap_surveys_pdf_archive'] = 'doc_id'
        self.primary_keys['redcap_surveys_response_users'] = 'response_id'
        self.primary_keys['redcap_surveys_short_codes'] = 'participant_id'
        self.primary_keys['redcap_validation_types'] = 'validation_name'

    def calculate_total_rows_count(self):
        for table in self.db.tables:
            table_class = self.db.load_table(table)
            self.total_rows_count[table] = table_class.count()

    def get_summary(self):
        tables_summary = {}
        for table in self.db.tables:
            count_query = f'SELECT COUNT(*) c FROM {table}'
            result = self.db.query(count_query)            
            num_rows = result.next()['c']
            tables_summary[table] = num_rows
        return tables_summary

    def print_constraints(self, table):
        constraint_query = f'SHOW CREATE TABLE {table}'
        result = self.db.query(constraint_query)
        for r in result:
            for k in r:
                print(k)
                print(r[k])

    def _print_tables(self):
        for table in self.db.tables:
            print(table)

    def add_ids_for_table_by_field(self, table, field, value, src_table, src_field):
        if [src_table, table] in self.skip_traverse_rels: return
        if table in self.skip_tables: return
        if (table == 'redcap_projects' and field == 'project_id') and value != self.current_project_id: return
        if field not in self.track_traversal[table]: self.track_traversal[table][field] = set()
        if value in self.track_traversal[table][field]: return
        self.track_traversal[table][field].add(value)
        # print(f'{src_table}.{src_field} -> {table}.{field} ({value})')
        if not self.primary_keys[table]: self.primary_keys[table] = [field]
        pk = self.primary_keys[table]
        f_rels = self.fwd_table_relations[table]
        r_rels = self.rev_table_relations[table]
        related_fields = list(f_rels.keys()) + list(r_rels.keys())
        fields = set.union(set([pk]), set(related_fields))
        if table in self.tables_with_project_id: fields.add('project_id')
        fields_string = ', '.join(fields)
        q_value = value if isinstance(value, int) else f"'{value}'"
        query = f'SELECT {fields_string} FROM {table} WHERE {field}={q_value}'
        for row in self.db.query(query):
            if 'project_id' in row and row['project_id'] != self.current_project_id: continue
            if row[pk] in self.related_item_ids[table]: continue
            self.related_item_ids[table].add(row[pk])

            # if self.no_traverse: continue
            if table in self.skip_traverse_tables: continue
            # if src_table in self.single_traverse_tables: continue

            # Add forward relations
            for l_col in f_rels:
                val = row[l_col]
                if not val: continue
                for f_rel in f_rels[l_col]:
                    f_tab, f_col = f_rel
                    # if f_tab in self.tables_with_project_id:
                    #     f_col = 'project_id'
                    #     val = self.current_project_id
                    if not ((f_tab == src_table) and (f_col == src_field)):
                        self.add_ids_for_table_by_field(f_tab, f_col, val, table, field)

            # Add reverse relations
            if table not in self.skip_reverese_traverse_tables:
                for l_col in r_rels:
                    val = row[l_col]
                    if not val: continue
                    for r_rel in r_rels[l_col]:
                        r_tab, r_col = r_rel
                                # if r_tab in self.tables_with_project_id:
                                #     r_col = 'project_id'
                                #     val = self.current_project_id
                        if not ((r_tab == src_table) and (r_col == src_field)):
                            self.add_ids_for_table_by_field(r_tab, r_col, val, table, field)


    def identify_dependents_by_project_id(self, id):
        self.current_project_id = id
        # project = self.session.query(self.projects).get(id)
        for table in self.unrelated_tables_with_project_id:
            print(f'Looking table: {table} for items with project_id: {id}')
            
            # if table in self.unrelated_tables_with_project_id:
            #     self.no_traverse = False
            self.add_ids_for_table_by_field(table, 'project_id', id, None, None)
            # else:
            #     self.no_traverse = True
            #     self.add_ids_for_table_by_field(table, 'project_id', id, None, None)


    def identify_dependents_by_username(self, username):
        self.current_project_id = None
            
        self.add_ids_for_table_by_field('redcap_user_information', 'username', username, None, None)


    def calculate_purge_queries(self):
        self.purge_queries = []
        for table in self.related_item_ids:
            field = self.primary_keys[table]
            values = ""
            if not self.related_item_ids[table]: continue
            for value in self.related_item_ids[table]:
                q_value = value if isinstance(value, int) else f"'{value}'"
                values = f'{values}, {q_value}' if values else q_value
            query = f'DELETE FROM {table} WHERE {field} NOT IN ({values})'
            self.purge_queries.append(query)
        return self.purge_queries