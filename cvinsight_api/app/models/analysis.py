from app.db.database import Base
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.sql import func


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    raw_text = Column(Text, nullable=True)

    # Scores
    overall_score = Column(Float, nullable=True)
    ats_score = Column(Float, nullable=True)

    # AI results stored as JSON
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    suggestions = Column(JSON, default=list)
    keywords_found = Column(JSON, default=list)
    keywords_missing = Column(JSON, default=list)
    interview_questions = Column(JSON, default=list)
    rewritten_summary = Column(Text, nullable=True)

    # Job match
    job_description = Column(Text, nullable=True)
    job_match_score = Column(Float, nullable=True)
    job_missing_skills = Column(JSON, default=list)
    job_matched_skills = Column(JSON, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
