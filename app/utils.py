import os
import secrets
from pathlib import Path
from .config import settings
from starlette.datastructures import UploadFile
import shutil
import mimetypes
from passlib.context import CryptContext
import smtplib
from email.message import EmailMessage

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def ensure_upload_dir():
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def random_filename(original: str) -> str:
    ext = Path(original).suffix
    return secrets.token_hex(16) + ext


def validate_file(file: UploadFile, allowed_mimes: set, max_size: int):
    # Check content type
    if file.content_type not in allowed_mimes:
        return False, "نوع الملف غير مدعوم"
    # read small chunk to check size
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > max_size:
        return False, "حجم الملف أكبر من الحد المسموح"
    return True, size


def save_upload(file: UploadFile, allowed_mimes: set, max_size: int):
    ok, res = validate_file(file, allowed_mimes, max_size)
    if not ok:
        return None, res
    ensure_upload_dir()
    stored = random_filename(file.filename)
    path = Path(settings.UPLOAD_DIR) / stored
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"original_name": file.filename, "stored_name": stored, "content_type": file.content_type, "size": path.stat().st_size}, None


def send_email(subject: str, html_body: str, to_email: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER or f"no-reply@{settings.SMTP_HOST}"
    msg["To"] = to_email
    msg.set_content("هذا الإيميل يدعم HTML")
    msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            if settings.SMTP_USER and settings.SMTP_PASS:
                smtp.starttls()
                smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
            smtp.send_message(msg)
    except Exception as e:
        raise
