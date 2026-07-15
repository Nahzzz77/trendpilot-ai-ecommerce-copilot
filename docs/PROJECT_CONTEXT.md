# TrendPilot 项目上下文

> 用途：在切换会话、更换电脑或中断开发后，快速恢复 TrendPilot 的真实项目状态、产品边界与下一步工作。本文记录的是当前仓库状态，不代表所有内容均已提交到 Git。

## 1. 项目基本信息

### 项目名称

TrendPilot（GitHub 仓库：`trendpilot-ai-ecommerce-copilot`）。

### 项目目标

开发一个可上传到 GitHub、用于 AI 产品经理面试展示的 MVP，完整呈现从业务问题定义、数据产品设计、确定性分析到 AI 辅助决策的产品闭环。

### 产品定位

面向潮流服饰品牌的 AI 电商运营决策助手。TrendPilot 不替代运营人员执行决策，而是将经营数据转化为可读指标、可验证问题和后续可执行建议。

### 目标用户

- 中小型潮流服饰品牌的电商运营人员。
- 商品、投放和供应链协同人员。
- 需要快速理解销售、流量、转化、毛利和库存情况的业务负责人。

### 解决的业务问题

- 经营数据分散，运营人员需要手工计算指标。
- 指标口径不统一，容易出现错误比较或错误归因。
- Dashboard 可以展示结果，但不能主动指出值得关注的问题。
- 运营人员难以从多个指标中判断处理优先级。
- 纯 LLM 分析容易产生错误数字或缺少可验证证据。
- 需要通过“规则证据 + AI 解读”的混合架构提高诊断可信度。

## 2. 当前项目阶段

### 当前版本与 Git 状态

- 当前分支：`main`，跟踪 `origin/main`。
- 最新已提交并推送的 commit：`a21cc513e6d0a225bb704ec70aea782984bda889`。
- 最新 commit 内容：`docs: add phase 2 product screenshots and README updates`。
- Phase 1 标签：`v0.1-foundation`，指向 `33befd873438cd65880d66d533620bf2553961fd`。
- Phase 2 标签：`v0.2-dashboard`，指向 `f97e78f193dc7208b9173c7a01292e335d48ecf5`。
- 当前没有 Phase 3 commit 或 tag。
- Phase 3 第 2–4 阶段文件目前是本地未提交、未跟踪文件。
- 本文档同样属于本地新增文件，按当前要求暂不提交。

### 已完成阶段

#### Phase 1：项目基础与数据入口

已完成：

- 项目基础目录结构。
- Streamlit 首页。
- 内置示例 CSV 加载。
- 用户上传 CSV。
- 17 个必填字段校验。
- 合法数据写入 `st.session_state`。
- 数据行数、商品数、日期范围和数据预览。
- 90 天、10 个商品、900 行模拟经营数据。
- README、AGENTS、requirements 和基础 pytest。

稳定保存点：`v0.1-foundation`。

#### Phase 2：确定性指标与经营 Dashboard

已完成：

- 分析数据类型转换和业务合法性校验。
- 日期、类目和商品筛选。
- 销售、流量、转化、退款、广告、毛利和库存指标。
- 当前周期与上一等长周期对比。
- 每日趋势、商品汇总、类目汇总和库存快照。
- Streamlit 经营总览 Dashboard。
- Plotly 趋势、漏斗、排名和类目占比图表。
- 中文示例数据与非零差异化库存。
- Phase 2 产品截图和 README 展示。

稳定保存点：`v0.2-dashboard`。截图文档提交位于其后的 `a21cc51`。

#### Phase 3：AI 经营诊断助手

当前已完成但尚未提交：

- 第 1 阶段：建立 Phase 1/2 回归基线。
- 第 2 阶段：`DiagnosisContext` 数据结构与构建逻辑。
- 第 3 阶段：确定性规则引擎、Evidence、DiagnosticFinding 和优先级评分。
- 第 4 阶段：唯一 Rule ID、原因候选目录、行动候选目录及 Finding 候选引用。

当前正在进行的阶段：

