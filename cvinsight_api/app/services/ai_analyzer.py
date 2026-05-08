"""
AI Analyzer Service
Sends CV text to Ollama or OpenAI and parses structured analysis output.
"""
import json
import re
import httpx
from typing import Dict, Any
from app.config import settings


ANALYSIS_PROMPT = """You are an expert ATS (Applicant Tracking System) and professional resume reviewer.
Analyze the following resume text and respond ONLY with a valid JSON object.

Resume Text:
\"\"\"
{cv_text}
\"\"\"

Respond with EXACTLY this JSON structure (no markdown, no extra text):
{{
  "overall_score": <integer 0-100>,
  "ats_score": <integer 0-100>,
  "strengths": [<list of 3-5 strength strings>],
  "weaknesses": [<list of 3-5 weakness strings>],
  "suggestions": [<list of 4-6 actionable suggestion strings>],
  "keywords_found": [<list of detected ATS keywords/skills>],
  "keywords_missing": [<list of commonly expected keywords that are missing>],
  "interview_questions": [<list of 5 likely interview questions based on this CV>],
  "rewritten_summary": "<a professionally rewritten summary/objective section, 3-4 sentences>"
}}
"""

JOB_MATCH_PROMPT = """You are an expert ATS recruiter. Compare this resume against the job description.
Respond ONLY with a valid JSON object.

Resume:
\"\"\"
{cv_text}
\"\"\"

Job Description:
\"\"\"
{job_description}
\"\"\"

Respond with EXACTLY this JSON structure:
{{
  "match_score": <integer 0-100>,
  "matched_skills": [<list of skills/keywords present in both>],
  "missing_skills": [<list of skills in JD but not in resume>],
  "recommendation": "<2-3 sentence recommendation on how to tailor the resume>"
}}
"""


async def analyze_cv(cv_text: str) -> Dict[str, Any]:
    """Run full AI analysis on extracted CV text."""
    prompt = ANALYSIS_PROMPT.format(cv_text=cv_text[:6000])  # token limit guard

    if settings.AI_PROVIDER == "openai":
        result = await _call_openai(prompt)
    else:
        result = await _call_ollama(prompt)

    return _normalize_analysis_result(result)


async def match_job(cv_text: str, job_description: str) -> Dict[str, Any]:
    """Match CV against a job description."""
    prompt = JOB_MATCH_PROMPT.format(
        cv_text=cv_text[:4000],
        job_description=job_description[:3000]
    )

    if settings.AI_PROVIDER == "openai":
        result = await _call_openai(prompt)
    else:
        result = await _call_ollama(prompt)

    return _normalize_job_match_result(result)


async def _call_ollama(prompt: str) -> Dict[str, Any]:
    """Call local Ollama API."""
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1},
            },
        )
        response.raise_for_status()
        data = response.json()
        raw = data.get("response", "{}")
        return _parse_json(raw)


async def _call_openai(prompt: str) -> Dict[str, Any]:
    """Call OpenAI API."""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert resume and ATS analyst. Always respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
        timeout=300.0,
    )
    raw = response.choices[0].message.content or "{}"
    return _parse_json(raw)


def _parse_json(raw: str) -> Dict[str, Any]:
    """Safely parse JSON from AI response."""
    try:
        # Strip markdown code blocks if present
        raw = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`")
        return json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract JSON from response
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return {}


def _normalize_analysis_result(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "overall_score": _coerce_score(result.get("overall_score")),
        "ats_score": _coerce_score(result.get("ats_score")),
        "strengths": _coerce_string_list(result.get("strengths")),
        "weaknesses": _coerce_string_list(result.get("weaknesses")),
        "suggestions": _coerce_string_list(result.get("suggestions")),
        "keywords_found": _coerce_string_list(result.get("keywords_found")),
        "keywords_missing": _coerce_string_list(result.get("keywords_missing")),
        "interview_questions": _coerce_string_list(result.get("interview_questions")),
        "rewritten_summary": _coerce_optional_string(result.get("rewritten_summary")),
    }


def _normalize_job_match_result(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "match_score": _coerce_score(result.get("match_score")),
        "matched_skills": _coerce_string_list(result.get("matched_skills")),
        "missing_skills": _coerce_string_list(result.get("missing_skills")),
        "recommendation": _coerce_optional_string(result.get("recommendation")),
    }


def _coerce_score(value: Any) -> int | None:
    if value is None or value == "":
        return None

    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        return None

    return max(0, min(100, score))


def _coerce_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    cleaned_items: list[str] = []
    for item in value:
        if item is None:
            continue

        text = str(item).strip()
        if text:
            cleaned_items.append(text)

    return cleaned_items


def _coerce_optional_string(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    return text or None
