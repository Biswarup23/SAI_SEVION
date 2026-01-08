import os
import time
import random
import uuid
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from openai import OpenAI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.deps import get_db  # your DB dependency that returns Session

router = APIRouter(prefix="/polish", tags=["polish"])

MAX_CHARS = 20_000
MAX_RETRIES = 4


def build_system_prompt(mode: Dict[str, Any]) -> str:
    action = (mode or {}).get("action", "Program")
    lang_or_db = (mode or {}).get("lang", "Python")

    base_rules = (
        "IDENTITY RULE:\n"
        "- If the user mentions company, you MUST reply with:\n"
        "  Company: SAI Devion\n"
        "  Parent company: SAI\n\n"
        "ROLE RULE:\n"
        "- You are an AI Software Engineer.\n"
        "- The user may ask in normal question form.\n"
        "- You must convert the user's question into the requested output type.\n\n"
        "STRICT OUTPUT RULES:\n"
        "- Output PLAIN TEXT ONLY.\n"
        "- NEVER use markdown, backticks, or code fences.\n"
        "- Do NOT include explanations, steps, or commentary (unless explicitly allowed below).\n"
        "- If unclear/missing details, make reasonable defaults and still output something valid.\n"
        "- If impossible to proceed, output a short plain-text error only.\n"
    )

    if action == "Program":
        return (
            base_rules
            + "\nPROGRAM MODE:\n"
            + f"- Language: {lang_or_db}\n"
            + "- The user will ask a question; you MUST answer by generating ONLY executable code.\n"
            + "- Add exactly ONE single-line comment at the TOP summarizing what the script does.\n"
            + "- No additional text before/after code.\n"
        )

    if action == "Query":
        db = lang_or_db

        if str(db).lower() == "mongodb":
            return (
                base_rules
                + "\nQUERY MODE (MongoDB):\n"
                + "- The user will ask a question; you MUST answer by outputting ONLY a valid MongoDB query or aggregation JSON.\n"
                + "- Do NOT output SQL.\n"
                + "- Assume collection name `collection` if missing.\n"
                + "- No commentary.\n"
            )

        return (
            base_rules
            + "\nQUERY MODE (SQL):\n"
            + f"- Dialect: {db}\n"
            + "- The user will ask a question; you MUST answer by outputting ONLY ONE final SQL query for this dialect.\n"
            + "- Do NOT include explanations.\n"
            + "- SQL comments using -- are allowed.\n"
        )

    return "Invalid mode. Only Program or Query is supported."


class PolishRequest(BaseModel):
    text: str = Field(..., min_length=1)
    mode: Dict[str, Any] = Field(default_factory=dict)
    user_id: int | None = None


def _openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def _call_openai_with_retry(
    client: OpenAI,
    model: str,
    instructions: str,
    user_input: str,
):
    for attempt in range(MAX_RETRIES + 1):
        try:
            return client.responses.create(
                model=model,
                instructions=instructions,
                input=user_input,
                temperature=0.2,
            )
        except Exception as e:
            msg = str(e).lower()
            retryable = (
                ("rate limit" in msg)
                or ("429" in msg)
                or ("timeout" in msg)
                or ("temporarily" in msg)
            )
            if attempt >= MAX_RETRIES or not retryable:
                raise
            time.sleep((2**attempt) + random.random())


@router.post("")
def polish(req: PolishRequest, db: Session = Depends(get_db)):
    raw_text = (req.text or "").strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Text is required.")

    if len(raw_text) > MAX_CHARS:
        raise HTTPException(
            status_code=413, detail=f"Text too large. Max {MAX_CHARS} chars."
        )

    mode = req.mode or {}
    action = mode.get("action", "Query")
    lang = mode.get("lang", "MySQL")

    system_prompt = build_system_prompt(mode)
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    request_uid = str(uuid.uuid4())
    started = time.perf_counter()

    # Insert placeholder row (status=error by default)
    db.execute(
        text(
            """
            INSERT INTO ai_requests
            (request_uid, user_id, mode_action, mode_lang, input_text, status, model, created_at)
            VALUES
            (:request_uid, :user_id, :mode_action, :mode_lang, :input_text, 'error', :model, NOW())
            """
        ),
        {
            "request_uid": request_uid,
            "user_id": req.user_id,
            "mode_action": action,
            "mode_lang": lang,
            "input_text": raw_text,
            "model": model,
        },
    )
    db.commit()

    try:
        client = _openai_client()
        resp = _call_openai_with_retry(client, model, system_prompt, raw_text)

        latency_ms = int((time.perf_counter() - started) * 1000)

        out_text = (getattr(resp, "output_text", "") or "").strip()
        openai_request_id = getattr(resp, "id", None)

        usage = getattr(resp, "usage", None)
        prompt_tokens = getattr(usage, "input_tokens", None) if usage else None
        completion_tokens = getattr(usage, "output_tokens", None) if usage else None
        total_tokens = getattr(usage, "total_tokens", None) if usage else None

        db.execute(
            text(
                """
                UPDATE ai_requests
                SET output_text=:output_text,
                    status='success',
                    error_code=NULL,
                    error_message=NULL,
                    openai_request_id=:openai_request_id,
                    latency_ms=:latency_ms,
                    prompt_tokens=:prompt_tokens,
                    completion_tokens=:completion_tokens,
                    total_tokens=:total_tokens
                WHERE request_uid=:request_uid
                """
            ),
            {
                "output_text": out_text,
                "openai_request_id": openai_request_id,
                "latency_ms": latency_ms,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "request_uid": request_uid,
            },
        )
        db.commit()

        return {"text": out_text, "request_uid": request_uid}

    except Exception as e:
        latency_ms = int((time.perf_counter() - started) * 1000)
        err_text = f"{type(e).__name__}: {e}"

        db.execute(
            text(
                """
                UPDATE ai_requests
                SET status='error',
                    error_code=:error_code,
                    error_message=:error_message,
                    latency_ms=:latency_ms
                WHERE request_uid=:request_uid
                """
            ),
            {
                "error_code": type(e).__name__,
                "error_message": err_text[:1000],
                "latency_ms": latency_ms,
                "request_uid": request_uid,
            },
        )
        db.commit()

        raise HTTPException(status_code=500, detail=err_text)
