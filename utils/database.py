import sqlite3

DB_NAME = "database/results.db"  # Update path to match your structure

# === Initialize database ===
def init_db():
    """
    Initializes the database by creating the 'results' table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS results (
            name TEXT,
            email TEXT,
            score REAL,
            skills TEXT,
            filename TEXT PRIMARY KEY,
            notes TEXT DEFAULT '',
            rating INTEGER DEFAULT 0,
            starred INTEGER DEFAULT 0,
            gpt_title TEXT DEFAULT '',
            ml_title TEXT DEFAULT '',
            resume_title TEXT DEFAULT '',
            ml_title_top3 TEXT DEFAULT '',
            gpt_confidence REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()


# === Insert or update result ===
def insert_result(name, email, score, skills, filename,
                  gpt_title='', ml_title='', resume_title='',
                  ml_title_top3='', gpt_confidence=0.0, starred=0):
    """
    Inserts or replaces a resume result into the database.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO results 
        (name, email, score, skills, filename, gpt_title, ml_title, resume_title, ml_title_top3, gpt_confidence, starred)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, email, score, skills, filename,
          gpt_title, ml_title, resume_title,
          ml_title_top3, gpt_confidence, starred))
    conn.commit()
    conn.close()


# === Toggle starred status ===
def toggle_star(filename):
    """
    Toggles the 'starred' status for a specific candidate.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE results SET starred = 1 - starred WHERE filename = ?', (filename,))
    conn.commit()
    conn.close()


# === Get all results ===
def get_all_results():
    """
    Retrieves all resume results from the database.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT name, email, score, skills, filename, notes, rating, starred,
               gpt_title, ml_title, resume_title, ml_title_top3, gpt_confidence
        FROM results
    ''')
    rows = c.fetchall()
    conn.close()
    return rows


# === Update notes and rating ===
def update_notes_and_rating(filename, notes, rating):
    """
    Updates notes and rating for a specific candidate.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        UPDATE results SET notes = ?, rating = ? WHERE filename = ?
    ''', (notes, rating, filename))
    conn.commit()
    conn.close()
