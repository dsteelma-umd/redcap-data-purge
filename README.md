# Redcap Data Purge

## Introduction

Tool to purge Redcap database and files directory to just keep data from
specified projects.

**NOTE**: This is a work in progress and need code cleanup and reorganization.

## Getting Started

### Prerequisites

The following prerequisites are required for this application:

* Python 3.7
* pip

### Application Setup

1) Clone the repository

2) Switch into the root directory of the applicationL

    ```
    > cd redcap-data-purge
    ```

3) Create a virtual environment in an "venv" subdirectory:

    ```
    > python3 -m venv venv
    ```

4) Activate the virtual environment:

    ```
    > source venv/bin/activate
    ```

5) Using "pip", Install the required dependencies:

    ```
    > pip install -r requirements.txt
    ```

6) Copy the "env_example" file to ".env" and edit the .env file with your
   environment information:

    ```
    cp env_example .env
    ```

## Development Database

Due to security considerations, the data on the servers should not be copied
off of the servers.

For development, the  RedCap development database server server can be used.
The MySQL database from the production server can be copied back to the dev
server. See the ["Clone RedCap database"][clone_redcap_db] page in Confluence
for more information.

### Connecting to the development database server from a workstation

1) Create an SSH tunnel from your local machine to the "redcapdbdev" server:

```
> ssh <USERNAME>@redcapdevdb.lib.umd.edu -L 3306:127.0.0.1:3306 -N
``` 

replacing \<USERNAME> with your username. For example, if your username is
"jsmith":

```
> ssh jsmith@redcapdevdb.lib.umd.edu -L 3306:127.0.0.1:3306 -N
``` 

2) In the ".env" file, the "DB_URL" can then be set at:

```
DB_URL=mysql://redcap:<DB_PASSWORD>@127.0.0.1:3306/redcap
```

where \<DB_URL> is the database password. The database password can be found
in the "Identities" document on the "SSDR" Google Team Drive.

## RedCap Database Purge

There are 119 tables in the "redcap" database. For purposes of the database
purge, these tables can be divided into the following categories:

* The "redcap_projects" table and its child tables
* The "redcap_user_information" table and its child tables
* Unattached tables that contain a "project_id" field
* Unattached tables that contain a "username" field
* Tables with no records
* Tables used for RedCap application configuration that should be kept
* Tables used for RedCap application configuration that should be cleared

A "child" table is a table that contains a foreign key with a "CASCADE DELETE"
relationship to the parent table. This means that a deletion of a row in
the parent table will automatically cause the deletion of related rows in
the child table. There can be multiple levels of cascade deletion.

For the purposes of this application, an "unattached" table is a table that does
not have a foreign key relationship with either the "redcap_projects" or
"redcap_user_information_table", but do contain either a "project_id" or
"username" field. This tables are considered "unattached" because deleting
a record in the "redcap_projects" or "redcap_user_information" tables will
not have any affect on these tables. Therefore separate SQL statements are
needed to handle purging for these tables.

### "redcap_projects" table and its child tables

The following is the list of the "redcap_projects" table and its descendent
tables. All of these tables will be affected by the deletion of a row in
"redcap_projects" table:

* redcap_projects
    * redcap_actions
    * redcap_data_access_groups
    * redcap_data_dictionaries
    * redcap_data_quality_rules
    * redcap_data_quality_status
        * redcap_data_quality_resolutions
    * redcap_ddp_log_view
        * redcap_ddp_log_view_data
    * redcap_ddp_mapping
    * redcap_ddp_preview_fields
    * redcap_ddp_records
        * redcap_ddp_records_data
    * redcap_docs
        * redcap_docs_to_edocs
    * redcap_ehr_user_projects
    * redcap_esignatures
    * redcap_events_arms
        * redcap_events_metadata
            * redcap_events_forms
            * redcap_events_repeat
    * redcap_events_calendar
    * redcap_external_links
        * redcap_external_links_dags
        * redcap_external_links_users
    * redcap_external_links_exclude_projects
    * redcap_external_module_settings
    * redcap_folders_projects
    * redcap_library_map
    * redcap_locking_data
    * redcap_locking_labels
    * redcap_metadata
    * redcap_metadata_archive
    * redcap_metadata_prod_revisions
    * redcap_metadata_temp
    * redcap_mobile_app_devices
    * redcap_mobile_app_log
    * redcap_new_record_cache
    * redcap_project_checklist
    * redcap_projects_templates
    * redcap_randomization
        * redcap_randomization_allocation
    * redcap_record_counts
    * redcap_record_dashboards
    * redcap_reports
        * redcap_reports_access_dags
        * redcap_reports_access_roles
        * redcap_reports_access_users
        * redcap_reports_fields
        * redcap_reports_filter_dags
        * redcap_reports_filter_events
    * redcap_surveys
        * redcap_surveys_emails
            * redcap_surveys_emails_recipients
                * redcap_surveys_scheduler_queue
        * redcap_surveys_participants
            * redcap_surveys_response
                * redcap_surveys_login
                * redcap_surveys_response_users
            * redcap_surveys_short_codes
        * redcap_surveys_pdf_archive
        * redcap_surveys_queue
        * redcap_surveys_scheduler
    * redcap_surveys_erase_twilio_log
    * redcap_surveys_phone_codes
    * redcap_surveys_queue_hashes
    * redcap_surveys_response_values
    * redcap_user_rights
    * redcap_user_roles
    * redcap_web_service_cache

