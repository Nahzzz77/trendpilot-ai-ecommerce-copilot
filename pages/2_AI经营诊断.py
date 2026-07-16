"""TrendPilot deterministic operating diagnosis page."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.ai_provider import AIProvider
from src.ai_report_models import AIReport, AIReportGenerationResult
from src.ai_report_service import generate_ai_report
from src.data_processor import AnalysisDataError, prepare_analysis_data
from src.diagnosis_catalog import ACTION_CATALOG, CAUSE_CATALOG
from src.diagnosis_context import DiagnosisContextError, build_diagnosis_context
from src.diagnosis_engine import run_diagnosis
from src.diagnosis_models import DiagnosisContext, DiagnosticFinding, Evidence
from src.providers.openai_provider import create_openai_provider


DATA_SESSION_KEY = "sales_data"
SOURCE_SESSION_KEY = "sales_data_source"
AI_REPORT_PROVIDER_SESSION_KEY = "ai_report_provider"
AI_REPORT_RESULT_SESSION_KEY = "ai_report_result"
AI_REPORT_SCOPE_SESSION_KEY = "ai_report_scope_signature"

METRIC_LABELS = {
    "sales_amount": "销售额",
    "visitors": "访客数",
    "payment_conversion_rate": "支付转化率",
    "roas": "ROAS",
    "ad_spend": "广告投入",
    "gross_margin": "毛利率",
    "refund_rate": "退款率",
    "estimated_days_left": "库存可售天数",
    "product_sales_amount": "商品销售额",
    "previous_sales_share": "上期销售占比",
}
PRIORITY_LABELS = {"high": "高优先级", "medium": "中优先级", "low": "低优先级"}
CAUSES_BY_ID = {entry.cause_id: entry for entry in CAUSE_CATALOG}
ACTIONS_BY_ID = {entry.action_id: entry for entry in ACTION_CATALOG}


def format_evidence_value(value: float | int | None, unit: str) -> str:
    """Format one evidence value without changing its calculated precision."""
    if value is None or pd.isna(value):
        return "—"
    if unit == "currency":
        return f"¥{value:,.2f}"
    if unit == "rate":
        return f"{value:.2%}"
    if unit == "count":
        return f"{value:,.0f}"
    if unit == "days":
        return f"{value:,.1f} 天"
    return f"{value:,.2f}"


def format_evidence_change(evidence: Evidence) -> str:
    """Format the comparison convention encoded by the rule engine."""
    change = evidence.change_value
    if change is None or pd.isna(change):
        return "无法计算变化"
    if evidence.change_type == "relative":
        return f"变化 {change:+.1%}"
    if evidence.change_type == "percentage_point":
        return f"变化 {change * 100:+.2f} 个百分点"
    if evidence.unit == "rate":
        return f"高于阈值 {change * 100:+.2f} 个百分点"
    if evidence.unit == "days":
        return f"与阈值相差 {change:+.1f} 天"
    return f"变化 {change:+,.2f}"


def render_finding(finding: DiagnosticFinding) -> None:
    """Render a deterministic finding as business-facing product content."""
    with st.container(border=True):
        title_column, priority_column = st.columns([4, 1])
        with title_column:
            st.markdown(f"### {finding.title}")
            st.caption(
                f"影响对象：{finding.scope.scope_name}"
                + (f"（{finding.scope.scope_id}）" if finding.scope.scope_id else "")
            )
        with priority_column:
            st.markdown(f"**{PRIORITY_LABELS[finding.priority]}**")
            st.caption(f"优先级评分：{finding.priority_score}")

        st.markdown("**【数据证据】**")
        for evidence in finding.evidence:
            metric_name = METRIC_LABELS.get(evidence.metric_key, evidence.metric_key)
            current_value = format_evidence_value(evidence.current_value, evidence.unit)
            baseline_value = format_evidence_value(evidence.baseline_value, evidence.unit)
            st.markdown(
                f"- {metric_name}：本期 **{current_value}**，对比基准 "
                f"**{baseline_value}**，{format_evidence_change(evidence)}"
            )

        st.markdown("**【系统判断】**")
        st.write(
            f"确定性规则 {finding.rule_id} 已触发，系统识别为“{finding.title}”，"
            f"当前优先级为{PRIORITY_LABELS[finding.priority]}。"
        )

        cause_column, action_column = st.columns(2)
        with cause_column:
            st.markdown("**【可能原因】**")
            causes = [
                CAUSES_BY_ID[cause_id]
                for cause_id in finding.cause_candidate_ids
                if cause_id in CAUSES_BY_ID
            ]
            if causes:
                for cause in causes:
                    st.markdown(f"- **{cause.cause_name}**：{cause.description}")
            else:
                st.write("暂无可引用的原因候选。")

        with action_column:
            st.markdown("**【行动建议】**")
            actions = [
                ACTIONS_BY_ID[action_id]
                for action_id in finding.action_candidate_ids
                if action_id in ACTIONS_BY_ID
            ]
            if actions:
                for action in actions:
                    observe_metric = METRIC_LABELS.get(
                        action.observe_metric, action.observe_metric
                    )
                    st.markdown(
                        f"- **{action.action_name}**｜负责人：{action.owner}｜"
                        f"建议周期：{action.suggested_period}｜观察：{observe_metric}"
                    )
            else:
                st.write("暂无可引用的行动候选。")


def build_ai_report_scope_signature(
    source_name: str,
    start_date: date,
    end_date: date,
    categories: list[str],
    product_ids: list[str],
) -> tuple[object, ...]:
    """Identify the exact analysis scope that an AI report belongs to."""
    return (
        source_name,
        start_date.isoformat(),
        end_date.isoformat(),
        tuple(categories),
        tuple(product_ids),
    )


def get_ai_report_provider() -> AIProvider | None:
    """Resolve the configured provider without handling credentials in the page."""
    if AI_REPORT_PROVIDER_SESSION_KEY in st.session_state:
        return st.session_state[AI_REPORT_PROVIDER_SESSION_KEY]
    return create_openai_provider()


def render_ai_report(report: AIReport, findings: tuple[DiagnosticFinding, ...]) -> None:
    """Render only a report that has already passed the backend Validator."""
    findings_by_id = {finding.finding_id: finding for finding in findings}

    st.markdown("#### 经营摘要")
    st.write(report.executive_summary)

    st.markdown("#### AI解读｜重点问题分析")
    for explanation in report.finding_explanations:
        finding = findings_by_id[explanation.finding_id]
        with st.container(border=True):
            st.markdown(f"**{finding.title}｜{PRIORITY_LABELS[finding.priority]}**")
            st.write(explanation.explanation)
            st.caption(f"优先级说明：{explanation.why_priority}")

    if report.cross_issue_insights:
        st.markdown("#### 问题关联")
        for insight in report.cross_issue_insights:
            finding_titles = "、".join(
                findings_by_id[finding_id].title for finding_id in insight.finding_ids
            )
            st.markdown(f"- **{finding_titles}**：{insight.insight}")

    st.markdown("#### 原因假设")
    if report.cause_hypotheses:
        for hypothesis in report.cause_hypotheses:
            finding = findings_by_id[hypothesis.finding_id]
            cause = CAUSES_BY_ID[hypothesis.cause_id]
            st.markdown(f"- **{finding.title}｜{cause.cause_name}**：{hypothesis.hypothesis}")
            st.caption(f"验证方式：{hypothesis.validation_method}")
    else:
        st.write("当前报告未选择原因假设。")

    st.markdown("#### 行动建议｜行动顺序")
    if report.recommended_actions:
        for recommendation in sorted(
            report.recommended_actions,
            key=lambda item: item.action_sequence,
        ):
            finding = findings_by_id[recommendation.finding_id]
            action = ACTIONS_BY_ID[recommendation.action_id]
            observe_metric = METRIC_LABELS.get(
                action.observe_metric, action.observe_metric
            )
            st.markdown(
                f"{recommendation.action_sequence}. **{action.action_name}**｜"
                f"对应问题：{finding.title}｜观察指标：{observe_metric}"
            )
            st.caption(f"行动理由：{recommendation.reason}")
    else:
        st.write("当前报告未选择候选行动。")

    st.markdown("#### 数据限制")
    if report.limitations:
        for limitation in report.limitations:
            st.markdown(f"- {limitation}")
    else:
        st.write("当前报告未补充其他数据限制。")


def render_ai_report_result(
    result: AIReportGenerationResult,
    findings: tuple[DiagnosticFinding, ...],
) -> None:
    """Render a stable generation status and never expose invalid content."""
    if result.status == "success" and result.report is not None:
        st.success(result.message)
        render_ai_report(result.report, findings)
        return
    if result.status == "unavailable":
        st.info("当前未配置AI服务，仍可查看确定性诊断结果")
        return
    st.error(result.message)


def render_ai_report_section(
    *,
    source_name: str,
    start_date: date,
    end_date: date,
    categories: list[str],
    product_ids: list[str],
    category_scope: str,
    product_scope: str,
    context: DiagnosisContext,
    findings: tuple[DiagnosticFinding, ...],
) -> None:
    """Integrate the existing AI report service after deterministic diagnosis."""
    st.divider()
    st.subheader("AI增强分析")
    st.caption(
        f"当前分析范围：{source_name}｜{start_date.isoformat()} 至 "
        f"{end_date.isoformat()}｜{category_scope}｜{product_scope}"
    )
    st.caption(
        "AI 仅使用当前范围内的汇总指标、诊断结果和候选目录，"
        "不读取原始 CSV。"
    )

    current_scope = build_ai_report_scope_signature(
        source_name,
        start_date,
        end_date,
        categories,
        product_ids,
    )
    previous_scope = st.session_state.get(AI_REPORT_SCOPE_SESSION_KEY)
    if previous_scope != current_scope:
        st.session_state.pop(AI_REPORT_RESULT_SESSION_KEY, None)
        st.session_state[AI_REPORT_SCOPE_SESSION_KEY] = current_scope

    if not findings:
        st.session_state.pop(AI_REPORT_RESULT_SESSION_KEY, None)
        st.info("当前没有诊断问题，无需生成 AI 报告。")
        return

    provider = get_ai_report_provider()
    if st.button(
        "生成 AI 经营分析报告",
        type="primary",
        key="ai_report_generate_button",
    ):
        with st.spinner("正在组织诊断结果并生成 AI 经营分析报告…"):
            st.session_state[AI_REPORT_RESULT_SESSION_KEY] = generate_ai_report(
                context,
                findings,
                provider,
            )

    result = st.session_state.get(AI_REPORT_RESULT_SESSION_KEY)
    if result is None:
        if provider is None:
            st.info("当前未配置AI服务，仍可查看确定性诊断结果")
        else:
            st.caption("生成状态：尚未生成。确定性诊断结果不受影响。")
    else:
        render_ai_report_result(result, findings)


st.set_page_config(page_title="AI 经营诊断 | TrendPilot", page_icon="🧭", layout="wide")
st.title("AI 经营诊断")
st.caption("用确定性规则识别经营问题，并将指标证据转化为可执行的诊断卡片")

if DATA_SESSION_KEY not in st.session_state:
    st.warning("请先返回首页加载数据，再进入 AI 经营诊断。")
    st.markdown("[🏠 返回首页](../)")
    st.stop()

try:
    prepared = prepare_analysis_data(st.session_state[DATA_SESSION_KEY])
except AnalysisDataError as exc:
    st.error(f"当前数据暂时无法诊断：{exc}")
    st.markdown("[🏠 返回首页重新加载数据](../)")
    st.stop()

minimum_date = prepared["date"].min().date()
maximum_date = prepared["date"].max().date()
default_start = max(minimum_date, maximum_date - timedelta(days=29))

with st.sidebar:
    st.header("诊断筛选")
    selected_dates = st.date_input(
        "分析周期",
        value=(default_start, maximum_date),
        min_value=minimum_date,
        max_value=maximum_date,
        key="diagnosis_dates",
    )
    selected_categories = st.multiselect(
        "商品类目",
        options=sorted(prepared["category"].unique()),
        placeholder="全部类目",
        key="diagnosis_categories",
    )
    product_pool = prepared
    if selected_categories:
        product_pool = product_pool.loc[
            product_pool["category"].isin(selected_categories)
        ]
    product_options = (
        product_pool[["product_id", "product_name"]]
        .drop_duplicates()
        .sort_values("product_id")
    )
    product_labels = {
        row.product_id: f"{row.product_name}（{row.product_id}）"
        for row in product_options.itertuples(index=False)
    }
    selected_products = st.multiselect(
        "商品",
        options=list(product_labels),
        format_func=lambda product_id: product_labels[product_id],
        placeholder="全部商品",
        key="diagnosis_products",
    )

if not isinstance(selected_dates, (tuple, list)) or len(selected_dates) != 2:
    st.info("请选择完整的开始日期和结束日期。")
    st.stop()

start_date, end_date = selected_dates
source_name = st.session_state.get(SOURCE_SESSION_KEY, "未知来源")

try:
    context = build_diagnosis_context(
        st.session_state[DATA_SESSION_KEY],
        start_date,
        end_date,
        selected_categories,
        selected_products,
        source_name=source_name,
    )
except (AnalysisDataError, DiagnosisContextError) as exc:
    if "没有可诊断数据" in str(exc):
        st.info("当前筛选条件下没有可诊断数据，请调整日期、类目或商品范围。")
    else:
        st.error(f"当前数据暂时无法诊断：{exc}")
    st.stop()

findings = tuple(run_diagnosis(context))
category_scope = "、".join(selected_categories) if selected_categories else "全部类目"
product_scope = (
    "、".join(product_labels[product_id] for product_id in selected_products)
    if selected_products
    else "全部商品"
)

st.info("当前模式：确定性诊断模式｜所有结论均由固定指标公式和规则生成")
st.caption(
    f"数据来源：{context.source_name} ｜ 分析周期：{start_date.isoformat()} 至 "
    f"{end_date.isoformat()}"
)
st.caption(f"当前筛选：{category_scope} ｜ {product_scope}")

st.subheader("诊断概览")
affected_products = {
    finding.scope.scope_id
    for finding in findings
    if finding.scope.scope_type == "product" and finding.scope.scope_id
}
overview_columns = st.columns(3)
overview_columns[0].metric("发现问题", len(findings), border=True)
overview_columns[1].metric(
    "高优先级",
    sum(finding.priority == "high" for finding in findings),
    border=True,
)
overview_columns[2].metric("影响商品", len(affected_products), border=True)

if not findings:
    st.success("当前筛选范围未触发诊断规则，暂无需要展示的诊断结果。")
    render_ai_report_section(
        source_name=context.source_name,
        start_date=start_date,
        end_date=end_date,
        categories=selected_categories,
        product_ids=selected_products,
        category_scope=category_scope,
        product_scope=product_scope,
        context=context,
        findings=findings,
    )
    st.stop()

st.subheader("诊断结果")
st.caption("按优先级评分从高到低展示；可能原因与行动建议来自人工维护的业务目录。")
for diagnosis_finding in findings:
    render_finding(diagnosis_finding)

render_ai_report_section(
    source_name=context.source_name,
    start_date=start_date,
    end_date=end_date,
    categories=selected_categories,
    product_ids=selected_products,
    category_scope=category_scope,
    product_scope=product_scope,
    context=context,
    findings=findings,
)

st.caption(
    "AI 报告只使用当前范围内的汇总指标、诊断结果和候选目录；"
    "页面不直接读取密钥、拼接 Prompt 或调用模型 SDK，也不会修改原始数据。"
)
