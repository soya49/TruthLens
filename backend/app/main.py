import json
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.ai_service import provider_status
from app.analyzer.advanced import compare_word_usage, semantic_observations
from app.analyzer.conversation import parse_conversation
from app.analyzer.evidence import extract_text, validate_upload
from app.analyzer.pipeline import DISCLAIMER, analyze_statement
from app.analyzer.timeline import build_timeline
from app.analyzer.media import inspect_media
from app.config import settings
from app.database import Base, engine, get_db
from app.models import Analysis, User
from app.schemas import AnalysisRequest, AnalysisResponse, AuthRequest, AuthResponse, HistoryItem
from app.security import create_access_token, get_current_user, hash_password, verify_password


Base.metadata.create_all(bind=engine)
app = FastAPI(title="TruthLens API", version="1.0.0")
allowed_origins = {settings.frontend_url}
if settings.environment.lower() != "production":
    allowed_origins.update({"http://localhost:5173", "http://127.0.0.1:5173"})
app.add_middleware(CORSMiddleware, allow_origins=sorted(allowed_origins), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


def save_analysis(db: Session, user: User, analysis_type: str, title: str, input_text: str, result: dict) -> None:
    db.add(Analysis(user_id=user.id, analysis_type=analysis_type, title=title[:200], input_text=input_text, result_json=json.dumps(result)))
    db.commit()


def result_for(request: AnalysisRequest, kind: str = "statement") -> AnalysisResponse:
    result = analyze_statement(request)
    result.metadata.update({"analysis_type": kind, "provider": provider_status()})
    for claim in result.claims:
        claim.observations.extend(semantic_observations(claim.text))
    return result


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "mode": provider_status()}


@app.post("/api/auth/register", response_model=AuthResponse)
def register(request: AuthRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email = request.email.strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with that email already exists.")
    user = User(email=email, password_hash=hash_password(request.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with that email already exists.")
    db.refresh(user)
    return AuthResponse(access_token=create_access_token(user.id))


@app.post("/api/auth/login", response_model=AuthResponse)
def login(request: AuthRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == request.email.strip().lower()))
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return AuthResponse(access_token=create_access_token(user.id))


@app.get("/api/auth/profile")
def profile(user: User = Depends(get_current_user)) -> dict[str, object]:
    return {"id": user.id, "email": user.email, "created_at": user.created_at.isoformat()}


@app.post("/api/analyze/statement", response_model=AnalysisResponse)
def statement_analysis(request: AnalysisRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> AnalysisResponse:
    result = result_for(request)
    save_analysis(db, user, "statement", "Statement analysis", request.statement, result.model_dump())
    return result


@app.post("/api/analyze/conversation")
def conversation_analysis(request: AnalysisRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, object]:
    turns = parse_conversation(request.statement)
    result = result_for(request, "conversation")
    result.metadata["turns"] = turns
    save_analysis(db, user, "conversation", "Conversation analysis", request.statement, result.model_dump())
    return result.model_dump()


@app.post("/api/analyze/compare")
def compare_analysis(request: AnalysisRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, object]:
    versions = [request.statement, *request.previous_statements]
    result = result_for(request, "comparison")
    result.metadata["versions"] = len(versions)
    result.metadata["comparison_observations"] = compare_word_usage(versions)
    save_analysis(db, user, "comparison", "Story comparison", "\n---\n".join(versions), result.model_dump())
    return result.model_dump()


@app.post("/api/analyze/timeline")
def timeline_analysis(request: AnalysisRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, object]:
    result = result_for(request, "timeline")
    result.metadata["timeline"] = build_timeline(request.statement)
    save_analysis(db, user, "timeline", "Timeline analysis", request.statement, result.model_dump())
    return result.model_dump()


@app.post("/api/analyze/evidence")
async def evidence_analysis(claim: str = Form(...), evidence: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, object]:
    content = await evidence.read(settings.max_upload_bytes + 1)
    try:
        validate_upload(evidence.filename, evidence.content_type, len(content), settings.max_upload_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    extracted, extraction_mode = extract_text(evidence.filename or "evidence", evidence.content_type, content)
    result = {"disclaimer": DISCLAIMER, "mode": extraction_mode, "claim": claim, "evidence_filename": Path(evidence.filename or "evidence").name, "extracted_text": extracted[:20_000], "assessment": "UNVERIFIED", "observations": ["Uploaded evidence is not automatically authentic or independently verified."], "provider": provider_status()}
    save_analysis(db, user, "evidence", "Evidence analysis", claim, result)
    return result


@app.post("/api/analyze/media")
async def media_analysis(media: UploadFile = File(...), user: User = Depends(get_current_user)) -> dict[str, object]:
    content = await media.read(settings.max_upload_bytes + 1)
    try:
        details = inspect_media(media.filename, media.content_type, len(content), settings.max_upload_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"disclaimer": DISCLAIMER, "mode": "metadata-only", "details": details, "observations": ["Audio/video signal interpretation is not enabled in this build.", "No facial, vocal, pause, or behavioural feature is treated as evidence of deception."], "next_step": "Configure a reviewed transcription or media-processing provider before enabling derived observations."}


@app.get("/api/history", response_model=list[HistoryItem])
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[HistoryItem]:
    rows = db.scalars(select(Analysis).where(Analysis.user_id == user.id).order_by(Analysis.created_at.desc())).all()
    return [HistoryItem(id=row.id, analysis_type=row.analysis_type, title=row.title, created_at=row.created_at.isoformat()) for row in rows]


@app.get("/api/history/{analysis_id}")
def history_detail(analysis_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, object]:
    row = db.scalar(select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user.id))
    if row is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return {"id": row.id, "analysis_type": row.analysis_type, "title": row.title, "created_at": row.created_at.isoformat(), "result": json.loads(row.result_json)}


@app.delete("/api/history/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history(analysis_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> None:
    row = db.scalar(select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user.id))
    if row is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    db.delete(row)
    db.commit()
