"""
SQLAlchemy ORM models for database tables
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class CSVDocument(Base):
    """Model for CSV documents uploaded by users"""
    __tablename__ = "csv_documents"
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    preview_data = Column(JSON, nullable=False)
    full_data = Column(JSON, nullable=False)
    is_described = Column(Boolean, default=False, nullable=False)
    row_count = Column(Integer, nullable=False)
    column_count = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document_metadata = relationship("DocumentMetadata", back_populates="document", cascade="all, delete-orphan")
    knowledge_base = relationship("KnowledgeBase", back_populates="document", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "preview": self.preview_data,
            "full_data": self.full_data,
            "is_described": bool(self.is_described),
            "row_count": self.row_count,
            "column_count": self.column_count,
            "upload_date": str(self.upload_date),
        }


class DocumentMetadata(Base):
    """Model for document column metadata"""
    __tablename__ = "document_metadata"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("csv_documents.id"), nullable=False, unique=True)
    filename = Column(String(255), nullable=False)
    column_metadata = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("CSVDocument", back_populates="document_metadata")
    
    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "filename": self.filename,
            "column_metadata": self.column_metadata,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }


class FileRegistry(Base):
    """Central registry tracking all uploaded files with their dynamic tables"""
    __tablename__ = "file_registry"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("csv_documents.id"), nullable=False, unique=True)
    filename = Column(String(255), nullable=False, index=True)
    file_type = Column(String(50), default="csv", nullable=False)  # csv, excel, json, etc.
    dynamic_table_name = Column(String(255), nullable=True)  # Name of the dynamically created table
    data_category = Column(String(255), nullable=True)  # Category from LLM analysis
    row_count = Column(Integer, nullable=False)  # Number of data rows
    column_count = Column(Integer, nullable=False)  # Number of columns
    is_described = Column(Boolean, default=False, nullable=False, index=True)  # User verified?
    verified_at = Column(DateTime, nullable=True)  # When user verified the data
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    table_created_at = Column(DateTime, nullable=True)  # When dynamic table was created
    
    # Relationships
    document = relationship("CSVDocument", cascade="all, delete-orphan", single_parent=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "filename": self.filename,
            "file_type": self.file_type,
            "dynamic_table_name": self.dynamic_table_name,
            "data_category": self.data_category,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "is_described": bool(self.is_described),
            "verified_at": str(self.verified_at) if self.verified_at else None,
            "upload_date": str(self.upload_date),
            "table_created_at": str(self.table_created_at) if self.table_created_at else None,
        }


class KnowledgeBase(Base):
    """Model for knowledge base entries created after LLM analysis"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("csv_documents.id"), nullable=False, unique=True)
    filename = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    data_category = Column(String(255), nullable=False)
    insights = Column(JSON, nullable=False)
    use_cases = Column(JSON, nullable=False)
    column_analysis = Column(JSON, nullable=False)
    data_quality_score = Column(Float, nullable=False)
    recommendations = Column(JSON, nullable=False)
    column_metadata = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("CSVDocument", back_populates="knowledge_base")
    
    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "filename": self.filename,
            "summary": self.summary,
            "data_category": self.data_category,
            "insights": self.insights,
            "use_cases": self.use_cases,
            "column_analysis": self.column_analysis,
            "data_quality_score": self.data_quality_score,
            "recommendations": self.recommendations,
            "column_metadata": self.column_metadata,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }


class User(Base):
    """Model for user accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