### "redcap_user_information" table and its child tables

The following is the list of the "redcap_user_information" table and its descendent
tables. All of these tables will be affected by the deletion of a row in
"redcap_user_information" table:

* redcap_user_information
    * redcap_actions
    * redcap_ehr_access_tokens
    * redcap_ehr_user_map
    * redcap_ehr_user_projects
    * redcap_folder_projects
    * redcap_folders
    * redcap_folders_projects
    * redcap_messages
    * redcap_messages_recipients
    * redcap_messages_status
    * redcap_surveys_themes
    * redcap_todo_list
    * redcap_two_factor_response

### Unattached tables that contain a "project_id" field

The following tables are not associated with the "redcap_projects" table via
a foreign key, but contain a "project_id" field, so must be handled
individually:

* redcap_data
* redcap_edocs_metadata
    * edcap_mobile_app_files
* redcap_log_event 

### Unattached tables that contain a "username" field

The following tables are not associated with the "redcap_user_information" table
via a foreign key, but contain a "username" field, so must be handled
individually:

* redcap_auth
* redcap_auth_history
* redcap_sendit_docs
    * redcap_sendit_recipients (Transitive through "document_id" on "redcap_sendit_docs)


### Tables with no records

The following tables have no records, so do not need to be purged:

* redcap_external_modules_log
* redcap_external_modules_log_parameters
* redcap_instrument_zip
* redcap_instrument_zip_authors
* redcap_ip_banned
* redcap_projects_external
* redcap_pub_articles
* redcap_pub_authors
* redcap_pub_matches
* redcap_pub_mesh_terms
* redcap_user_whitelist

### Tables used for RedCap application configuration that should be kept

The following tables are used by RedCap for application configuration. They
do not contain a "project_id" or "username" field, but do contain
configuration or other information related to the running of the RedCap
application:

* redcap_auth_questions
* redcap_config
* redcap_crons
* redcap_external_modules
* redcap_external_modules_downloads
* redcap_history_version
* redcap_instrument_zip_origins
* redcap_messages_threads
* redcap_pub_sources
* redcap_validation_types

### Tables used for RedCap application configuration that should be cleared
The following tables are used by RedCap for application configuration. They
do not contain a "project_id" or "username" field, and typically contain
usage history information that it is not necessary to maintain when
migrating a "clean" database copy:

* redcap_crons_history
* redcap_dashboard_ip_location_cache
* redcap_history_size
* redcap_ip_cache
* redcap_log_view
* redcap_log_view_requests
* redcap_page_hits
* redcap_sessions
* redcap_surveys_emails_send_rate


## Usage

To generate the files to use in purging the database:

```
> python -m redcapdatapurge <PROJECT_IDS_TO_KEEP_FILE> <USER_NAMES_TO_KEEP_FILE>
```

where \<PROJECT_IDS_TO_KEEP_FILE> is a file containing the project ids to keep
(one per line), and \<USER_NAMES_TO_KEEP_FILE> is a file containing the user
names to keep (one per line). See `example_project_ids_to_keep.txt` and
`example_user_names_to_keep.txt` as examples.

**Note:** The "USER_NAMES_TO_KEEP_FILE" should contain an a "site-admin" entry,
as that appears to be required by the RedCap application.

The following files are produced:

* Cleanup (CLEANUP_OUTPUT_FILE)
* Purge Queries (PURGE_QUERIES_OUTPUT_FILE)
* RedCap Admin Purge Queries (REDCAP_ADMIN_PURGE_QUERIES_OUTPUT_FILE)

### Cleanup (CLEANUP_OUTPUT_FILE)

While writing this application, it was observed that some tables associated
with project_ids or usernames still contained records, even after all the
entries were deleted from the "redcap_projects" and "redcap_user_information"
tables. These "orphaned" records indicate that there was a referential integrity
issue at some point in the RedCap application's life, in which a project or
user was deleted and all the related records were not properly cleaned up.

The values used in the SQL statements in this file were discovered by deleting
all the records from the "redcap_projects" and "redcap_user_information", and
then seeing which records were left in the tables that had foreign keys with
"CASCADE DELETE" (i.e., the tables in the
'"redcap_projects" table and its child tables' and
'"redcap_user_information" table and its child tables' sections above).

This SQL file SHOULD be run when creating a "clean" database for transferring
a set of records. It is not necessary to run the script in other circumstances,
but seems advisable as a cleanup step.

### Purge Queries (PURGE_QUERIES_OUTPUT_FILE)

This SQL file contains the queries to delete project and user-related data
from all tables, preserving only those entries for the provided project ids
and usernames.

### RedCap Admin Purge Queries (REDCAP_ADMIN_PURGE_QUERIES_OUTPUT_FILE)

This SQL file contains queries for deleting RedCap administrative/usage
information that is not needed for a database transfer.

This SQL file SHOULD be run when creating a "clean" database for transferring
a set of records.

This SQL file SHOULD NOT be run against a database where the usage history
should be preserved.

## Helper Scripts

The following scripts are designed to perform a specific function, unrelated
to the actual purge SQL file generation:

### total_rows_counts.py

Prints a list of all the tables in the database, with their associated row
counts.

```
> python total_row_counts.py
```

### verify_empty_tables

Verifies that the tables that are expected to be empty are actually empty.

```
> python verify_empty_tables.py
```

### retrieve_files_list.py

Prints (to standard out) a list of all the unique files in the
"redcap_edocs_metadata" and "redcap_sendit_docs" tables that may be in
the "edocs" directory of the RedCap server.

```
> python retrieve_files_list.py
```

To send the output to a file (such as "file_list.txt"), simply use a Unix pipe:

```
> python retrieve_files_list.py > file_list.txt
```

This list can be used with the Unix "tar" or "rm" commands to store or remove
all the files.

For example, to create an "allfiles.tar" tar archive containing all the files
in the list:
 
1) Copy the file list to the "/apps/redcap/edocs" directory of the RedCap
server.

