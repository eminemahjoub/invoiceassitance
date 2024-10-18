import sqlite3

def create_database():
    conn = sqlite3.connect('invoices.db')  # Create database or connect to it
    cursor = conn.cursor()
    
    # Create a table for invoices
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY,
            client_name TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            items TEXT NOT NULL,
            pdf_filename TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
