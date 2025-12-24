import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [t[0] for t in cursor.fetchall()]

shop_tables = [t for t in tables if t.startswith('shop_')]
system_tables = [t for t in tables if not t.startswith('shop_')]

print("\n" + "="*70)
print("DANH SACH CAC BANG DU LIEU")
print("="*70)

print("\n*** SHOP TABLES (Cua hang van phong pham) ***\n")
for i, table in enumerate(shop_tables, 1):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    print(f"{i}. {table.upper()} ({len(columns)} fields)")
    for col_id, col_name, col_type, notnull, default, pk in columns:
        print(f"   - {col_name:20} {col_type:15} {'NOT NULL' if notnull else ''}")

print("\n*** SYSTEM TABLES (Django) ***\n")
for i, table in enumerate(system_tables, 1):
    print(f"{i}. {table}")

print("\n" + "="*70)
print(f"Total: {len(shop_tables)} shop tables + {len(system_tables)} system tables = {len(tables)} tables")
print("="*70 + "\n")

conn.close()