2) Run the following command:

```
> tar -cvf allfiles.tar -T file_list.txt
```

**Note:** There is no guarantee that all the files will actually be present,
so the tar command may report some missing files (and exit with 
"Exiting with failure status due to previous errors").

For deleting all the files listed in the file, [Stack Overflow](https://stackoverflow.com/a/5142498)
suggests:

```
> xargs rm < file_list.txt
```

**Note:** This command has not been tested.

## Scenario: Creating Database for Transfer

The following steps are provided as an example of how to create a "clean"
RedCap database containing only information for a particular set of project ids
and user names.

1) Follow the steps in the "Application Setup" section, including copying
the "env_example" file to ".env" and filling out the parameters. For
the following steps, the following parameters were used for the filenames:

| Parameter | Value |
|-----------|-------|
|CLEANUP_OUTPUT_FILE|/tmp/cleanup.sql|
|PURGE_QUERIES_OUTPUT_FILE|/tmp/purge_queries_output.sql|
|REDCAP_ADMIN_PURGE_QUERIES_OUTPUT_FILE|/tmp/redcap_admin_purge_queries_output.sql|

Be sure to also fill out the "DB_URL" parameter.

2) Create a "project_ids_to_keep.txt" file containing only the project ids
of the projects that should be transferred. See "example_project_ids_to_keep.txt"
for an example. The project ids should be provided one per line.

3) Create a "user_names_to_keep.txt" file containing only the user names
that should be transferred. Be sure to include the "site-admin" user, as that
is needed by some RedCap functionality. See "example_user_names_to_keep.txt"
for an example.

4) Run the "verify_empty_tables.py" script to verify that all the tables that
are expected to be empty are actually empty:

```
> python verify_empty_tables.py
```

5) Run the "redcapdatapurge" command:

```
> python -m redcapdatapurge project_ids_to_keep.txt user_names_to_keep.txt
```

The following files are produced:

* /tmp/cleanup.sql
* /tmp/purge_queries_output.sql
* /tmp/redcap_admin_purge_queries_output.sql

6) Copy the files to the "/tmp" directory on the RedCap database server (in the
following examples the "redcapdevdb.lib.umd.edu" server is used). Replace
"jsmith" with your username:

```
> scp /tmp/cleanup.sql jsmith@redcapdevdb.lib.umd.edu:/tmp
> scp /tmp/purge_queries_output.sql jsmith@redcapdevdb.lib.umd.edu:/tmp
> scp /tmp/redcap_admin_purge_queries_output.sql jsmith@redcapdevdb.lib.umd.edu:/tmp
```

7) Log in to the RedCap database server.

8) On the RedCap database server, switch to the "db" service account.

9) As the "db" service account user, run the following commands:

