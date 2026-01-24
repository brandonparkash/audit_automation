from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import database as db
import apps.uploader_logic as uploader
import os

# Initialize DB
db.db_connect()

# Ensure uploads directory exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# --- TRACKER ROUTES ---
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("tracker/dashboard.html", {"request": request, "info": db.get_all_audits()})

@app.post("/add")
async def handle_add(dept: str = Form(...), doc: str = Form(...), name: str = Form(...), email: str = Form(...), deadline: str = Form(...)):
    db.add_audit_request(dept, doc, name, email, deadline)
    return RedirectResponse(url="/", status_code=303)

# --- SECURE UPLOAD ROUTES ---
@app.get("/upload/{sec_key}", response_class=HTMLResponse)
async def upload_page(request: Request, sec_key: str):
    # Verify key exists
    audit = db.get_audit_by_key(sec_key)
    if not audit:
        return HTMLResponse("<h1>Invalid or Expired Security Key</h1>", status_code=404)
        
    return templates.TemplateResponse("uploader/public_upload.html", {"request": request, "audit": audit})

@app.post("/upload/{sec_key}")
async def handle_upload(sec_key: str, file: UploadFile = File(...)):
    # 1. Get Audit Info
    audit = db.get_audit_by_key(sec_key)
    if not audit:
        return HTMLResponse("<h1>Error: Audit request not found.</h1>", status_code=404)

    # 2. Use Logic Module to Save File
    saved_path = uploader.save_evidence_file(file, audit['document_type'], audit['department'])

    # 3. Update DB
    db.update_evidence(sec_key, saved_path)
    
    return HTMLResponse("""
        <div style="font-family:sans-serif; text-align:center; padding:50px;">
            <h1 style="color:#27ae60;">✓ Upload Successful</h1>
            <p>Your evidence has been securely filed in the Audit Vault.</p>
        </div>
    """)

# --- ARCHIVE ROUTE ---
@app.get("/archive", response_class=HTMLResponse)
async def archive_gallery(request: Request):
    evidence_list = []
    
    # Check if uploads folder exists to avoid errors
    if os.path.exists("uploads"):
        # Walk through the directory tree
        for root, dirs, files in os.walk("uploads"):
            for file in files:
                # Create the web-accessible path
                # We perform string manipulation to handle Windows/Mac path differences
                relative_path = os.path.join(root, file)
                web_path = relative_path.replace("\\", "/") 
                
                # Create a pretty "Category" name (e.g. FED_Inspection > Housing)
                category = root.replace("uploads", "").replace("\\", " > ").replace("/", " > ").strip(" >_")
                
                evidence_list.append({
                    "filename": file,
                    "path": web_path,
                    "category": category
                })
    
    return templates.TemplateResponse("tracker/archive.html", {
        "request": request, 
        "evidence": evidence_list
    })

@app.post("/delete/{audit_id}")
async def delete_item(audit_id: int):
    db.delete_single_audit(audit_id)
    return RedirectResponse(url="/", status_code=303)

@app.post("/nuclear_clear")
async def clear_everything():
    db.nuclear_wipe()
    return RedirectResponse(url="/", status_code=303)