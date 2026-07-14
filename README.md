# TrendPilot

> 面向潮流服饰品牌的 AI 电商运营决策助手

TrendPilot 是一个用于 AI 产品经理面试展示的本地 MVP。项目希望把电商经营数据转化为可解释的问题诊断和可执行的运营建议。当前仓库只完成阶段 1：建立可靠的数据上传与校验入口。

## 项目背景

中小型潮流服饰品牌通常拥有销售、流量和库存数据，但运营人员仍需依赖经验判断数据变化原因、商品风险和行动优先级。TrendPilot 的长期产品流程是：

```text
经营数据分析 → 异常发现 → 原因解释 → 行动建议 → 效果验证
```

## 阶段 1 功能

- 加载项目自带的模拟经营数据。
- 上传用户自己的 CSV 文件。
- 校验 17 个必填字段，并明确提示缺失字段。
- 将合法数据写入 Streamlit Session State。
- 展示数据行数、商品数、日期范围和前 20 行预览。

阶段 1 **不包含**指标分析、异常检测、大模型调用、单品诊断或运营方案生成。

## 项目结构

```text
.
├── app.py
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   └── data_validator.py
├── data/
│   └── sample_sales_data.csv
├── tests/
│   ├── test_data_loader.py
│   └── test_data_validator.py
├── docs/
├── assets/
├── AGENTS.md
├── requirements.txt
└── README.md
```

## 快速启动

需要 Python 3.11 或更高版本。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

打开终端显示的本地地址后，可点击“加载示例数据”，也可以上传自己的 CSV。

## CSV 必填字段

```text
date, product_id, product_name, category, price, cost, impressions,
visitors, product_clicks, add_to_cart, orders, units_sold, sales_amount,
ad_spend, refund_units, inventory, rating
```

字段名称区分拼写，但会自动清除字段名前后的空格。上传文件建议使用 UTF-8 编码。额外字段不会导致校验失败。

## 示例数据

`data/sample_sales_data.csv` 是固定生成的模拟数据，包含：

- 2026-04-01 至 2026-06-29，共 90 天；
- 10 个潮流服饰商品；
- 每个商品每天一行，共 900 行；
- 销售、流量、广告、退款、库存和评分字段。

这些数据仅用于产品功能演示，不代表真实商家、真实用户或商业效果。

## 测试

```powershell
python -m pytest
```

基础测试覆盖 CSV 读取、空文件处理、字段校验、数据摘要和示例数据规模。

## 当前限制

- 仅支持 CSV 文件和单次浏览器会话，不使用数据库。
- 只校验必填字段是否存在，尚未校验每列的数据类型和业务取值范围。
- 未接入电商平台、用户系统、支付系统或生产环境。
- 未接入任何大模型，也没有创建或保存真实 API Key。

## 后续阶段

后续将在每个阶段单独验收后，依次增加指标看板、可解释异常检测、AI 经营诊断、单品诊断、运营方案和完整评估文档。
