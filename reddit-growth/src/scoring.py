from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scores:
    relevance: float
    audience_match: float
    problem_severity: float
    engagement_potential: float
    value_fit: float
    promotion_opportunity: float
    rule_risk: float

    @property
    def opportunity(self) -> float:
        positive = (
            self.relevance
            + self.audience_match
            + self.problem_severity
            + self.engagement_potential
            + self.value_fit
            + self.promotion_opportunity
        )
        # Rule risk is a penalty: 10 means highest risk.
        return max(0.0, min(100.0, positive / 60.0 * 100.0 - self.rule_risk * 5.0))


def score_post(*, relevance: float, audience_match: float, problem_severity: float,
               engagement_potential: float, value_fit: float,
               promotion_opportunity: float, rule_risk: float) -> Scores:
    values = locals().values()
    if any(not 0 <= float(v) <= 10 for v in values):
        raise ValueError("All scores must be between 0 and 10")
    return Scores(
        relevance, audience_match, problem_severity, engagement_potential,
        value_fit, promotion_opportunity, rule_risk
    )
