# 🛠️ Fix: Alembic Migration Conflict on Server

If you see the error `KeyError: '020_add_orderline_spec'`, follow these steps to synchronize the migration state.

## Step 1: Update the Code on Server

Connect to your server via SSH and pull the latest changes that I've just pushed to GitHub.

```bash
cd /var/www/R1
git pull origin main
```

## Step 2: Fix the Database State

Since the migration IDs were inconsistent, we need to tell the database that it should be at the "correct" head.

Run this command inside your Docker environment:

```bash
docker-compose exec backend alembic stamp head
```

> [!IMPORTANT]
> This command marks the database as being at the latest version. Use this if your database structure already contains the changes from the migrations but the version tracking is stuck.

## Step 3: Verify the Fix

Try to create the "Dimensions" attribute again in the UI. It should work now as the `DIMENSIONS` type will be available in the database.

If it still fails, run the migrations normally:

```bash
docker-compose exec backend alembic upgrade head
```
