# Database Service

This directory contains the PostgreSQL database configuration and initialization scripts for the Deals Agent application.

## Components

- `Dockerfile`: PostgreSQL container configuration
- `init/`: Database initialization scripts
  - `01_create_tables.sql`: Creates database schema and tables
  - `02_insert_sample_data.sql`: Inserts initial sample data
  - `sample_data.json`: JSON data used for sample data insertion

## Database Configuration

The database is configured with the following default settings:
- Database Name: `deals_db`
- User: `deals_user`
- Password: `deals_password`
- Port: `5432`

## Initialization Process

1. The database container is created using the PostgreSQL 15 image
2. Initialization scripts in the `init/` directory are executed in alphabetical order
3. Tables are created first, followed by sample data insertion

## Development

To modify the database schema:
1. Update the `01_create_tables.sql` file
2. If adding new sample data, update `sample_data.json` and `02_insert_sample_data.sql`
3. Rebuild the database container to apply changes

## Backup and Restore

Database backups are handled by the backup service in the `../backups` directory.
See the backup service README for more information about backup procedures. 