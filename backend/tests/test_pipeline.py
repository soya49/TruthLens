from app.analyzer.pipeline import analyze_statement
from app.schemas import AnalysisRequest, Assessment


def test_statement_is_not_labelled_as_lie():
    response = analyze_statement(AnalysisRequest(statement="I arrived around 8 pm."))

    assert response.claims[0].assessment == Assessment.AMBIGUOUS
    assert all(claim.assessment != "LYING" for claim in response.claims)


def test_explicit_numeric_change_is_flagged_for_review():
    response = analyze_statement(
        AnalysisRequest(
            statement="I arrived at 10 pm.",
            previous_statements=["I arrived at 8 pm."],
        )
    )

    assert len(response.findings) == 1
    assert response.findings[0].title == "Potential factual conflict"
