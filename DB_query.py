import sqlite3

conn = sqlite3.connect('D:/Preditictive Agent/logs.db') # Use your exact absolute path!
cursor = conn.cursor()

# Create the maintenance table
cursor.execute('''
CREATE TABLE IF NOT EXISTS maintenance_windows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    reason TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()
conn.close()
print("✅ Maintenance table created successfully.")