"""
API Router — Analysis Endpoints
POST /api/upload
POST /api/analyze
POST /api/job-match
GET  /api/history
GET  /api/analysis/{id}
"""
import uuid
import aiofiles
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.database import get_db
from app.models.analysis import Analysis
from app.schemas.analysis import (
    AnalysisRequest, JobMatchRequest,
    AnalysisResult, UploadResponse, HistoryItem
)
from app.services import cv_parser, ai_analyzer
from app.config import settings

router = APIRouter(prefix="/api", tags=["analysis"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}


@router.post("/upload", response_model=UploadResponse)
async def upload_cv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a CV file (PDF or DOCX)."""
    suffix = Path(file.filename or "").suffix.lower()
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Use PDF or DOCX."
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="File too large.")

    # Save file
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    file_path = upload_dir / unique_name

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Extract text
    try:
        raw_text = cv_parser.extract_text(str(file_path))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse file: {e}")

    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="No readable text found in the uploaded file.")

    # Save to DB
    analysis = Analysis(
        filename=file.filename,
        file_path=str(file_path),
        raw_text=raw_text,
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return UploadResponse(
        analysis_id=analysis.id,
        filename=file.filename,
        message="File uploaded and parsed successfully.",
    )


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_cv(
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """Run AI analysis on an uploaded CV."""
    analysis = await _get_analysis_or_404(db, request.analysis_id)

    if not analysis.raw_text:
        raise HTTPException(status_code=422, detail="No text found in uploaded CV.")

    try:
        result = await ai_analyzer.analyze_cv(analysis.raw_text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {e}")

    # Persist results
    analysis.overall_score = result.get("overall_score")
    analysis.ats_score = result.get("ats_score")
    analysis.strengths = result.get("strengths", [])
    analysis.weaknesses = result.get("weaknesses", [])
    analysis.suggestions = result.get("suggestions", [])
    analysis.keywords_found = result.get("keywords_found", [])
    analysis.keywords_missing = result.get("keywords_missing", [])
    analysis.interview_questions = result.get("interview_questions", [])
    analysis.rewritten_summary = result.get("rewritten_summary")

    await db.commit()
    await db.refresh(analysis)
    return analysis


@router.post("/job-match", response_model=AnalysisResult)
async def job_match(
    request: JobMatchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Match CV against a job description."""
    analysis = await _get_analysis_or_404(db, request.analysis_id)

    if not analysis.raw_text:
        raise HTTPException(status_code=422, detail="No text found in uploaded CV.")

    try:
        result = await ai_analyzer.match_job(analysis.raw_text, request.job_description)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Job match failed: {e}")

    analysis.job_description = request.job_description
    analysis.job_match_score = result.get("match_score")
    analysis.job_matched_skills = result.get("matched_skills", [])
    analysis.job_missing_skills = result.get("missing_skills", [])

    await db.commit()
    await db.refresh(analysis)
    return analysis


@router.get("/history", response_model=list[HistoryItem])
async def get_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Return list of past analyses."""
    stmt = select(Analysis).order_by(desc(Analysis.created_at)).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/analysis/{analysis_id}", response_model=AnalysisResult)
async def get_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Fetch a specific analysis by ID."""
    return await _get_analysis_or_404(db, analysis_id)


async def _get_analysis_or_404(db: AsyncSession, analysis_id: int) -> Analysis:
    stmt = select(Analysis).where(Analysis.id == analysis_id)
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis
