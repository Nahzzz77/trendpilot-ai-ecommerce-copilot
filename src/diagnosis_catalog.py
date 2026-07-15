"""Curated cause and action candidates for deterministic diagnosis findings."""

from dataclasses import dataclass


RULE_IDS = (
    "R001_SALES_DECLINE",
    "R002_VISITOR_DECLINE",
    "R003_CONVERSION_DECLINE",
    "R004_ROAS_DECLINE",
    "R005_AD_SPEND_UP_WITHOUT_SALES_GROWTH",
    "R006_GROSS_MARGIN_DECLINE",
    "R007_REFUND_RATE_INCREASE",
    "R008_INVENTORY_DAYS_LOW",
    "R009_INVENTORY_DAYS_HIGH",
    "R010_KEY_PRODUCT_SALES_DECLINE",
)


@dataclass(frozen=True, slots=True)
class CauseCatalogEntry:
    cause_id: str
    cause_name: str
    description: str
    applicable_rules: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ActionCatalogEntry:
    action_id: str
    action_name: str
    owner: str
    suggested_period: str
    observe_metric: str


CAUSE_CATALOG = (
    CauseCatalogEntry(
        "C001_TRAFFIC_DECLINE",
        "流量规模下降",
        "进入商品或店铺的有效访客规模减少。",
        ("R001_SALES_DECLINE",),
    ),
    CauseCatalogEntry(
        "C002_CONVERSION_DECLINE",
        "转化效率下降",
        "现有流量转化为订单的效率下降。",
        ("R001_SALES_DECLINE",),
    ),
    CauseCatalogEntry(
        "C003_CHANNEL_TRAFFIC_WEAKNESS",
        "渠道引流走弱",
        "主要流量渠道的覆盖或引流效率可能下降。",
        ("R002_VISITOR_DECLINE", "R010_KEY_PRODUCT_SALES_DECLINE"),
    ),
    CauseCatalogEntry(
        "C004_PRODUCT_PAGE_FRICTION",
        "商品承接效率不足",
        "商品信息、价格或权益可能影响访问后的购买决策。",
        ("R003_CONVERSION_DECLINE", "R010_KEY_PRODUCT_SALES_DECLINE"),
    ),
    CauseCatalogEntry(
        "C005_AD_TRAFFIC_EFFICIENCY",
        "广告流量效率下降",
        "广告流量质量或投放组合可能未匹配销售产出。",
        ("R004_ROAS_DECLINE", "R005_AD_SPEND_UP_WITHOUT_SALES_GROWTH"),
    ),
    CauseCatalogEntry(
        "C006_COST_OR_DISCOUNT_PRESSURE",
        "成本或折扣压力",
        "成本、折扣或商品结构变化可能压缩毛利空间。",
        ("R006_GROSS_MARGIN_DECLINE",),
    ),
    CauseCatalogEntry(
        "C007_PRODUCT_EXPECTATION_GAP",
        "商品预期差异",
        "商品质量、描述或履约体验可能与消费者预期存在差异。",
        ("R007_REFUND_RATE_INCREASE",),
    ),
    CauseCatalogEntry(
        "C008_SALES_VELOCITY_OUTPACING_STOCK",
        "销售速度超过库存准备",
        "近期销售速度可能快于当前库存覆盖能力。",
        ("R008_INVENTORY_DAYS_LOW",),
    ),
    CauseCatalogEntry(
        "C009_REPLENISHMENT_LAG",
        "补货节奏滞后",
        "补货到货节奏可能未跟上当前销售消耗。",
        ("R008_INVENTORY_DAYS_LOW",),
    ),
    CauseCatalogEntry(
        "C010_DEMAND_BELOW_STOCK_PLAN",
        "需求低于库存计划",
        "实际销售速度可能低于备货时的需求预期。",
        ("R009_INVENTORY_DAYS_HIGH",),
    ),
    CauseCatalogEntry(
        "C011_PRODUCT_DEMAND_WEAKNESS",
        "重点商品需求走弱",
        "重点商品的需求或市场吸引力可能下降。",
        ("R001_SALES_DECLINE", "R010_KEY_PRODUCT_SALES_DECLINE"),
    ),
)


