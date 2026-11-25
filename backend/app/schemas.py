from enum import StrEnum

from pydantic import BaseModel, Field


class Assessment(StrEnum):
    CONSISTENT = "CONSISTENT"
    POTENTIAL_CONTRADICTION = "POTENTIAL_CONTRADICTION"
    SUPPORTED_BY_EVIDENCE = "SUPPORTED_BY_EVIDENCE"
    CONTRADICTED_BY_EVIDENCE = "CONTRADICTED_BY_EVIDENCE"
    UNVERIFIED = "UNVERIFIED"
    INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION"
    AMBIGUOUS = "AMBIGUOUS"


class AnalysisRequest(BaseModel):
    statement: str = Field(min_length=1, max_length=50_000)
    context: str | None = Field(default=None, max_length=20_000)
    previous_statements: list[str] = Field(default_factory=list, max_length=20)


class Claim(BaseModel):
    text: str
    observations: list[str] = Field(default_factory=list)
    assessment: Assessment


class Finding(BaseModel):
    title: str
    explanation: str
    observations: list[str] = Field(default_factory=list)
    alternative_explanations: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    disclaimer: str
    mode: str
    claims: list[Claim]
    findings: list[Finding]
    follow_up_questions: list[str]
    metadata: dict[str, object] = Field(default_factory=dict)


class AuthRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class HistoryItem(BaseModel):
    id: int
    analysis_type: str
    title: str
    created_at: str
