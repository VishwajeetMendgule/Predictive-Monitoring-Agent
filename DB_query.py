import sqlite3

# Create tables if they don't exist
def initialize_db():
    conn = sqlite3.connect('D:/Preditictive Agent/logs.db')
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

    # Create the chat_history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,  -- 'user' or 'assistant'
        content TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

# Call initialize_db when module is imported
initialize_db()


def check_maintenance_mode(current_log_time, db_connection):
    """
    Queries the database to see if the current log time falls within an active maintenance window.
    Returns (True, reason) if in maintenance, (False, None) if not.
    """
    # Convert Pandas timestamp to standard SQLite string format: YYYY-MM-DD HH:MM:SS
    time_str = current_log_time.strftime("%Y-%m-%d %H:%M:%S")
    
    query = """
        SELECT reason FROM maintenance_windows 
        WHERE ? BETWEEN start_time AND end_time
        ORDER BY id DESC LIMIT 1
    """
    
    cursor = db_connection.cursor()
    cursor.execute(query, (time_str,))
    result = cursor.fetchone()
    
    if result:
        return True, result[0] # Return True and the reason
    return False, None

def add_maintenance_window(start_time, end_time, reason):
    """
    Inserts a new maintenance window into the database.
    
    Parameters:
    - start_time: String in format 'YYYY-MM-DD HH:MM:SS'
    - end_time: String in format 'YYYY-MM-DD HH:MM:SS'  
    - reason: String describing the maintenance reason
    """
    conn = sqlite3.connect('D:/Preditictive Agent/logs.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO maintenance_windows (start_time, end_time, reason)
        VALUES (?, ?, ?)
    ''', (start_time, end_time, reason))
    
    conn.commit()
    conn.close()

def save_chat_message(session_id, role, content):
    """
    Saves a chat message to the database.
    
    Parameters:
    - session_id: Unique identifier for the chat session
    - role: 'user' or 'assistant'
    - content: The message content
    """
    conn = sqlite3.connect('D:/Preditictive Agent/logs.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO chat_history (session_id, role, content)
        VALUES (?, ?, ?)
    ''', (session_id, role, content))
    
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    """
    Retrieves the chat history for a session.
    
    Parameters:
    - session_id: Unique identifier for the chat session
    
    Returns:
    - List of tuples: [(role, content), ...]
    """
    conn = sqlite3.connect('D:/Preditictive Agent/logs.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT role, content FROM chat_history
        WHERE session_id = ?
        ORDER BY timestamp ASC
    ''', (session_id,))
    
    history = cursor.fetchall()
    conn.close()
    return history




# conn = sqlite3.connect('D:/Preditictive Agent/logs.db') # Use your exact absolute path!
# cursor = conn.cursor()

# # Create the maintenance table
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS maintenance_windows (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     start_time TEXT NOT NULL,
#     end_time TEXT NOT NULL,
#     reason TEXT,
#     created_at TEXT DEFAULT CURRENT_TIMESTAMP
# )
# ''')
# conn.commit()
# conn.close()
# print("✅ Maintenance table created successfully.")