> Phase 3 第 4 阶段已验收，下一步等待开始 Phase 3 第 5 阶段“确定性诊断页面”。

尚未开始：

- Streamlit AI 经营诊断页面。
- AI Provider。
- Prompt。
- LLM 调用。
- AI Report Validator。
- AI 报告展示。

## 3. 产品架构

当前及规划中的完整链路：

```text
数据输入
↓
数据处理
↓
指标计算
↓
经营 Dashboard
↓
DiagnosisContext
↓
确定性规则引擎
↓
AI 能力层（未来）
```

### 数据输入

首页负责加载项目示例 CSV 或用户上传 CSV，执行必填字段校验，并将合法原始 DataFrame 保存到当前 Streamlit Session State。

### 数据处理

数据处理层复制原始 DataFrame，转换日期和数值类型，校验标识字段、非负数值和评分范围，并应用日期、类目和商品筛选。它不得修改 Session State 中的原始数据。

### 指标计算

指标层通过 Pandas 计算确定性经营指标。所有比率先汇总分子和分母，再执行除法。指标层是所有业务数字的唯一可信来源。

### 经营 Dashboard

Dashboard 负责筛选交互、指标格式化、图表和表格展示，不负责重新定义或计算业务口径。当前页面是 `pages/1_经营总览.py`。

### DiagnosisContext

DiagnosisContext 调用 Phase 2 的公开数据处理和指标函数，将当前周期、上一周期、商品、类目、趋势和库存结果组装为规则引擎输入。它不携带原始 CSV 明细。

### 确定性规则引擎

规则引擎根据集中配置的阈值发现销售、流量、转化、广告、毛利、退款、库存和重点商品问题，生成带证据、范围、优先级、原因候选和行动候选的 `DiagnosticFinding`。

### AI 能力层（未来）

未来 AI 层只读取结构化 Finding 和候选目录，负责解释问题、组织可能原因和生成行动报告。AI 不重新计算 KPI，也不直接读取原始 CSV。无 API Key 时必须保留完整的确定性诊断能力。

## 4. 当前代码结构

```text
app.py
pages/
  1_经营总览.py
src/
  data_loader.py
  data_validator.py
  data_processor.py
  metrics.py
  charts.py
  diagnosis_models.py
  diagnosis_context.py
  diagnosis_scoring.py
  diagnosis_rules.py
  diagnosis_engine.py
  diagnosis_catalog.py
tests/
  test_data_loader.py
  test_data_validator.py
  test_data_processor.py
  test_metrics.py
  test_charts.py
  test_dashboard.py
  test_diagnosis_context.py
  test_diagnosis_rules.py
  test_diagnosis_engine.py
  test_diagnosis_catalog.py
docs/
  PROJECT_CONTEXT.md
  screenshots/
data/
  sample_sales_data.csv
scripts/
  generate_sample_data.py
```

### 重要文件职责

#### `app.py`

Streamlit 首页。负责示例数据加载、CSV 上传、必填字段校验、Session State 保存和数据摘要预览。

#### `pages/1_经营总览.py`

Phase 2 经营 Dashboard。负责日期、类目、商品筛选以及 KPI、趋势、结构和库存展示。

#### `src/data_loader.py`

读取 CSV、处理读取错误，并生成首页数据摘要。

#### `src/data_validator.py`

维护 17 个必填字段并检查字段是否完整。

#### `src/data_processor.py`

将原始数据转换为可分析副本，执行数据合法性检查和闭区间筛选。不得修改输入 DataFrame。

#### `src/metrics.py`

Phase 2 确定性指标核心。负责 KPI、每日趋势、商品汇总、类目汇总、库存快照、周期对比和最新日对比。

#### `src/charts.py`

使用 Plotly 将指标层输出转化为图表，不重新计算 KPI。

#### `src/diagnosis_models.py`

定义 `DiagnosisContext`、`Evidence`、`FindingScope` 和 `DiagnosticFinding` 等诊断数据结构。

#### `src/diagnosis_context.py`

复用 Phase 2 数据处理和指标函数，构建规则引擎需要的当前期、上期、商品、类目、趋势和库存上下文。

