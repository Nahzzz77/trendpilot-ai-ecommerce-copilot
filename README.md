# TrendPilot

> 面向潮流服饰品牌的 AI 电商运营决策助手

TrendPilot 是一个面向潮流服饰品牌电商运营人员的 AI 经营决策助手，也是一个用于 AI 产品经理面试展示的本地 MVP。

当前版本已经形成一条可演示、可验证的经营分析流程：

```text
数据上传
→ Dashboard 指标计算
→ 确定性规则发现问题
→ 展示数据证据、系统判断、候选原因和候选行动
```

所有经营数字和问题判断都有明确来源。当前版本尚未接入真实大模型、AI Provider、Prompt 或 AI Report；下一阶段计划开发 AI 经营分析报告。

## 产品架构

TrendPilot 使用“确定性分析 + AI 增强”的产品思路，当前已完成确定性分析部分：

- **Pandas** 负责计算经营指标和周期对比，是业务数字的唯一来源。
- **Rule Engine** 根据集中配置的阈值发现经营问题，并生成带证据和优先级的诊断结果。
- **Cause Catalog** 和 **Action Catalog** 提供受控的候选原因与候选行动，避免系统随意生成结论。
- **当前版本尚未接入真实大模型**，诊断页面展示的是确定性系统结果。
- **下一阶段的 LLM** 将在结构化诊断结果之上负责经营总结、问题解释、原因假设和行动排序，不重新计算指标，也不直接读取原始 CSV。

## 已实现功能

### 数据入口

- 加载项目内置示例 CSV，或上传用户自己的 CSV。
- 校验 17 个必填字段。
- 校验日期、商品标识、非负数值和 0–5 分评分。
- 将合法数据保存在当前 Streamlit Session State，并展示数据摘要和预览。
- 内置固定随机种子生成的 90 天、10 个商品、900 行示例数据。

### 经营 Dashboard

- 默认分析最近 30 天。
- 支持日期、类目和商品联动筛选。
- 展示 KPI 和上一等长周期对比。
- 展示销售、流量、转化、广告、退款、毛利和库存分析。
- 展示每日趋势、流量转化漏斗、商品排名、类目占比和库存明细。
- 展示最新一天、前一天和此前 7 日均值对比。

### 确定性经营诊断

- 使用 `DiagnosisContext` 复用 Dashboard 的指标结果，不修改原始数据。
- 通过确定性规则识别销售、访客、转化率、ROAS、广告投入、毛利率、退款率、库存和重点商品问题。
- 每个问题包含 `DiagnosticFinding`、`Evidence`、影响范围和优先级。
- 根据影响程度、变化幅度和数据完整度生成高、中、低优先级。
- 使用 Cause Catalog 提供受控的候选原因。
- 使用 Action Catalog 提供负责人、建议周期和观察指标明确的候选行动。
- 诊断卡片明确区分“数据证据”“系统判断”“可能原因”和“行动建议”。
- 支持日期、类目和商品筛选，以及无数据、筛选为空和无诊断结果状态。

### 测试

- 当前共有 **67 个自动测试**。
- 覆盖数据加载、字段校验、指标计算、图表、Dashboard、DiagnosisContext、规则边界、优先级、目录引用和诊断页面。

## 当前项目阶段

| 阶段 | 状态 | 主要内容 |
|---|---|---|
| Phase 1：数据入口 | 已完成 | CSV 上传、示例数据、17 个字段校验和 Session State |
| Phase 2：经营 Dashboard | 已完成 | 确定性指标、周期对比、图表和库存分析 |
| Phase 3：确定性经营诊断 | 已完成 | DiagnosisContext、规则引擎、优先级、Cause/Action Catalog 和诊断页面 |
| Phase 3：AI Report | 尚未开发 | 下一阶段开发 AI Provider 和 AI 经营分析报告 |

## 产品截图

### 首页数据上传

![TrendPilot 首页数据上传](docs/screenshots/phase2-home-upload.png)

### 经营总览 Dashboard

![TrendPilot 经营总览 Dashboard](docs/screenshots/phase2-dashboard-overview.png)

