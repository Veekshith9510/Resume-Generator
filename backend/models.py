# Copyright (c) 2025 Veekshith Gullapudi. All rights reserved.

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class JobPost(Base):
    """
    Database model for storing job postings.
    Stores the URL, raw description text, and timestamp.
    """
    __tablename__ = "job_posts"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Resume(Base):
    """
    Database model for storing uploaded resumes.
    Stores the original filename, extracted text content, and file path.
    """
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content = Column(Text) # Storing extracted text for now
    original_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
