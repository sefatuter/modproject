import sqlite3

DATABASE = 'modsec_rules.db'

def get_db_connection():
    """
    Create a connection to the SQLite database.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """
    Initialize the database with the required tables.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_rule(rule):
    """
    Add a new rule to the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO rules (rule) VALUES (?)', (rule,))
    conn.commit()
    new_rule_id = cursor.lastrowid # 
    conn.close()
    return new_rule_id

def get_all_rules():
    """
    Retrieve all rules from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, rule FROM rules')
    rules = cursor.fetchall()
    conn.close()
    return rules

def delete_rule(rule_id):
    """
    Delete a rule from the database by its ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM rules WHERE id = ?', (rule_id,))
    conn.commit()
    conn.close()

def update_rule(rule_id, updated_rule):
    """
    Update a rule in the database by its ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE rules SET rule = ? WHERE id = ?', (updated_rule, rule_id))
    conn.commit()
    conn.close()