```
> mysql -u redcap -p redcap < /tmp/cleanup.sql
> mysql -u redcap -p redcap < /tmp/purge_queries_output.sql
> mysql -u redcap -p redcap < /tmp/redcap_admin_purge_queries_output.sql
```

You will be prompted for the password after each command.

10) At this point take a MySQL database dump of the database. This will be the
be the "database" portion of the transfer.

11) On the workstation, run the following command to create a "file_list.txt"
file of all the files to be transferred from the "edocs" directory on the
RedCap Server:

```
> python retrieve_files_list.py > file_list.txt
```

12) Copy the "file_list.txt" file to the "/tmp" directory of the RedCap server
(in the following examples the "redcapdev.lib.umd.edu" server is used). Replace
"jsmith" with your username:

**Note:** Unless you are certain all the files were transferred from the
production server to the dev server, it is probably better to transfer this
file to the production server, and use the production server in the following
steps.

```
> scp file_list.txt jsmith@redcapdev.lib.umd.edu:/tmp
```

13) Log in to the RedCap server.

14) On the RedCap database server, switch to the "db" service account.

15) As the "db" service account user, run the following commands to create
a "tar" archive of all the files in the "/tmp/file_list.txt" file:

```
> cd /apps/redcap/edocs
> tar -cvf allfiles.tar -T file_list.txt
```

**Note:** There is no guarantee that all the files will actually be present,
so the tar command may report some missing files (and exit with 
"Exiting with failure status due to previous errors").

The "allfiles.tar" constitutes the "files" portion of the transfer.

16) The "database" and "files" comprise all the information that should be
needed for the transfer.

## Scenario: Purging Projects and Usernames

The following steps are provided as an example of how to remove a set of project
ids and user names from an existing RedCap database.

1) Follow the steps in the "Application Setup" section, including copying
the "env_example" file to ".env" and filling out the parameters. For
the following steps, the following parameters were used for the filenames:

| Parameter | Value |
|-----------|-------|
|CLEANUP_OUTPUT_FILE|/tmp/cleanup.sql|
|PURGE_QUERIES_OUTPUT_FILE|/tmp/purge_queries_output.sql|
|REDCAP_ADMIN_PURGE_QUERIES_OUTPUT_FILE|/tmp/redcap_admin_purge_queries_output.sql|

Be sure to also fill out the "DB_URL" parameter.

2) Create a "project_ids_to_keep.txt" file containing the project ids
of the projects that should be kept. See "example_project_ids_to_keep.txt"
for an example. The project ids should be provided one per line.

3) Create a "user_names_to_keep.txt" file containing the user names
that should be kept. Be sure to include the "site-admin" user, as that
is needed by some RedCap functionality. See "example_user_names_to_keep.txt"
for an example.

4) Run the "verify_empty_tables.py" script to verify that all the tables that
are expected to be empty are actually empty:

```
> python verify_empty_tables.py
```

5) Run the "redcapdatapurge" command:

```
> python -m redcapdatapurge project_ids_to_keep.txt user_names_to_keep.txt
```

The following files are produced:

* /tmp/cleanup.sql
* /tmp/purge_queries_output.sql
* /tmp/redcap_admin_purge_queries_output.sql

6) Copy the files to the "/tmp" directory on the RedCap database server (in the
following examples the "redcapdevdb.lib.umd.edu" server is used). Replace
"jsmith" with your username:

**Note:** We do _not_ want to purge the RedCap admin tables, so the
"/tmp/redcap_admin_purge_queries_output.sql" should _not_ be transferred.

```
> scp /tmp/cleanup.sql jsmith@redcapdevdb.lib.umd.edu:/tmp
> scp /tmp/purge_queries_output.sql jsmith@redcapdevdb.lib.umd.edu:/tmp
```

7) Log in to the RedCap database server.

8) On the RedCap database server, switch to the "db" service account.

9) As the "db" service account user, run the following commands:

**Note:** In the following the "cleanup.sql" script is optional, as it only
removes orphaned rows from tables. If you are feeling conservative, it is
okay not to run it. 

```
> mysql -u redcap -p redcap < /tmp/cleanup.sql
> mysql -u redcap -p redcap < /tmp/purge_queries_output.sql
```

You will be prompted for the password after each command.

10) If you want to clean up the files in the "/apps/redcap/edocs" on the
RedCap server, probably the easiest thing to do is to keep the
"file_list.txt" file from the "Creating Database for Transfer" scenario and
use it to delete all the files in the list from the "/apps/redcap/edocs", using
the following command (WARNING: this command has not been tested):

```
> xargs rm < file_list.txt
```

## License

See the [LICENSE](LICENSE.md) file for license rights and limitations (Apache 2.0).

----
[clone_redcap_db]: https://confluence.umd.edu/display/ULDW/Clone+REDCap+database

[]: https://stackoverflow.com/a/5142498