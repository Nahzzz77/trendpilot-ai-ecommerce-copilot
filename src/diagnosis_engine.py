"""Execute and rank the MVP deterministic diagnosis rules."""

from src.diagnosis_models import DiagnosticFinding, DiagnosisContext
from src.diagnosis_rules import (
    detect_ad_spend_growth_without_sales_growth,
    detect_conversion_decline,
    detect_gross_margin_decline,
    detect_inventory_days_anomaly,
    detect_key_product_sales_decline,
    detect_refund_rate_increase,
    detect_roas_decline,
    detect_sales_decline,
    detect_visitor_decline,
)
from src.diagnosis_scoring import calculate_priority


def run_diagnosis(context: DiagnosisContext) -> list[DiagnosticFinding]:
    """Run every MVP rule and return findings in deterministic priority order."""
    detectors = (
        detect_sales_decline,
        detect_visitor_decline,
        detect_conversion_decline,
        detect_roas_decline,
        detect_ad_spend_growth_without_sales_growth,
        detect_gross_margin_decline,
        detect_refund_rate_increase,
        detect_inventory_days_anomaly,
        detect_key_product_sales_decline,
    )
    findings = [finding for detector in detectors for finding in detector(context)]
    return sorted(
        findings,
        key=lambda finding: (
            -finding.priority_score,
            finding.rule_id,
            finding.finding_id,
        ),
    )


__all__ = ["calculate_priority", "run_diagnosis"]
