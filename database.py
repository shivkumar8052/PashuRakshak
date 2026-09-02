import sqlite3

DATABASE = "animal_health.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            village TEXT NOT NULL,
            block TEXT,
            district TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS animals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id TEXT UNIQUE NOT NULL,
            farmer_id INTEGER NOT NULL,
            animal_type TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            FOREIGN KEY (farmer_id) REFERENCES farmers(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id TEXT NOT NULL,
            symptoms TEXT NOT NULL,
            symptom_count INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            village TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()