ACTION_CATALOG = (
    ActionCatalogEntry(
        "A001_REVIEW_SALES_FUNNEL", "复盘销售漏斗", "运营", "3天内", "sales_amount"
    ),
    ActionCatalogEntry(
        "A002_RECOVER_QUALITY_TRAFFIC", "恢复有效流量", "运营", "3天内", "visitors"
    ),
    ActionCatalogEntry(
        "A003_AUDIT_CONVERSION_FUNNEL",
        "检查转化漏斗",
        "运营",
        "3天内",
        "payment_conversion_rate",
    ),
    ActionCatalogEntry(
        "A004_REVIEW_CAMPAIGN_EFFICIENCY", "复盘投放效率", "投放", "今天", "roas"
    ),
    ActionCatalogEntry(
        "A005_REALLOCATE_AD_BUDGET", "调整广告预算分配", "投放", "3天内", "roas"
    ),
    ActionCatalogEntry(
        "A006_REVIEW_MARGIN_DRIVERS", "复盘毛利变化来源", "商品", "3天内", "gross_margin"
    ),
    ActionCatalogEntry(
        "A007_REVIEW_REFUND_REASONS", "复盘退款原因", "运营", "7天内", "refund_rate"
    ),
    ActionCatalogEntry(
        "A008_CHECK_PRODUCT_EXPECTATION", "核查商品体验与描述", "商品", "7天内", "refund_rate"
    ),
    ActionCatalogEntry(
        "A009_PLAN_REPLENISHMENT",
        "制定补货计划",
        "供应链",
        "3天内",
        "estimated_days_left",
    ),
    ActionCatalogEntry(
        "A010_PRIORITIZE_STOCK_ALLOCATION",
        "优先调配现有库存",
        "供应链",
        "今天",
        "estimated_days_left",
    ),
    ActionCatalogEntry(
        "A011_CONTROL_REPLENISHMENT",
        "控制后续补货",
        "供应链",
        "7天内",
        "estimated_days_left",
    ),
    ActionCatalogEntry(
        "A012_PLAN_INVENTORY_CLEARANCE",
        "制定库存消化计划",
        "运营",
        "7天内",
        "estimated_days_left",
    ),
    ActionCatalogEntry(
        "A013_REVIEW_KEY_PRODUCT",
        "复盘重点商品表现",
        "商品",
        "3天内",
        "product_sales_amount",
    ),
    ActionCatalogEntry(
        "A014_OPTIMIZE_PRODUCT_OFFER",
        "优化重点商品权益",
        "商品",
        "7天内",
        "product_sales_amount",
    ),
)


RULE_ACTION_MAP = {
    "R001_SALES_DECLINE": (
        "A001_REVIEW_SALES_FUNNEL",
        "A002_RECOVER_QUALITY_TRAFFIC",
        "A003_AUDIT_CONVERSION_FUNNEL",
    ),
    "R002_VISITOR_DECLINE": ("A002_RECOVER_QUALITY_TRAFFIC",),
    "R003_CONVERSION_DECLINE": ("A003_AUDIT_CONVERSION_FUNNEL",),
    "R004_ROAS_DECLINE": (
        "A004_REVIEW_CAMPAIGN_EFFICIENCY",
        "A005_REALLOCATE_AD_BUDGET",
    ),
    "R005_AD_SPEND_UP_WITHOUT_SALES_GROWTH": (
        "A004_REVIEW_CAMPAIGN_EFFICIENCY",
        "A005_REALLOCATE_AD_BUDGET",
    ),
    "R006_GROSS_MARGIN_DECLINE": ("A006_REVIEW_MARGIN_DRIVERS",),
    "R007_REFUND_RATE_INCREASE": (
        "A007_REVIEW_REFUND_REASONS",
        "A008_CHECK_PRODUCT_EXPECTATION",
    ),
    "R008_INVENTORY_DAYS_LOW": (
        "A009_PLAN_REPLENISHMENT",
        "A010_PRIORITIZE_STOCK_ALLOCATION",
    ),
    "R009_INVENTORY_DAYS_HIGH": (
        "A011_CONTROL_REPLENISHMENT",
        "A012_PLAN_INVENTORY_CLEARANCE",
    ),
    "R010_KEY_PRODUCT_SALES_DECLINE": (
        "A013_REVIEW_KEY_PRODUCT",
        "A014_OPTIMIZE_PRODUCT_OFFER",
    ),
}


def get_cause_candidate_ids(rule_id: str) -> tuple[str, ...]:
    return tuple(
        cause.cause_id for cause in CAUSE_CATALOG if rule_id in cause.applicable_rules
    )


def get_action_candidate_ids(rule_id: str) -> tuple[str, ...]:
    return RULE_ACTION_MAP.get(rule_id, ())
