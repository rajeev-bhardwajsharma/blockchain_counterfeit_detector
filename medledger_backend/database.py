# In database.py (Complete and Corrected Version)

import sqlite3
import time
import pickle

DATABASE_NAME = "blockchain.db"
DB_TIMEOUT = 10  # Wait for up to 10 seconds if the DB is locked

def init_db():
    """Initializes the database and creates BOTH required tables."""
    conn = sqlite3.connect(DATABASE_NAME, timeout=DB_TIMEOUT)
    cursor = conn.cursor()

    # Table 1: Stores the complete blockchain object
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blockchains (
            batch_id INTEGER PRIMARY KEY,
            blockchain_object BLOB NOT NULL
        )
    ''')
    
    # Table 2: Stores only the most recent state for fast queries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicine_state (
            batch_id INTEGER PRIMARY KEY,
            current_owner TEXT NOT NULL,
            status TEXT NOT NULL,
            location TEXT NOT NULL,
            last_updated REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def save_chain(batch_id, chain_object):
    """Serializes and saves the entire blockchain object."""
    conn = sqlite3.connect(DATABASE_NAME, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    serialized_object = pickle.dumps(chain_object)
    cursor.execute(
        "INSERT OR REPLACE INTO blockchains (batch_id, blockchain_object) VALUES (?, ?)",
        (batch_id, serialized_object)
    )
    conn.commit()
    conn.close()

def load_chain(batch_id):
    """Loads and deserializes the entire blockchain object."""
    conn = sqlite3.connect(DATABASE_NAME, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    cursor.execute("SELECT blockchain_object FROM blockchains WHERE batch_id = ?", (batch_id,))
    result = cursor.fetchone()
    conn.close()
    return pickle.loads(result[0]) if result else None

def log_creation(batch_id, owner, location):
    """Logs the initial state of a newly created medicine batch."""
    conn = sqlite3.connect(DATABASE_NAME, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO medicine_state (batch_id, current_owner, status, location, last_updated)
        VALUES (?, ?, ?, ?, ?)
        """,
        (batch_id, owner, "AVAILABLE", location, time.time())
    )
    conn.commit()
    conn.close()

def get_current_state(batch_id):
    """Quickly retrieves the current state of a medicine."""
    conn = sqlite3.connect(DATABASE_NAME, timeout=DB_TIMEOUT)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicine_state WHERE batch_id = ?", (batch_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_owner(batch_id, new_owner, new_location):
    """Updates the owner and location of a medicine batch after a transfer."""
    conn = sqlite3.connect(DATABASE_NAME, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE medicine_state
        SET current_owner = ?, location = ?, last_updated = ?
        WHERE batch_id = ?
        """,
        (new_owner, new_location, time.time(), batch_id)
    )
    conn.commit()
    conn.close()



def update_status(batch_id, new_status):
    """Updates the status of a medicine batch."""
    conn = sqlite3.connect(DATABASE_NAME, timeout=10)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE medicine_state
        SET status = ?, last_updated = ?
        WHERE batch_id = ?
        """,
        (new_status, time.time(), batch_id)
    )
    conn.commit()
    conn.close()