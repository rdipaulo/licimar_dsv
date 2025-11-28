import sqlite3
import os

db_path = os.path.join('instance', 'licimar_dev.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column exists
    cursor.execute("PRAGMA table_info(ambulantes)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'divida_acumulada' not in columns:
        print("Adding divida_acumulada column to ambulantes...")
        cursor.execute("""
            ALTER TABLE ambulantes 
            ADD COLUMN divida_acumulada NUMERIC(10, 2) DEFAULT 0
        """)
        conn.commit()
        print("✓ Column added successfully")
    else:
        print("✓ Column already exists")
        
    # Verify
    cursor.execute("PRAGMA table_info(ambulantes)")
    columns = cursor.fetchall()
    print("\nAmbulantes table columns:")
    for col in columns:
        print(f"  - {col[1]}: {col[2]}")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
