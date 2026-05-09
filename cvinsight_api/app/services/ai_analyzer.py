"""
AI Analyzer Service
Sends CV text to Ollama or OpenAI and parses structured analysis output.
"""
import json
import re
import logging
import httpx
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

# Global persistent client for connection pooling (reused across requests)
_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0))
    return _client


# ---------------------------------------------------------------------------
# Prompts — Use concrete example values so the model learns the format
# ---------------------------------------------------------------------------

ANALYSIS_PROMPT = """Analyze this resume for ATS compatibility. 
Return ONLY JSON with these keys: 
overall_score (0-100), ats_score (0-100), strengths (list), weaknesses (list), suggestions (list), keywords_found (list), keywords_missing (list), interview_questions (list), rewritten_summary (string).

Resume:
{cv_text}
"""

JOB_MATCH_PROMPT = """Compare resume vs job description.
Return ONLY JSON: match_score (0-100), matched_skills (list), missing_skills (list), recommendation (string).

Resume: {cv_text}
JD: {job_description}
"""

COVER_LETTER_PROMPT = """Generate a {tone} cover letter.
Return ONLY JSON: cover_letter (string).

Resume: {cv_text}
JD: {job_description}
"""


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------

async def analyze_cv(cv_text: str) -> Dict[str, Any]:
    """Run full AI analysis on extracted CV text."""
    prompt = ANALYSIS_PROMPT.format(cv_text=cv_text[:4000])

    if settings.AI_PROVIDER == "openai":
        result = await _call_openai(prompt)
    else:
        result = await _call_ollama(prompt, max_tokens=2048)

    return _normalize_analysis_result(result)


async def match_job(cv_text: str, job_description: str) -> Dict[str, Any]:
    """Match CV against a job description."""
    prompt = JOB_MATCH_PROMPT.format(
        cv_text=cv_text[:3000],
        job_description=job_description[:2000]
    )

    if settings.AI_PROVIDER == "openai":
        result = await _call_openai(prompt)
    else:
        result = await _call_ollama(prompt, max_tokens=1024)

    return _normalize_job_match_result(result)


async def generate_cover_letter(cv_text: str, job_description: str, tone: str = "professional") -> str:
    """Generate a tailored cover letter."""
    prompt = COVER_LETTER_PROMPT.format(
        cv_text=cv_text[:3000],
        job_description=job_description[:2000],
        tone=tone
    )

    if settings.AI_PROVIDER == "openai":
        result = await _call_openai(prompt)
    else:
        result = await _call_ollama(prompt, max_tokens=2048)

    letter = result.get("cover_letter", "")
    if not letter:
        logger.warning("generate_cover_letter: AI returned empty cover_letter. Raw result: %s", result)
    return letter


# ---------------------------------------------------------------------------
# Internal API callers
# ---------------------------------------------------------------------------

async def _call_ollama(prompt: str, max_tokens: int = 2048) -> Dict[str, Any]:
    """Call Ollama Chat API using persistent client."""
    client = _get_client()
    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": "You are an ATS resume analyzer. Respond ONLY with valid JSON. No explanations."},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "num_predict": max_tokens,
        },
    }
    try:
        response = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        raw = data.get("message", {}).get("content", "")
        
        logger.debug("Ollama raw response (first 300 chars): %s", raw[:300])
        if not raw:
            logger.error("Ollama returned empty response. Full data: %s", data)
            return {}
        return _parse_json(raw)
    except httpx.TimeoutException:
        logger.error("Ollama request timed out after 300s")
        return {}
    except httpx.HTTPStatusError as e:
        logger.error("Ollama HTTP error %s: %s", e.response.status_code, e.response.text[:200])
        return {}
    except Exception as e:
        logger.error("Ollama unexpected error: %s", e)
        return {}


async def _call_openai(prompt: str) -> Dict[str, Any]:
    """Call OpenAI API."""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert resume and ATS analyst. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
            timeout=300.0,
        )
        raw = response.choices[0].message.content or "{}"
        return _parse_json(raw)
    except Exception as e:
        logger.error("OpenAI error: %s", e)
        return {}


# ---------------------------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------------------------

def _parse_json(raw: str) -> Dict[str, Any]:
    """Safely parse JSON from AI response."""
    # Strip markdown code blocks
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to extract the first JSON object
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.warning("_parse_json: Failed to parse JSON. Raw (first 300): %s", raw[:300])
    return {}


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

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
        score = int(round(float(str(value).split("-")[0].strip())))
    except (TypeError, ValueError):
        return None
    return max(0, min(100, score))


def _coerce_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if item is not None and str(item).strip()]


def _coerce_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
