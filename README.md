# Redcap Data Purge

## Introduction

Tool to purge Redcap database and files directory to just keep data from
specified projects.

**NOTE**: This is a work in progress and need code cleanup and reorganization.

## Getting Started

### Prerequisites

The following prerequisires are required for this application:

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

## License

See the [LICENSE](LICENSE.md) file for license rights and limitations (Apache 2.0).

----
[clone_redcap_db]: https://confluence.umd.edu/display/ULDW/Clone+REDCap+database