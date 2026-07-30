"""Placeholder database connection strings for parser unit tests."""

SQLITE_FILE_URL = 'sqlite:////tmp/forge-crm/crm_db'
SQLITE_MEMORY_URL = 'sqlite:///:memory:'
POSTGRES_URL = 'postgresql://crm_user:placeholder@127.0.0.1:5432/crm_db'
MYSQL_URL = 'mysql://crm_user:placeholder@127.0.0.1:3306/crm_db'
MYSQL_EMPTY_PASSWORD_URL = 'mysql://root:@127.0.0.1:3306/crm_db'
POSTGRES_ENCODED_PASSWORD_URL = 'postgresql://crm_user:p%40ss%2Fword@127.0.0.1/crm_db'
