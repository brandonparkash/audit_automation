import os
import shutil
import sqlite3
import uuid
import stat

def db_connect():
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        security_key TEXT UNIQUE,
        department TEXT NOT NULL,
        document_type TEXT NOT NULL,
        contact_name TEXT NOT NULL,
        email TEXT NOT NULL,
        deadline DATE,
        status TEXT DEFAULT 'Pending',
        file_path TEXT)""")
    conn.commit()
    conn.close()

def get_all_audits():
    conn = sqlite3.connect("main.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audits")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_audit_request(dept, doc, name, email, deadline):
    # Generate a secure random key (UUID)
    sec_key = uuid.uuid4().hex
    
    conn = sqlite3.connect("main.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO audits (security_key, department, document_type, contact_name, email, deadline) VALUES (?,?,?,?,?,?)",
                   (sec_key, dept, doc, name, email, deadline))
    conn.commit()
    conn.close()

def get_audit_by_key(sec_key):
    conn = sqlite3.connect("main.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audits WHERE security_key = ?", (sec_key,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_evidence(sec_key, path):
    conn = sqlite3.connect("main.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE audits SET file_path = ?, status = 'Complete' WHERE security_key = ?", (path, sec_key))
    conn.commit()
    conn.close()

# This helper function handles read-only files that Windows sometimes creates
def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def delete_single_audit(audit_id):
    conn = sqlite3.connect("main.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT file_path FROM audits WHERE id = ?", (audit_id,))
    row = cursor.fetchone()
    
    if row and row['file_path']:
        file_path = row['file_path']
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                # Cleanup empty folders
                parent_dir = os.path.dirname(file_path)
                if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
                    # Check one level up (the doc_type folder)
                    grandparent_dir = os.path.dirname(parent_dir)
                    if grandparent_dir != "uploads" and os.path.exists(grandparent_dir) and not os.listdir(grandparent_dir):
                        os.rmdir(grandparent_dir)
            except PermissionError:
                print(f"File {file_path} is currently locked by another process.")

    cursor.execute("DELETE FROM audits WHERE id = ?", (audit_id,))
    conn.commit()
    conn.close()

def nuclear_wipe():
    conn = sqlite3.connect("main.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM audits")
    conn.commit()
    conn.close()
    
    # Wipe Physical Files
    if os.path.exists("uploads"):
        try:
            shutil.rmtree("uploads", onerror=remove_readonly)
        except Exception as e:
            print(f"Minor cleanup error: {e}. Some files may be in use.")
        
    # Ensure the base folder exists for next time
    if not os.path.exists("uploads"):
        os.makedirs("uploads")