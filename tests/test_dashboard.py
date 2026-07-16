from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.data_loader import load_sample_data


DASHBOARD_PATH = Path(__file__).resolve().parents[1] / "pages" / "1_经营总览.py"
HOME_PATH = Path(__file__).resolve().parents[1] / "app.py"


def test_homepage_loads_sample_data_and_keeps_phase_one_summary():
    app = AppTest.from_file(str(HOME_PATH)).run(timeout=20)

    app.button[0].click().run(timeout=20)

    assert not app.exception
    assert "sales_data" in app.session_state
    labels = [metric.label for metric in app.metric]
    assert labels == ["数据行数", "商品数", "开始日期", "结束日期"]


def test_homepage_preview_uses_chinese_labels_without_mutating_source_data():
    app = AppTest.from_file(str(HOME_PATH)).run(timeout=20)

    app.button[0].click().run(timeout=20)

    assert not app.exception
    preview_columns = list(app.dataframe[0].value.columns)
    expected_labels = [
        "日期",
        "商品ID",
        "商品名称",
        "商品类别",
        "售价",
        "成本",
        "曝光次数",
        "访客数",
        "商品点击",
        "加购次数",
        "订单数",
        "销量",
        "销售额",
        "广告花费",
        "退款数量",
        "库存数量",
        "商品评分",
    ]
    assert preview_columns[: len(expected_labels)] == expected_labels

    source_columns = list(app.session_state["sales_data"].columns)
    assert source_columns[: len(expected_labels)] == [
        "date",
        "product_id",
        "product_name",
        "category",
        "price",
        "cost",
        "impressions",
        "visitors",
        "product_clicks",
        "add_to_cart",
        "orders",
        "units_sold",
        "sales_amount",
        "ad_spend",
        "refund_units",
        "inventory",
        "rating",
    ]


def test_homepage_uses_operator_friendly_upload_guidance():
    app = AppTest.from_file(str(HOME_PATH)).run(timeout=20)

    assert not app.exception
    assert any(expander.label == "数据上传说明" for expander in app.expander)

    copy = "\n".join(element.value for element in app.markdown)
    assert "上传经营数据前，请确认文件包含以下基础信息和经营指标" in copy
    assert "基础信息" in copy
    assert "日期" in copy
    assert "商品" in copy
    assert "类目" in copy
    assert "经营指标" in copy
    assert "销售额" in copy
    assert "订单量" in copy
    assert "访客数" in copy
    assert "库存" in copy
    assert "数据事实由确定性系统提供" in copy
    assert "AI 负责解释和行动建议" in copy


def test_dashboard_guides_user_to_load_data_when_session_is_empty():
    app = AppTest.from_file(str(DASHBOARD_PATH)).run(timeout=20)

    assert not app.exception
    messages = [element.value for element in app.warning]
    assert any("返回首页" in message and "加载数据" in message for message in messages)


def test_dashboard_renders_core_kpis_for_sample_data():
    app = AppTest.from_file(str(DASHBOARD_PATH))
    app.session_state["sales_data"] = load_sample_data()
    app.session_state["sales_data_source"] = "项目示例数据"

    app.run(timeout=30)

    assert not app.exception
    metric_labels = [metric.label for metric in app.metric]
    for label in ["销售额", "订单量", "访客数", "支付转化率", "客单价", "ROAS"]:
        assert label in metric_labels
    captions = [caption.value for caption in app.caption]
    assert any("2026-05-31 至 2026-06-29" in caption for caption in captions)
    assert any(button.label == "进入 AI 经营诊断" for button in app.button)


def test_category_filter_recalculates_dashboard_kpis():
    app = AppTest.from_file(str(DASHBOARD_PATH))
    app.session_state["sales_data"] = load_sample_data()
    app.run(timeout=30)
    full_sales = next(metric.value for metric in app.metric if metric.label == "销售额")

    first_category = app.multiselect[0].options[0]
    app.multiselect[0].set_value([first_category]).run(timeout=30)
    filtered_sales = next(metric.value for metric in app.metric if metric.label == "销售额")

    assert not app.exception
    assert filtered_sales != full_sales
