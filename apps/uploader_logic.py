import os
import shutil

def save_evidence_file(file, doc_type, department):
    # 1. Sanitize names for folders (replace spaces with underscores)
    clean_doc = doc_type.replace(" ", "_")
    clean_dept = department.replace(" ", "_")
    
    # 2. Build Path: uploads/Document_Type/Department/
    folder_path = os.path.join("uploads", clean_doc, clean_dept)
    os.makedirs(folder_path, exist_ok=True)
    
    # 3. Save File
    file_location = os.path.join(folder_path, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return file_location