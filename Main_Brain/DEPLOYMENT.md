# Deployment Guide

## Database Migration
When deploying updates that change the database schema, you must run the migration script.

### Adding 'Category' to Dashboard Items
If you encounter the error:
`column "category" of relation "dashboard_items" does not exist`

Run the following command in the `Suzlon_Copilot_Main_Brain` directory on your server:

```bash
python migrate_db.py
```

Ensure your `.env` file is correctly configured with the production database credentials before running the script.

## Environment Variables
Ensure the following variables are set in your `.env`:
- `DB_HOST`: Database hostname
- `DB_PORT`: 5432
- `DB_NAME`: Suzlon_Backend
- `DB_USER`: suzlon_user
- `DB_PASSWORD`: suzlon_password
