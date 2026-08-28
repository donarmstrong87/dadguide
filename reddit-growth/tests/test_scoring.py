from src.scoring import score_post


def test_score_is_bounded():
    score = score_post(
        relevance=10,
        audience_match=10,
        problem_severity=10,
        engagement_potential=10,
        value_fit=10,
        promotion_opportunity=10,
        rule_risk=0,
    )
    assert score.opportunity == 100


def test_rule_risk_reduces_score():
    low = score_post(relevance=8, audience_match=8, problem_severity=8, engagement_potential=8, value_fit=8, promotion_opportunity=8, rule_risk=0)
    high = score_post(relevance=8, audience_match=8, problem_severity=8, engagement_potential=8, value_fit=8, promotion_opportunity=8, rule_risk=10)
    assert high.opportunity < low.opportunity
