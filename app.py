"""TrendPilot data entry and validation homepage."""

import pandas as pd
import streamlit as st

from src.data_loader import DataLoadError, load_csv, load_sample_data, summarize_dataset
from src.data_validator import REQUIRED_COLUMNS, validate_required_columns


DATA_SESSION_KEY = "sales_data"
SOURCE_SESSION_KEY = "sales_data_source"


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
    st.dataframe(dataframe.head(20), width="stretch", hide_index=True)
    st.caption("当前展示前 20 行；完整数据已保存在本次浏览器会话中。")


st.set_page_config(page_title="TrendPilot", page_icon="📈", layout="wide")

st.title("TrendPilot")
st.subheader("面向潮流服饰品牌的 AI 电商运营决策助手")
st.write(
    "加载经营数据后，可进入经营总览查看销售、转化、毛利和库存等确定性指标。"
    "当前版本不包含异常检测、原因解释或自动建议。"
)

st.markdown("### 使用流程")
st.markdown("**加载数据 → 校验字段 → 保存会话 → 查看经营总览**")

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

with st.expander("查看 CSV 必填字段"):
    st.code("\n".join(REQUIRED_COLUMNS), language="text")

if DATA_SESSION_KEY in st.session_state:
    st.divider()
    source = st.session_state.get(SOURCE_SESSION_KEY, "未知来源")
    st.caption(f"当前数据来源：{source}")
    render_dataset(st.session_state[DATA_SESSION_KEY])
    st.page_link("pages/1_经营总览.py", label="进入经营总览", icon="📊")
else:
    st.info("请加载示例数据，或上传包含全部必填字段的 CSV 文件。")
