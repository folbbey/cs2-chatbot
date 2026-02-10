"""
Backfill item_data for inventory items that have empty data.
"""
import psycopg2
import json
import os

# PostgreSQL connection
PG_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', '5432')),
    'database': os.getenv('POSTGRES_DB', 'fishing_bot'),
    'user': os.getenv('POSTGRES_USER', 'bot_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'bot_password')
}

# Load shop data
with open('modules/data/shop.json', 'r') as f:
    shop_data = json.load(f)

# Build lookup dictionary by item name (case-insensitive)
item_lookup = {}
for category, items in shop_data.items():
    for item in items:
        item_lookup[item['name'].lower()] = item
        # Also add aliases
        for alias in item.get('aliases', []):
            item_lookup[alias.lower()] = item

def backfill_item_data():
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    # Get all items with empty item_data
    cursor.execute("""
        SELECT user_id, item_name, item_data
        FROM user_inventory
        WHERE item_data = '{}' OR item_data IS NULL OR item_data = ''
    """)
    
    items = cursor.fetchall()
    print(f"Found {len(items)} items with empty data")
    
    updated = 0
    not_found = 0
    
    for user_id, item_name, old_data in items:
        # Look up item in shop data
        item_info = item_lookup.get(item_name.lower())
        
        if item_info:
            # Update with full item data
            new_data = json.dumps(item_info)
            cursor.execute("""
                UPDATE user_inventory
                SET item_data = %s
                WHERE user_id = %s AND item_name = %s
            """, (new_data, user_id, item_name))
            print(f"  Updated {user_id}: {item_name}")
            updated += 1
        else:
            print(f"  NOT FOUND in shop: {item_name} (user: {user_id})")
            not_found += 1
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nBackfill complete:")
    print(f"  Updated: {updated}")
    print(f"  Not found: {not_found}")

if __name__ == "__main__":
    backfill_item_data()
