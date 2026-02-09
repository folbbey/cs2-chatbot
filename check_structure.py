import sqlite3

# Check status effects structure
conn = sqlite3.connect('db/status_effects.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(user_status_effects)")
cols = cursor.fetchall()
print("Status effects columns:", [col[1] for col in cols])
cursor.execute("SELECT * FROM user_status_effects LIMIT 2")
print("Sample rows:", cursor.fetchall())
conn.close()

# Check economy for large values
conn = sqlite3.connect('db/economy.db')
cursor = conn.cursor()
cursor.execute("SELECT user_id, balance FROM user_balances ORDER BY balance DESC LIMIT 1")
max_val = cursor.fetchone()
print(f"\nMax balance: {max_val}")
conn.close()
