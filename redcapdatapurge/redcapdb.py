import dataset

class RedCapDB():
    def __init__(self, connection_string):
        self.connection_string = connection_string

        # Connect to the database using the dataset library
        self.db = dataset.connect(connection_string)

        # Initialize Tracking Vars
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

        # For each table in the database
        for table in self.db.tables:
            # Initialize placeholder collection with table name as the key
            self.track_traversal[table] = {}
            self.related_item_ids[table] = set()

            # Get the table class (Auto Loaded by Sqlalchemy)
            table_class = self.db.load_table(table)

            # Var to track reverse relationship
            rev_rel = {}
            #f'{table} -> {table_class} -> {table_class._table}'
            print(f'{table} -> {table_class} -> {table_class._table}')

            # Iterate through foreign keys of the table
            for fk in table_class._table.foreign_keys:
                l_col = fk.constraint.column_keys[0]
                f_table = fk.column.table.name
                f_col = fk.column.name

                # Add the local column, foriegn table and column to reverse relationship list 
                if l_col not in rev_rel: rev_rel[l_col] = []
                rev_rel[l_col].append([f_table, f_col])

                # Add the inverse relationship to forward relationship list 
                if f_table not in self.fwd_table_relations: self.fwd_table_relations[f_table] = {}
                if f_col not in self.fwd_table_relations[f_table]: self.fwd_table_relations[f_table][f_col] = []
                self.fwd_table_relations[f_table][f_col].append([table, l_col])

            # Add the reverse relationship var
            self.rev_table_relations[table] = rev_rel

            # To avoid key presense tests
            if table not in self.fwd_table_relations: self.fwd_table_relations[table] = {}
            
            # Get the primary key of the table
            self.primary_keys[table] = [pk.key for pk in table_class._table.primary_key.columns]

            # Track all tables that has 'project_id' column
            if 'project_id' in table_class.columns:
                self.tables_with_project_id.append(table)

        # Set a single column as the primary tracking column for the table, even if has multiple column primary key
        for pk_table in self.primary_keys:
            # Use 'project_id' as the tracking column if the table has it
            if pk_table in self.tables_with_project_id:  self.primary_keys[pk_table] = 'project_id'
            # If the table has multiple primary keys, use the first one as the tracking column
            elif len(self.primary_keys[pk_table]) > 0: self.primary_keys[pk_table] = self.primary_keys[pk_table][0]
            else: self.primary_keys[pk_table] = None

        # Identify tables that are realted to the 'redcap_projects' table
        prj_rel_tbls = [rel[0] for rel in self.fwd_table_relations['redcap_projects']['project_id']]

        # Identify tables that have 'project_id' column but do not have relationship with the 'redcap_projects' table
        for tbl in self.tables_with_project_id:
            if tbl not in prj_rel_tbls:
                self.unrelated_tables_with_project_id.append(tbl)
        
        # Add 'redcap_projects' to the unrelated_tables_with_project_id list
        # tables in this list will be directly queried to identify data related to 'project_id'
        self.unrelated_tables_with_project_id.append('redcap_projects')

        # Manual primary key overrides
        self.configure_primary_key_overrides()

        # Manual skip rules (tables or relationships to be skipped during recursive traversals)
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

    # Used find total rows in each table
    def calculate_total_rows_count(self):
        for table in self.db.tables:
            table_class = self.db.load_table(table)
            self.total_rows_count[table] = table_class.count()

    # Used to print contraints of each table
    def print_constraints(self, table):
        constraint_query = f'SHOW CREATE TABLE {table}'
        result = self.db.query(constraint_query)
        for r in result:
            for k in r:
                print(k)
                print(r[k])

    # Print table names of all tables in the database
    def _print_tables(self):
        for table in self.db.tables:
            print(table)

    # Recursivley traverse tables and identify and track related data rows
    def add_ids_for_table_by_field(self, table, field, value, src_table, src_field):
        # Skip if the traversal matches any of the skip rules
        if [src_table, table] in self.skip_traverse_rels: return
        if table in self.skip_tables: return
        if (table == 'redcap_projects' and field == 'project_id') and value != self.current_project_id: return
        if field not in self.track_traversal[table]: self.track_traversal[table][field] = set()
        if value in self.track_traversal[table][field]: return

        # Add the value to traversed values for the table-column being traversed by
        self.track_traversal[table][field].add(value)

        # print(f'{src_table}.{src_field} -> {table}.{field} ({value})')

        # If the table does not have any primary tracking key, use the current traverse field
        # as the primary tracking key
        if not self.primary_keys[table]: self.primary_keys[table] = [field]

        # Get the primary tracking for the table
        pk = self.primary_keys[table]

        # Get the relationships for the table
        f_rels = self.fwd_table_relations[table]
        r_rels = self.rev_table_relations[table]
        related_fields = list(f_rels.keys()) + list(r_rels.keys())

        # Fields to be retrieved from the database
        fields = set.union(set([pk]), set(related_fields))
        if table in self.tables_with_project_id: fields.add('project_id')

        # Generate the SQL query to retrieve tracking fields and relationship fields
        fields_string = ', '.join(fields)
        q_value = value if isinstance(value, int) else f"'{value}'"
        query = f'SELECT {fields_string} FROM {table} WHERE {field}={q_value}'

        # traverse and track each retrieved row
        for row in self.db.query(query):
            # Skip to next row if project id does not match the initial project_id 
            # that started the traversal 
            if 'project_id' in row and row['project_id'] != self.current_project_id: continue

            # If the current row's tracking ID value already tracked, skip to next
            if row[pk] in self.related_item_ids[table]: continue

            # Add current row's tracking ID value to the tracking list
            self.related_item_ids[table].add(row[pk])

            # if self.no_traverse: continue

            # Skip traversing, if current table should not be traversed
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

    # For each table containing the 'project_id' column but not related to the 'redcap_projects'
    # table, 
    def identify_dependents_by_project_id(self, id):
        self.current_project_id = id
        # project = self.session.query(self.projects).get(id)
        for table in self.unrelated_tables_with_project_id:
            print(f'Looking table: {table} for items with project_id: {id}')
            
            # Traverse and track related data
            self.add_ids_for_table_by_field(table, 'project_id', id, None, None)

            # if table in self.unrelated_tables_with_project_id:
            #     self.no_traverse = False
            #     self.add_ids_for_table_by_field(table, 'project_id', id, None, None)
            # else:
            #     self.no_traverse = True
            #     self.add_ids_for_table_by_field(table, 'project_id', id, None, None)


    # For the username provided, identify related data by traversing from the 'redcap_user_information'
    # table
    def identify_dependents_by_username(self, username):
        self.current_project_id = None
        self.add_ids_for_table_by_field('redcap_user_information', 'username', username, None, None)

    # Generate SQL DELETE quries based on the identified and tracked related data
    def calculate_purge_queries(self):
        self.purge_queries = []
        for table in self.related_item_ids:
            field = self.primary_keys[table]
            values = ""
            if not self.related_item_ids[table]: continue
            for value in self.related_item_ids[table]:
                q_value = value if isinstance(value, int) else f"'{value}'"
                values = f'{values}, {q_value}' if values else q_value
            query = f'DELETE FROM {table} WHERE {field} NOT IN ({values});'
            self.purge_queries.append(query)
        return self.purge_queries