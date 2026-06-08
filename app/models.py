from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class FileUpload(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    original_name = Column(String, nullable=False)
    stored_name = Column(String, nullable=False, unique=True)
    content_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class IndividualCandidate(Base):
    __tablename__ = "individuals"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    batch = Column(String(100), nullable=False)
    school = Column(String(100), nullable=False)
    notes = Column(Text)
    id_file_id = Column(Integer, ForeignKey("files.id"))
    photo_file_id = Column(Integer, ForeignKey("files.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    id_file = relationship("FileUpload", foreign_keys=[id_file_id])
    photo_file = relationship("FileUpload", foreign_keys=[photo_file_id])


class ListEntity(Base):
    __tablename__ = "lists"
    id = Column(Integer, primary_key=True, index=True)
    list_name = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    members = relationship("ListMember", back_populates="parent", cascade="all,delete")


class ListMember(Base):
    __tablename__ = "list_members"
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("lists.id"))
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    batch = Column(String(100), nullable=False)
    school = Column(String(100), nullable=False)
    id_file_id = Column(Integer, ForeignKey("files.id"))
    photo_file_id = Column(Integer, ForeignKey("files.id"))

    parent = relationship("ListEntity", back_populates="members")
    id_file = relationship("FileUpload", foreign_keys=[id_file_id])
    photo_file = relationship("FileUpload", foreign_keys=[photo_file_id])


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(255), nullable=False)
    detail = Column(Text)
    created_by = Column(String(255), default="system")
    created_at = Column(DateTime, default=datetime.utcnow)
