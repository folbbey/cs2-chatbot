"""Script to help convert fishing.py to PostgreSQL"""
import re

# Read the file
with open("modules/fishing.py", "r", encoding="utf-8") as f:
    content = f.content()

# 1. Replace imports
content = content.replace("import sqlite3", "")
if "from util.database import DatabaseConnection" not in content:
    content = content.replace("import sys", "import sys\nfrom util.database import DatabaseConnection")

# 2. Remove database initialization
# Remove self.db_path assignment
content = re.sub(r'\s+self\.db_path = os\.path\.join\([^)]+\)\s*', '\n', content)
# Remove initialize_database() call
content = content.replace("self.initialize_database()", "")

# 3. Remove initialize_database method
content = re.sub(r'def initialize_database\(self\):.*?conn\.close\(\)\s*', '', content, flags=re.DOTALL)

# 4. Replace connection patterns
# Pattern: conn = sqlite3.connect(self.db_path)\n        cursor = conn.cursor()
old_pattern = r'(\s+)conn = sqlite3\.connect\(self\.db_path\)\s+cursor = conn\.cursor\(\)'
new_pattern = r'\1with DatabaseConnection() as cursor:'

content = re.sub(old_pattern, new_pattern, content)

# 5. Remove conn.commit() and conn.close()
content = re.sub(r'\s+conn\.commit\(\)\s*', '\n', content)
content = re.sub(r'\s+conn\.close\(\)\s*', '\n', content)

# 6. Replace ? with %s
content = content.replace("?", "%s")

# 7. Fix PRAGMA and ALTER TABLE (remove these - schema managed by init.sql)
content = re.sub(r'\s+# Create bait column if it doesn.*?conn\.close\(\)\s*', '', content, flags=re.DOTALL)
content = re.sub(r'\s+cursor\.execute\(\s*""".*?PRAGMA.*?""".*?\)\s*', '', content, flags=re.DOTALL)
content = re.sub(r'\s+cursor\.execute\(\s*""".*?ALTER TABLE.*?""".*?\)\s*', '', content, flags=re.DOTALL)
content = re.sub(r'\s+columns = \[column\[1\] for column in cursor\.fetchall\(\)\]\s*', '', content)
content = re.sub(r'\s+if "bait" not in columns:.*?""".*?\)\s*', '', content, flags=re.DOTALL)

# 8. Fix COLLATE NOCASE - replace with ILIKE
content = content.replace("COLLATE NOCASE", "")

# 9. Fix ON CONFLICT
content = content.replace("ON CONFLICT", "ON CONFLICT")
content = content.replace("excluded.", "EXCLUDED.")

# Write back
with open("modules/fishing_postgres.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Done! Check fishing_postgres.py")
