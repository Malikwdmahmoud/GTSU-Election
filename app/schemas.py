from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class FileOut(BaseModel):
    id: int
    original_name: str
    stored_name: str
    content_type: str
    size: int
    created_at: datetime

    class Config:
        orm_mode = True


class IndividualCreate(BaseModel):
    full_name: str
    phone: str
    batch: str
    school: str
    notes: Optional[str] = None


class ListMemberIn(BaseModel):
    full_name: str
    phone: str
    batch: str
    school: str


class ListCreate(BaseModel):
    list_name: str
    contact_phone: str
    notes: Optional[str] = None
    members: List[ListMemberIn]
