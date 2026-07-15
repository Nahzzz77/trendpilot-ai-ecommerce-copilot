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