### 核心 KPI 指标

![TrendPilot 核心 KPI 指标](docs/screenshots/phase2-kpi-metrics.png)

### 销售与订单趋势

![TrendPilot 销售与订单趋势](docs/screenshots/phase2-sales-trends.png)

### 商品销售额排名

![TrendPilot 商品销售额排名](docs/screenshots/phase2-product-ranking.png)

### 库存分析

![TrendPilot 库存分析](docs/screenshots/phase2-inventory-analysis.png)

## 指标口径

所有比率均先汇总分子与分母，再执行除法。

| 指标 | 公式 |
|---|---|
| 点击率 | `Σproduct_clicks / Σimpressions` |
| 加购率 | `Σadd_to_cart / Σproduct_clicks` |
| 支付转化率 | `Σorders / Σvisitors` |
| 退款率 | `Σrefund_units / Σunits_sold` |
| 客单价 | `Σsales_amount / Σorders` |
| ROAS | `Σsales_amount / Σad_spend` |
| 毛利额 | `Σsales_amount - Σ(cost × units_sold)` |
| 毛利率 | `毛利额 / Σsales_amount` |
| 日均销量 | `Σunits_sold / 周期自然日数` |
| 当前库存 | 每个商品在截止日前最后一条库存之和 |
| 库存可售天数 | `当前库存 / 周期日均销量` |

普通比率分母为零时返回 `0.0`；日均销量为零时库存可售天数为空。比率类周期变化使用百分点，其余指标使用相对变化率。

## 快速开始

需要 Python 3.11+。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

打开首页后点击“加载示例数据”，依次进入“经营总览”和“AI 经营诊断”。

## 运行测试

```powershell
python -m pytest
```

## 重新生成示例数据

```powershell
python scripts/generate_sample_data.py
```

脚本使用固定随机种子，并将 CSV 写为 UTF-8 with BOM。

## 项目结构

```text
app.py                         # 数据加载、校验和预览首页
pages/
  1_经营总览.py               # 经营 Dashboard
  2_AI经营诊断.py             # 确定性经营诊断页面
src/
  data_loader.py              # CSV 读取与摘要
  data_validator.py           # 17 个必填字段校验
  data_processor.py           # 分析数据准备与筛选
  metrics.py                  # 确定性经营指标
  charts.py                   # Plotly 图表构建
  diagnosis_models.py         # Context、Finding、Evidence 数据结构
  diagnosis_context.py        # 诊断上下文构建
  diagnosis_rules.py          # 确定性诊断规则
  diagnosis_scoring.py        # 问题优先级评分
  diagnosis_engine.py         # 规则执行与结果排序
  diagnosis_catalog.py        # Cause Catalog 与 Action Catalog
data/sample_sales_data.csv    # 示例经营数据
scripts/generate_sample_data.py
tests/                        # pytest 与 Streamlit AppTest
docs/PROJECT_CONTEXT.md       # 项目状态恢复文档
docs/screenshots/             # README 产品截图
requirements.txt
```

## 数据字段

CSV 必须包含以下 17 个字段：

```text
date, product_id, product_name, category, price, cost,
impressions, visitors, product_clicks, add_to_cart, orders,
units_sold, sales_amount, ad_spend, refund_units, inventory, rating
```

## 当前边界

- 当前版本没有真实 LLM、AI Provider、Prompt 或 AI Report。
- AI 不直接读取原始 CSV；未来只接收结构化诊断结果。
- 指标计算和问题判断来自 Pandas 与确定性规则系统。
- 当前展示的原因和行动来自受控候选目录，不是 AI 生成的最终结论。
- Session State 只保存当前浏览器会话中的数据，不提供长期数据保存。
- 当前库存依赖上传数据中每个商品在截止日前的最后一条库存记录。
- 当前项目是用于产品验证和面试演示的本地 MVP，不是生产级企业软件。

## 下一步

下一阶段将开发 AI 经营分析报告：在不改变现有指标和规则结果的前提下，让 LLM 基于结构化诊断内容生成经营总结、问题解释、原因假设和行动排序。该能力当前尚未实现。
