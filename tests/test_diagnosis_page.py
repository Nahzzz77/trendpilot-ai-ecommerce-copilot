from datetime import date
from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.data_loader import load_sample_data


DIAGNOSIS_PAGE = (
    Path(__file__).resolve().parents[1] / "pages" / "2_AI经营诊断.py"
)


def _loaded_diagnosis_app():
    app = AppTest.from_file(str(DIAGNOSIS_PAGE))
    app.session_state["sales_data"] = load_sample_data()
    app.session_state["sales_data_source"] = "项目示例数据"
    return app.run(timeout=30)


def test_diagnosis_page_guides_user_to_load_data_when_session_is_empty():
    app = AppTest.from_file(str(DIAGNOSIS_PAGE)).run(timeout=20)

    assert not app.exception
    messages = [element.value for element in app.warning]
    assert any("返回首页" in message and "加载数据" in message for message in messages)


def test_diagnosis_page_loads_overview_for_sample_data():
    app = _loaded_diagnosis_app()

    assert not app.exception
    assert any("确定性诊断模式" in element.value for element in app.info)
    labels = [metric.label for metric in app.metric]
    assert labels[:3] == ["发现问题", "高优先级", "影响商品"]
    captions = [caption.value for caption in app.caption]
    assert any("项目示例数据" in caption for caption in captions)
    assert any("2026-05-31 至 2026-06-29" in caption for caption in captions)


def test_diagnosis_page_renders_finding_as_product_content_not_json():
    app = _loaded_diagnosis_app()

    assert not app.exception
    content = "\n".join(element.value for element in app.markdown)
    assert "访客数下降" in content
    assert "【数据证据】" in content
    assert "【系统判断】" in content
    assert "【可能原因】" in content
    assert "【行动建议】" in content
    assert '"finding_id"' not in content


def test_diagnosis_page_category_filter_updates_scope():
    app = _loaded_diagnosis_app()
    selected_category = app.multiselect[0].options[0]

    app.multiselect[0].set_value([selected_category]).run(timeout=30)

    assert not app.exception
    captions = [caption.value for caption in app.caption]
    assert any(selected_category in caption and "当前筛选" in caption for caption in captions)
    assert app.multiselect[1].options


def test_diagnosis_page_handles_empty_date_filter():
    app = AppTest.from_file(str(DIAGNOSIS_PAGE))
    sample = load_sample_data()
    sample = sample.loc[sample["date"] != "2026-06-15"].copy()
    app.session_state["sales_data"] = sample
    app.run(timeout=30)

    app.date_input[0].set_value((date(2026, 6, 15), date(2026, 6, 15))).run(
        timeout=30
    )

    assert not app.exception
    messages = [element.value for element in app.info]
    assert any("没有可诊断数据" in message and "调整" in message for message in messages)
