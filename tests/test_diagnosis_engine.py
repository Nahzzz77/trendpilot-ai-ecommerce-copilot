from dataclasses import replace

from src.diagnosis_engine import calculate_priority, run_diagnosis
from src.diagnosis_models import DiagnosticFinding, Evidence, FindingScope
from tests.test_diagnosis_rules import make_context


def test_priority_scoring_returns_high_medium_and_low() -> None:
    assert calculate_priority(impact=1.0, magnitude=1.0, completeness=1.0) == (100, "high")
    assert calculate_priority(impact=0.5, magnitude=0.5, completeness=1.0) == (60, "medium")
    assert calculate_priority(impact=0.1, magnitude=0.1, completeness=0.5) == (18, "low")


def test_priority_scoring_clamps_inputs_to_valid_range() -> None:
    assert calculate_priority(impact=2.0, magnitude=2.0, completeness=2.0) == (100, "high")
    assert calculate_priority(impact=-1.0, magnitude=-1.0, completeness=-1.0) == (0, "low")


def test_run_diagnosis_combines_rules_and_sorts_by_priority() -> None:
    context = make_context(
        current_kpis={"units_sold": 100},
        comparison={"sales_amount": -0.20, "visitors": -0.05},
    )

    findings = run_diagnosis(context)

    assert [finding.rule_id for finding in findings] == [
        "R001_SALES_DECLINE",
        "R002_VISITOR_DECLINE",
    ]
    assert findings[0].priority_score >= findings[1].priority_score


def test_finding_model_contains_required_contract() -> None:
    evidence = Evidence(
        metric_key="sales_amount",
        current_value=90.0,
        baseline_value=100.0,
        change_value=-0.10,
        change_type="relative",
        unit="currency",
    )
    finding = DiagnosticFinding(
        finding_id="sales-decline-overall",
        rule_id="R001_SALES_DECLINE",
        dimension="sales",
        scope=FindingScope(scope_type="overall", scope_id=None, scope_name="全店"),
        title="销售额下降",
        evidence=(evidence,),
        priority_score=80,
        priority="high",
        cause_candidate_ids=("C001_TRAFFIC_DECLINE",),
        action_candidate_ids=("A001_REVIEW_SALES_FUNNEL",),
    )

    assert finding.finding_id == "sales-decline-overall"
    assert finding.scope.scope_name == "全店"
    assert finding.evidence == (evidence,)
    assert finding.cause_candidate_ids == ("C001_TRAFFIC_DECLINE",)
    assert finding.action_candidate_ids == ("A001_REVIEW_SALES_FUNNEL",)
    assert replace(finding, priority="medium").priority == "medium"