#### `src/diagnosis_scoring.py`

根据影响程度、变化幅度和数据完整度计算 0–100 分，并输出 `high`、`medium` 或 `low`。

#### `src/diagnosis_rules.py`

维护集中阈值和 10 个唯一 Rule ID 对应的独立规则函数，生成确定性 Finding。

#### `src/diagnosis_engine.py`

统一执行所有规则，并按优先级分数稳定排序 Finding。

#### `src/diagnosis_catalog.py`

维护原因候选、行动候选、Rule ID 和规则到行动的映射。当前包含 11 个 Cause 和 14 个 Action。

#### `tests/`

覆盖 Phase 1 数据入口、Phase 2 指标与 Dashboard、Phase 3 Context、规则、评分及候选目录。

#### `docs/screenshots/`

保存 Phase 2 首页、Dashboard、KPI、趋势、商品排名和库存分析截图。

## 5. 已完成能力清单

### Phase 1

已实现功能：

- CSV 示例数据加载和文件上传。
- 必填字段校验。
- Session State 数据保存。
- 数据摘要和预览。
- 可复现模拟数据生成脚本。

测试情况：

- 数据加载、必填字段和示例数据质量均有 pytest 覆盖。
- 已纳入当前 62 项全量测试。

当前限制：

- 数据只保存在当前浏览器会话。
- 没有数据库或跨会话持久化。

### Phase 2

已实现功能：

- 完整确定性指标计算。
- 最近 30 天默认周期。
- 日期、类目和商品联动筛选。
- 当前期和上一等长周期对比。
- 销售、订单、销量、访客、转化、客单价、广告、ROAS、退款和毛利指标。
- 趋势、漏斗、商品排名、类目占比、毛利和库存展示。

测试情况：

- 数据处理、指标、图表和 Streamlit AppTest 已覆盖。
- Phase 2 完成时共有 35 项测试通过。
- 当前加入 Phase 3 测试后，全量 62 项仍全部通过。

当前限制：

- Dashboard 只做描述性分析，不主动生成经营结论。
- 库存依赖上传数据中每个商品最后一条库存记录。
- 没有异常历史、任务跟踪或自动执行。

### Phase 3

已实现功能：

- DiagnosisContext 及上下文构建。
- 当前和上期 KPI、商品、类目、趋势及库存输入。
- 10 个唯一 Rule ID。
- 销售额下降、访客下降、转化率下降、ROAS 下降、广告投入增加但销售未增长、毛利率下降、退款率上升、低库存、高库存和重点商品销售下降规则。
- 影响程度、变化幅度和数据完整度优先级评分。
- Evidence、FindingScope 和 DiagnosticFinding。
- Cause Catalog 和 Action Catalog。
- Finding 到原因候选及行动候选的有效引用。

测试情况：

- Phase 3 当前新增 27 项测试。
- 当前全量结果：`62 passed in 3.01s`。
- 示例数据默认 30 天可稳定产生 4 条规则诊断。

当前限制：

- 所有 Phase 3 文件尚未提交。
- 还没有诊断页面。
- 还没有 AI Provider、Prompt、LLM 或 AI Report Validator。
- 原因和行动目前仅为确定性候选目录，没有 AI 解释。

## 6. 当前设计原则

- AI 不负责计算业务指标，所有数字由 Pandas 确定性计算。
- LLM 不直接读取原始 CSV，也不接收逐行经营明细。
- 规则层负责发现问题、生成证据和确定优先级。
- AI 层负责解释问题、归纳可能原因和生成建议。
- AI 解释必须建立在 Finding 和候选目录之上。
- 无 API Key 或 AI 调用失败时，规则诊断仍然可用。
- 保持 Phase 1 数据入口和 Phase 2 Dashboard 稳定。
- 页面层只负责交互、格式化和展示，不包含业务计算逻辑。
- 阈值集中配置，不散落在规则函数或页面中。
- 每条 Finding 必须可追踪到唯一 Rule ID 和 Evidence。
- 优先保证完整面试 Demo，再考虑生产级架构优化。

## 7. 当前禁止事项

