"""TrendPilot data entry and validation homepage."""

import pandas as pd
import streamlit as st

from src.data_loader import DataLoadError, load_csv, load_sample_data, summarize_dataset
from src.data_validator import REQUIRED_COLUMNS, validate_required_columns


DATA_SESSION_KEY = "sales_data"
SOURCE_SESSION_KEY = "sales_data_source"
PREVIEW_COLUMN_LABELS = {
    "date": "日期",
    "product_id": "商品ID",
    "product_name": "商品名称",
    "category": "商品类别",
    "price": "售价",
    "cost": "成本",
    "impressions": "曝光次数",
    "visitors": "访客数",
    "product_clicks": "商品点击",
    "add_to_cart": "加购次数",
    "orders": "订单数",
    "units_sold": "销量",
    "sales_amount": "销售额",
    "ad_spend": "广告花费",
    "refund_units": "退款数量",
    "inventory": "库存数量",
    "rating": "商品评分",
}


def store_valid_data(dataframe: pd.DataFrame, source_name: str) -> bool:
    """Validate and store an accepted dataset in the current Streamlit session."""
    validation = validate_required_columns(dataframe)
    if not validation.is_valid:
        st.error(validation.error_message)
        return False

    st.session_state[DATA_SESSION_KEY] = dataframe
    st.session_state[SOURCE_SESSION_KEY] = source_name
    return True


def render_dataset(dataframe: pd.DataFrame) -> None:
    """Render a compact summary and preview for the active dataset."""
    summary = summarize_dataset(dataframe)
    row_count, product_count, start_date, end_date = st.columns(4)
    row_count.metric("数据行数", f"{summary['row_count']:,}")
    product_count.metric("商品数", summary["product_count"])
    start_date.metric("开始日期", summary["start_date"])
    end_date.metric("结束日期", summary["end_date"])

    st.subheader("数据预览")
    preview = dataframe.head(20).rename(columns=PREVIEW_COLUMN_LABELS)
    st.dataframe(preview, width="stretch", hide_index=True)
    st.caption("当前展示前 20 行；完整数据已保存在本次浏览器会话中。")


st.set_page_config(page_title="TrendPilot", page_icon="📈", layout="wide")

st.title("TrendPilot")
st.subheader("面向潮流服饰品牌的 AI 电商运营决策助手")
st.write(
    "加载经营数据后，可查看销售、转化、毛利和库存等经营指标，"
    "并进一步进入规则诊断和 AI 增强分析。"
    "数据事实由确定性系统提供，AI 负责解释和行动建议，"
    "最终决策仍由运营人员完成。"
)

st.markdown("### 使用流程")
st.markdown("**加载数据 → 经营总览 → 规则诊断 → AI 增强分析**")

sample_column, upload_column = st.columns(2)

with sample_column:
    st.markdown("#### 使用示例数据")
    st.write("加载项目内置的 90 天、10 个潮流服饰商品模拟经营数据。")
    if st.button("加载示例数据", type="primary", width="stretch"):
        try:
            sample_data = load_sample_data()
            if store_valid_data(sample_data, "项目示例数据"):
                st.success("示例数据已加载并通过字段校验。")
        except DataLoadError as exc:
            st.error(str(exc))

with upload_column:
    st.markdown("#### 上传自己的 CSV")
    uploaded_file = st.file_uploader("选择 CSV 文件", type=["csv"])
    if uploaded_file is not None and st.button("校验并使用上传数据", width="stretch"):
        try:
            uploaded_data = load_csv(uploaded_file)
            if store_valid_data(uploaded_data, uploaded_file.name):
                st.success("上传数据已通过字段校验。")
        except DataLoadError as exc:
            st.error(str(exc))

with st.expander("数据上传说明"):
    st.write("上传经营数据前，请确认文件包含以下基础信息和经营指标：")
    basic_column, metric_column = st.columns(2)
    with basic_column:
        st.markdown("**基础信息**\n- 日期\n- 商品\n- 类目")
    with metric_column:
        st.markdown("**经营指标**\n- 销售额\n- 订单量\n- 访客数\n- 库存")
    st.caption("完整 CSV 字段名称")
    st.code("\n".join(REQUIRED_COLUMNS), language="text")

if DATA_SESSION_KEY in st.session_state:
    st.divider()
    source = st.session_state.get(SOURCE_SESSION_KEY, "未知来源")
    st.caption(f"当前数据来源：{source}")
    render_dataset(st.session_state[DATA_SESSION_KEY])
    st.page_link("pages/1_经营总览.py", label="进入经营总览", icon="📊")
else:
    st.info("请加载示例数据，或上传符合“数据上传说明”的 CSV 文件。")
