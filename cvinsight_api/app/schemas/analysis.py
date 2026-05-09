from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AnalysisRequest(BaseModel):
    analysis_id: int


class JobMatchRequest(BaseModel):
    analysis_id: int
    job_description: str


class CoverLetterRequest(BaseModel):
    analysis_id: int
    job_description: str
    tone: str = "professional"  # professional, creative, concise


class AnalysisResult(BaseModel):
    id: int
    filename: str
    overall_score: Optional[float] = None
    ats_score: Optional[float] = None
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    keywords_found: List[str] = Field(default_factory=list)
    keywords_missing: List[str] = Field(default_factory=list)
    interview_questions: List[str] = Field(default_factory=list)
    rewritten_summary: Optional[str] = None
    job_match_score: Optional[float] = None
    job_missing_skills: List[str] = Field(default_factory=list)
    job_matched_skills: List[str] = Field(default_factory=list)
    job_recommendation: Optional[str] = None
    job_description: Optional[str] = None
    cover_letter: Optional[str] = None
    cover_letter_jd: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    analysis_id: int
    filename: str
    message: str


class HistoryItem(BaseModel):
    id: int
    filename: str
    overall_score: Optional[float] = None
    ats_score: Optional[float] = None
    job_match_score: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