后续开发不要：

- 重构 Phase 2 Dashboard。
- 修改已有 Phase 2 指标公式。
- 在页面中重新计算 KPI 或复制业务口径。
- 直接让 LLM 分析原始 CSV。
- 让 LLM 发明新的指标、Finding、Cause ID 或 Action ID。
- 引入复杂 Agent 或多 Agent 编排。
- 引入数据库或历史报告持久化。
- 开发自由聊天机器人。
- 开发自动执行任务、投放调整或库存操作。
- 引入复杂权限、长期记忆或定时任务。
- 扩展超出当前 Phase 3 MVP 的功能。
- 在诊断页面验收前进入 AI Provider、Prompt 或 LLM 开发。

## 8. 下一步开发计划

### Phase 3 第 5 阶段：确定性诊断页面

目标链路：

```text
首页上传数据
→ 经营 Dashboard
→ AI 经营诊断页面
→ 查看规则诊断
```

本阶段应实现：

- 新增 `pages/2_AI经营诊断.py`。
- 无 Session State 数据时引导返回首页。
- 复用当前数据和默认最近 30 天周期。
- 支持日期、类目和商品筛选。
- 调用 `build_diagnosis_context`。
- 调用 `run_diagnosis`。
- 展示诊断数量和优先级概览。
- 展示重点 Finding、Evidence、Cause 候选和 Action 候选。
- 展示无诊断结果、筛选为空和数据错误状态。
- 使用 Streamlit AppTest 覆盖无数据、默认数据、筛选和规则展示。

本阶段不要进入：

- AI Provider。
- LLM 调用。
- Prompt。
- AI Report Validator。
- AI 分析报告。

只有确定性诊断页面完成并验收后，才进入 AI 能力阶段。

## 9. 技术约束

### Python 与依赖

- 要求 Python 3.11+。
- 当前虚拟环境：Python 3.11.9。
- Streamlit：`>=1.35,<2.0`。
- Pandas：`>=2.2,<3.0`。
- Plotly：`>=5.22,<7.0`。
- pytest：`>=8.0,<9.0`。
- 当前尚未添加 AI SDK。

### 测试状态

- 当前测试数量：62。
- 最近一次完整测试：`62 passed in 3.01s`。
- 测试命令：

```powershell
.\.venv\Scripts\python.exe -m pytest
```

### Git 状态

- 当前分支：`main`。
- `main` 跟踪 `origin/main`。
- 最新已推送 commit：`a21cc51`。
- 工作区不是干净状态：Phase 3 文件和本上下文文档尚未提交。
- 切换电脑前必须先决定是否将 Phase 3 当前阶段封存到 Git，否则未跟踪文件不会出现在远程仓库。

### 运行方式

安装依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

启动应用：

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

默认访问地址：

```text
http://localhost:8501
```

检查 Git 状态：

```powershell
git status --short --branch
```

## 10. 面试展示方向

TrendPilot 最终用于 AI 产品经理面试展示。项目价值不只是“调用大模型”，而是呈现完整的 AI 产品设计方法。

### 产品背景

说明潮流服饰品牌拥有流量、销售、广告和库存数据，但日常经营仍依赖人工汇总和经验判断。

### 用户痛点

突出指标计算耗时、口径不统一、问题优先级不清晰，以及纯 Dashboard 缺少行动导向。

### 数据分析能力

展示 CSV 校验、确定性指标、周期对比、商品与类目分析、趋势和库存可售天数。

### AI 设计思路

强调 AI 不是替代指标计算，而是在可靠数据和规则证据之上完成解释与建议。

### 混合架构

核心表达：

```text
Pandas 确定性指标
+ 规则引擎发现问题
+ LLM 解释与建议
= 可验证的 AI 经营诊断
```

### AI 价值

- 降低运营人员理解多个指标的成本。
- 将 Dashboard 从“展示数据”升级为“指出问题”。
- 将规则结果转化为业务语言和行动顺序。
- 在保持可解释性的前提下提升决策效率。

面试演示应优先完成清晰闭环，而不是展示复杂 Agent、数据库或生产级基础设施。
