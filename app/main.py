from pydantic import BaseSettings, EmailStr
from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .config import settings
from .database import engine, Base, get_db
from . import models, crud, utils
from sqlalchemy.orm import Session
import os
import uuid
from pathlib import Path
from pydantic import EmailStr
from pydantic_settings import BaseSettings

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def gen_ref(prefix: str = "IND"):
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "project": settings.PROJECT_NAME})


@app.get("/apply/individual", response_class=HTMLResponse)
def individual_form(request: Request):
    schools = ["بحري", "أم درمان", "الخرطوم"]
    return templates.TemplateResponse("individual.html", {"request": request, "schools": schools})


@app.post("/submit/individual", response_class=HTMLResponse)
async def submit_individual(request: Request, full_name: str = Form(...), phone: str = Form(...), batch: str = Form(...), school: str = Form(...), notes: str = Form(None), id_file: UploadFile = File(...), photo_file: UploadFile = File(...), db: Session = Depends(get_db)):
    # server-side validation
    if not full_name or not phone or not batch or not school:
        raise HTTPException(status_code=400, detail="بيانات مطلوبة مفقودة")

    ok_id, res = utils.validate_file(id_file, settings.ALLOWED_ID_MIMES, settings.MAX_FILE_SIZE)
    if not ok_id:
        return templates.TemplateResponse("individual.html", {"request": request, "error": res, "schools": ["بحري","أم درمان","الخرطوم"]})
    ok_photo, res2 = utils.validate_file(photo_file, settings.ALLOWED_PHOTO_MIMES, settings.MAX_FILE_SIZE)
    if not ok_photo:
        return templates.TemplateResponse("individual.html", {"request": request, "error": res2, "schools": ["بحري","أم درمان","الخرطوم"]})

    meta_id, _ = utils.save_upload(id_file, settings.ALLOWED_ID_MIMES, settings.MAX_FILE_SIZE)
    meta_photo, _ = utils.save_upload(photo_file, settings.ALLOWED_PHOTO_MIMES, settings.MAX_FILE_SIZE)

    candidate = crud.create_individual(db, {"full_name": full_name, "phone": phone, "batch": batch, "school": school, "notes": notes}, meta_id, meta_photo)
    ref = gen_ref("IND")
    crud.log_action(db, "submit_individual", f"ref={ref}, id={candidate.id}")

    # send email (best effort)
    try:
        html = f"<h2>طلب ترشح فردي - {ref}</h2><p>الاسم: {full_name}</p><p>الهاتف: {phone}</p><p>الدفعة: {batch}</p><p>المدرسة: {school}</p>"
        utils.send_email(f"طلب ترشح فردي - {ref}", html, settings.ADMIN_EMAIL)
    except Exception:
        pass

    return templates.TemplateResponse("success.html", {"request": request, "message": "تم إرسال طلبك بنجاح", "ref": ref})


@app.get("/apply/list", response_class=HTMLResponse)
def list_form(request: Request):
    schools = ["بحري", "أم درمان", "الخرطوم"]
    return templates.TemplateResponse("list.html", {"request": request, "schools": schools})


@app.post("/submit/list", response_class=HTMLResponse)
async def submit_list(request: Request, list_name: str = Form(...), contact_phone: str = Form(...), notes: str = Form(None), db: Session = Depends(get_db)):
    # Expect 25 members with fields member_i_* and files member_i_id, member_i_photo
    members = []
    file_metas = {}
    for i in range(25):
        prefix = f"member_{i}_"
        full = (await request.form()).get(prefix + "full_name")
        phone = (await request.form()).get(prefix + "phone")
        batch = (await request.form()).get(prefix + "batch")
        school = (await request.form()).get(prefix + "school")
        if not (full and phone and batch and school):
            return templates.TemplateResponse("list.html", {"request": request, "error": f"الرجاء إكمال بيانات العضو رقم {i+1}", "schools": ["بحري","أم درمان","الخرطوم"]})
        members.append({"full_name": full, "phone": phone, "batch": batch, "school": school})

    form = await request.form()
    # Save member files
    for i in range(25):
        id_key = f"member_{i}_id"
        photo_key = f"member_{i}_photo"
        if id_key not in form or photo_key not in form:
            return templates.TemplateResponse("list.html", {"request": request, "error": "ملفات الأعضاء مفقودة", "schools": ["بحري","أم درمان","الخرطوم"]})
        id_file = form[id_key]
        photo_file = form[photo_key]
        ok_id, res = utils.validate_file(id_file, settings.ALLOWED_ID_MIMES, settings.MAX_FILE_SIZE)
        if not ok_id:
            return templates.TemplateResponse("list.html", {"request": request, "error": f"ملف إثبات العضو {i+1}: {res}", "schools": ["بحري","أم درمان","الخرطوم"]})
        ok_photo, res2 = utils.validate_file(photo_file, settings.ALLOWED_PHOTO_MIMES, settings.MAX_FILE_SIZE)
        if not ok_photo:
            return templates.TemplateResponse("list.html", {"request": request, "error": f"الصورة الشخصية للعضو {i+1}: {res2}", "schools": ["بحري","أم درمان","الخرطوم"]})
        meta_id, _ = utils.save_upload(id_file, settings.ALLOWED_ID_MIMES, settings.MAX_FILE_SIZE)
        meta_photo, _ = utils.save_upload(photo_file, settings.ALLOWED_PHOTO_MIMES, settings.MAX_FILE_SIZE)
        file_metas[f"member_{i}_id"] = meta_id
        file_metas[f"member_{i}_photo"] = meta_photo

    lst = crud.create_list_with_members(db, {"list_name": list_name, "contact_phone": contact_phone, "notes": notes}, members, file_metas)
    ref = gen_ref("LST")
    crud.log_action(db, "submit_list", f"ref={ref}, id={lst.id}")

    try:
        html = f"<h2>طلب ترشيح قائمة - {ref}</h2><p>اسم القائمة: {list_name}</p><p>هاتف المسؤول: {contact_phone}</p><p>عدد الأعضاء: {len(members)}</p>"
        utils.send_email(f"طلب ترشيح قائمة - {ref}", html, settings.ADMIN_EMAIL)
    except Exception:
        pass

    return templates.TemplateResponse("success.html", {"request": request, "message": "تم إرسال القائمة بنجاح", "ref": ref})


@app.get('/admin', response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse('admin_login.html', {"request": request})


@app.post('/admin/login')
def admin_login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    # very simple auth - production should use session/cookie + hashed password
    if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
        response = RedirectResponse(url='/admin/dashboard', status_code=status.HTTP_302_FOUND)
        return response
    return templates.TemplateResponse('admin_login.html', {"request": request, "error": "بيانات الدخول خاطئة"})


@app.get('/admin/dashboard', response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    individuals = db.query(models.IndividualCandidate).order_by(models.IndividualCandidate.created_at.desc()).all()
    lists = db.query(models.ListEntity).order_by(models.ListEntity.created_at.desc()).all()
    stats = {
        "individuals": db.query(models.IndividualCandidate).count(),
        "lists": db.query(models.ListEntity).count(),
        "members": db.query(models.ListMember).count(),
    }
    return templates.TemplateResponse('admin_dashboard.html', {"request": request, "individuals": individuals, "lists": lists, "stats": stats})


@app.get('/uploads/{filename}')
def get_upload(filename: str):
    path = Path(settings.UPLOAD_DIR) / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path)
