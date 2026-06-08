from . import models
from sqlalchemy.orm import Session
from .models import FileUpload, IndividualCandidate, ListEntity, ListMember, AuditLog
from datetime import datetime


def create_file_record(db: Session, file_meta: dict):
    f = FileUpload(
        original_name=file_meta["original_name"],
        stored_name=file_meta["stored_name"],
        content_type=file_meta["content_type"],
        size=file_meta["size"],
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def create_individual(db: Session, data: dict, id_file_meta: dict, photo_file_meta: dict):
    id_file = create_file_record(db, id_file_meta)
    photo_file = create_file_record(db, photo_file_meta)
    c = IndividualCandidate(
        full_name=data["full_name"],
        phone=data["phone"],
        batch=data["batch"],
        school=data["school"],
        notes=data.get("notes"),
        id_file_id=id_file.id,
        photo_file_id=photo_file.id,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def create_list_with_members(db: Session, list_data: dict, members: list, file_metas: dict):
    lst = ListEntity(list_name=list_data["list_name"], contact_phone=list_data["contact_phone"], notes=list_data.get("notes"))
    db.add(lst)
    db.commit()
    db.refresh(lst)

    for idx, m in enumerate(members):
        id_meta = file_metas.get(f"member_{idx}_id")
        photo_meta = file_metas.get(f"member_{idx}_photo")
        id_f = create_file_record(db, id_meta)
        photo_f = create_file_record(db, photo_meta)
        mm = ListMember(
            parent_id=lst.id,
            full_name=m["full_name"],
            phone=m["phone"],
            batch=m["batch"],
            school=m["school"],
            id_file_id=id_f.id,
            photo_file_id=photo_f.id,
        )
        db.add(mm)
    db.commit()
    db.refresh(lst)
    return lst


def log_action(db: Session, action: str, detail: str, created_by: str = "system"):
    a = AuditLog(action=action, detail=detail, created_by=created_by, created_at=datetime.utcnow())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a
