from app.analyzer.claim_extractor import extract_claims
from app.analyzer.contradictions import compare_claims
from app.analyzer.linguistic import inspect_language
from app.schemas import AnalysisRequest, AnalysisResponse, Assessment, Claim, Finding


DISCLAIMER = (
    "TruthLens evaluates statements and evidence; it does not determine whether a person is lying. "
    "Observations are not proof of deception."
)


def analyze_statement(request: AnalysisRequest) -> AnalysisResponse:
    claims = extract_claims(request.statement)
    claim_models: list[Claim] = []
    for text in claims:
        observations = inspect_language(text)
        claim_models.append(
            Claim(
                text=text,
                observations=observations,
                assessment=(Assessment.AMBIGUOUS if observations else Assessment.UNVERIFIED),
            )
        )

    findings: list[Finding] = []
    for current, previous in compare_claims(claims, request.previous_statements):
        findings.append(
            Finding(
                title="Potential factual conflict",
                explanation="The statements contain different explicit numeric or date-like references. "
                "This requires context review and is not evidence of intentional deception.",
                observations=[f"Current statement: {current}", f"Earlier statement: {previous}"],
                alternative_explanations=[
                    "The statements may refer to different events.",
                    "One value may be approximate or a later correction.",
                ],
                follow_up_questions=["Are these references about the same event and time period?"],
            )
        )

    return AnalysisResponse(
        disclaimer=DISCLAIMER,
        mode="deterministic-baseline",
        claims=claim_models,
        findings=findings,
        follow_up_questions=[
            "Which parts of this account can be checked against independent evidence?",
            "Are any dates, locations, or participants approximate?",
        ],
    )
