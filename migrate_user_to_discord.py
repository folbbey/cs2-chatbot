"""
Script to manually migrate a user's fishing data from CS2 to Discord.
Usage: python migrate_user_to_discord.py <cs2_username> <discord_username>
"""
import sys
import psycopg2
from psycopg2 import sql


def migrate_user(cs2_user: str, discord_user: str):
    """Migrate all fishing data from CS2 user to Discord user."""
    
    # Database connection parameters
    conn_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'fishing_bot',
        'user': 'bot_user',
        'password': 'bot_password'
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        print(f"Migrating data from CS2 user '{cs2_user}' to Discord user '{discord_user}'...")
        
        # Check if CS2 user has any data
        cursor.execute("SELECT COUNT(*) FROM caught_fish WHERE user_id = %s", (cs2_user,))
        fish_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_inventory WHERE user_id = %s", (cs2_user,))
        inventory_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT balance FROM user_balances WHERE user_id = %s", (cs2_user,))
        balance_result = cursor.fetchone()
        balance = balance_result[0] if balance_result else 0
        
        cursor.execute("SELECT COUNT(*) FROM status_effects WHERE user_id = %s", (cs2_user,))
        effects_count = cursor.fetchone()[0]
        
        print(f"\nCS2 user '{cs2_user}' has:")
        print(f"  - {fish_count} caught fish")
        print(f"  - {inventory_count} inventory items")
        print(f"  - ${balance} balance")
        print(f"  - {effects_count} status effects")
        
        if fish_count == 0 and inventory_count == 0 and balance == 0 and effects_count == 0:
            print(f"\nNo data to migrate for CS2 user '{cs2_user}'")
            return
        
        # Check if Discord user already has data
        cursor.execute("SELECT COUNT(*) FROM caught_fish WHERE user_id = %s", (discord_user,))
        discord_fish = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_inventory WHERE user_id = %s", (discord_user,))
        discord_inventory = cursor.fetchone()[0]
        
        if discord_fish > 0 or discord_inventory > 0:
            print(f"\nWARNING: Discord user '{discord_user}' already has data!")
            print(f"  - {discord_fish} caught fish")
            print(f"  - {discord_inventory} inventory items")
            response = input("Continue with migration? This will overwrite existing data (yes/no): ")
            if response.lower() != 'yes':
                print("Migration cancelled.")
                return
        
        # Perform migration
        print(f"\nMigrating data...")
        
        # Migrate caught fish
        cursor.execute("""
            UPDATE caught_fish
            SET user_id = %s
            WHERE user_id = %s
        """, (discord_user, cs2_user))
        print(f"  ✓ Migrated {cursor.rowcount} caught fish")
        
        # Migrate inventory (handle conflicts by summing quantities)
        cursor.execute("""
            INSERT INTO user_inventory (user_id, item_name, item_data, quantity)
            SELECT %s, item_name, item_data, quantity
            FROM user_inventory
            WHERE user_id = %s
            ON CONFLICT (user_id, item_name) DO UPDATE
            SET quantity = user_inventory.quantity + EXCLUDED.quantity
        """, (discord_user, cs2_user))
        print(f"  ✓ Migrated inventory items")
        
        # Delete old CS2 inventory records
        cursor.execute("DELETE FROM user_inventory WHERE user_id = %s", (cs2_user,))
        
        # Migrate balance (add to existing if any)
        if balance > 0:
            cursor.execute("""
                INSERT INTO user_balances (user_id, balance)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET balance = user_balances.balance + EXCLUDED.balance
            """, (discord_user, balance))
            print(f"  ✓ Migrated balance: ${balance}")
            
            # Delete old CS2 balance
            cursor.execute("DELETE FROM user_balances WHERE user_id = %s", (cs2_user,))
        
        # Migrate status effects
        cursor.execute("""
            UPDATE status_effects
            SET user_id = %s
            WHERE user_id = %s
        """, (discord_user, cs2_user))
        print(f"  ✓ Migrated {cursor.rowcount} status effects")
        
        # Commit changes
        conn.commit()
        print(f"\n✓ Migration completed successfully!")
        print(f"All data from '{cs2_user}' has been moved to '{discord_user}'")
        
    except psycopg2.Error as e:
        print(f"\n✗ Database error: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python migrate_user_to_discord.py <cs2_username> <discord_username>")
        print("\nExample:")
        print("  python migrate_user_to_discord.py WolfGangDealers 'Black-Squad WolfGang'")
        sys.exit(1)
    
    cs2_username = sys.argv[1]
    discord_username = sys.argv[2]
    
    migrate_user(cs2_username, discord_username)
