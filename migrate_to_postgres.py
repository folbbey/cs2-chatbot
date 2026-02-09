"""
Migration script to convert SQLite databases to PostgreSQL.
Run this on your local machine to migrate existing data.
"""
import sqlite3
import psycopg2
import os
import sys

# PostgreSQL connection details
PG_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', '5432')),
    'database': os.getenv('POSTGRES_DB', 'fishing_bot'),
    'user': os.getenv('POSTGRES_USER', 'bot_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'bot_password')
}

# SQLite database paths
SQLITE_DBS = {
    'economy': 'db/economy.db',
    'fish': 'db/fish.db',
    'inventory': 'db/inventory.db',
    'status_effects': 'db/status_effects.db'
}


def migrate_economy(sqlite_conn, pg_conn):
    """Migrate economy.db to PostgreSQL."""
    print("Migrating economy data...")
    
    sqlite_cursor = sqlite_conn.cursor()
    
    sqlite_cursor.execute("SELECT user_id, balance FROM user_balances")
    rows = sqlite_cursor.fetchall()
    
    migrated = 0
    skipped = 0
    for row in rows:
        try:
            pg_cursor = pg_conn.cursor()
            pg_cursor.execute(
                "INSERT INTO user_balances (user_id, balance) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET balance = EXCLUDED.balance",
                row
            )
            pg_conn.commit()
            migrated += 1
        except Exception as e:
            pg_conn.rollback()
            print(f"  Skipping {row[0]} (balance: {row[1]}): {str(e).split('DETAIL')[0].strip()}")
            skipped += 1
    
    print(f"Migrated {migrated} user balances (skipped {skipped})")


def migrate_fish(sqlite_conn, pg_conn):
    """Migrate fish.db to PostgreSQL."""
    print("Migrating fish data...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute("SELECT user_id, name, weight, price, bait FROM caught_fish")
    rows = sqlite_cursor.fetchall()
    
    for row in rows:
        pg_cursor.execute(
            "INSERT INTO caught_fish (user_id, name, weight, price, bait) VALUES (%s, %s, %s, %s, %s)",
            row
        )
    
    pg_conn.commit()
    print(f"Migrated {len(rows)} caught fish records")


def migrate_inventory(sqlite_conn, pg_conn):
    """Migrate inventory.db to PostgreSQL."""
    print("Migrating inventory data...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Check if item_data column exists
    sqlite_cursor.execute("PRAGMA table_info(user_inventory)")
    columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    if 'item_data' in columns:
        sqlite_cursor.execute("SELECT user_id, item_name, quantity FROM user_inventory")
    else:
        sqlite_cursor.execute("SELECT user_id, item_name, quantity FROM user_inventory")
    
    rows = sqlite_cursor.fetchall()
    
    for row in rows:
        pg_cursor.execute(
            "INSERT INTO user_inventory (user_id, item_name, quantity) VALUES (%s, %s, %s) ON CONFLICT (user_id, item_name) DO UPDATE SET quantity = EXCLUDED.quantity",
            row
        )
    
    pg_conn.commit()
    print(f"Migrated {len(rows)} inventory records")


def migrate_status_effects(sqlite_conn, pg_conn):
    """Migrate status_effects.db to PostgreSQL."""
    print("Migrating status effects data...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute("SELECT user_id, effect_id, expires_at FROM user_status_effects")
    rows = sqlite_cursor.fetchall()
    
    for row in rows:
        pg_cursor.execute(
            "INSERT INTO status_effects (user_id, effect_name, expiration_time) VALUES (%s, %s, %s) ON CONFLICT (user_id, effect_name) DO UPDATE SET expiration_time = EXCLUDED.expiration_time",
            row
        )
    
    pg_conn.commit()
    print(f"Migrated {len(rows)} status effects")


def main():
    """Main migration function."""
    print("Starting database migration from SQLite to PostgreSQL...")
    print(f"Target: {PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['database']}")
    
    # Connect to PostgreSQL
    try:
        pg_conn = psycopg2.connect(**PG_CONFIG)
        print("Connected to PostgreSQL")
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        sys.exit(1)
    
    # Migrate each database
    migrations = {
        'economy': migrate_economy,
        'fish': migrate_fish,
        'inventory': migrate_inventory,
        'status_effects': migrate_status_effects
    }
    
    for db_name, migrate_func in migrations.items():
        db_path = SQLITE_DBS[db_name]
        if not os.path.exists(db_path):
            print(f"Skipping {db_name} - database file not found: {db_path}")
            continue
        
        try:
            sqlite_conn = sqlite3.connect(db_path)
            migrate_func(sqlite_conn, pg_conn)
            sqlite_conn.close()
        except Exception as e:
            print(f"Error migrating {db_name}: {e}")
            pg_conn.rollback()
    
    pg_conn.close()
    print("\nMigration complete!")


if __name__ == "__main__":
    main()
