"""Orchestrate payload creation, provider calls, and report validation."""

from collections.abc import Sequence

from src.ai_provider import AI_REPORT_SCHEMA, AIProvider
from src.ai_report_models import AIReportGenerationResult
from src.ai_report_payload import build_ai_report_payload
from src.ai_report_validator import AIReportValidationError, validate_ai_report
from src.diagnosis_models import DiagnosticFinding, DiagnosisContext


def generate_ai_report(
    context: DiagnosisContext,
    findings: Sequence[DiagnosticFinding],
    provider: AIProvider | None,
) -> AIReportGenerationResult:
    """Run the provider-neutral AI report chain without affecting diagnosis."""
    if not findings:
        return AIReportGenerationResult(
            status="unavailable",
            message="当前没有可生成 AI 报告的诊断问题。",
        )
    if provider is None:
        return AIReportGenerationResult(
            status="unavailable",
            message="当前未配置 AI 服务，可继续查看确定性诊断结果。",
        )

    payload = build_ai_report_payload(context, findings)
    try:
        raw_report = provider.generate_report(payload, AI_REPORT_SCHEMA)
    except Exception:
        return AIReportGenerationResult(
            status="provider_error",
            message="AI 报告生成失败，确定性诊断结果不受影响。",
        )

    try:
        report = validate_ai_report(raw_report, findings)
    except AIReportValidationError:
        return AIReportGenerationResult(
            status="validation_error",
            message="AI 报告未通过校验，确定性诊断结果不受影响。",
        )

    return AIReportGenerationResult(
        status="success",
        report=report,
        message="AI 报告生成成功。",
    )


__all__ = ["generate_ai_report"]
