from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, String
from sqlalchemy.dialects.mysql import LONGTEXT
from typing import Optional, List
from datetime import datetime

class UserPreferences(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    linkedin_search_url: str
    keywords: str  # Comma separated
    exclude_keywords: Optional[str] = None
    cv_text: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    report_times: str = Field(default="09:00,18:00")
    is_active: bool = Field(default=True)
    is_scanning: bool = Field(default=False)
    target_status: str = Field(default="Student") # Student, Graduate, Intern

class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    linkedin_job_id: str = Field(index=True, unique=True)
    title: str
    company: str
    location: str
    url: str
    posted_date: Optional[datetime] = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    match_score: Optional[float] = None
    seniority_requirement: Optional[str] = None # Student, Junior, Senior, etc.
    is_reported: bool = Field(default=False)
