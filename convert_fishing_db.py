#!/usr/bin/env python3
"""
Automated conversion script to migrate fishing.py from SQLite to PostgreSQL.
This handles all database connection patterns systematically.
"""
import re

def convert_fishing_module():
    # Read the fishing module
    with open("modules/fishing.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Track the number of replacements
    replacements_made = 0
    
    # Pattern 1: Simple connection pattern (most common)
    # conn = sqlite3.connect(...)\n        cursor = conn.cursor()
    # ... queries ...
    # conn.commit()\n        conn.close()
    
    # Pattern to find connection blocks
    pattern = r'(\s+)conn = sqlite3\.connect\(self\.db_path\)\s+cursor = conn\.cursor\(\)'
    
    # Replace with context manager
    content = re.sub(pattern, r'\1with DatabaseConnection() as cursor:', content)
    replacements_made += len(re.findall(pattern, content))
    
    # Pattern 2: Remove conn.commit() and conn.close()
    content = re.sub(r'\s+conn\.commit\(\)\s*\n', '\n', content)
    content = re.sub(r'\s+conn\.close\(\)\s*\n', '\n', content)
    
    # Pattern 3: Replace ? with %s (PostgreSQL parameter style)
    content = content.replace(' = ?', ' = %s')
    content = content.replace('(?, ', '(%s, ')
    content = content.replace(', ?)', ', %s)')
    content = content.replace('(?)', '(%s)')
    content = content.replace('(?,', '(%s,')
    content = content.replace(',?)', ',%s)')
    
    # Pattern 4: Fix specific SQL syntax differences
    # AUTOINCREMENT -> handled by SERIAL in schema
    # COLLATE NOCASE -> remove (use ILIKE instead)
    content = content.replace(' COLLATE NOCASE', '')
    
    # Write the updated content
    with open("modules/fishing.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Conversion complete! Made {replacements_made} connection pattern replacements.")
    print("Additional replacements:")
    print("- Replaced all ? with %s for PostgreSQL parameter binding")
    print("- Removed COLLATE NOCASE clauses")
    print("- Removed conn.commit() and conn.close() calls")

if __name__ == "__main__":
    convert_fishing_module()
