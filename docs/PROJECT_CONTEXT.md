# TrendPilot 项目上下文

> 用途：在切换会话、更换电脑或中断开发后，快速恢复 TrendPilot 的真实项目状态、产品边界与下一步工作。本文以当前已验收并推送的产品功能版本为基准。

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
- Phase 3 第6阶段 Step 1–5 checkpoint 提交信息：`feat: complete phase 3 ai report backend foundation`。
- 本次 Step 6A、Step 6B、Step 7 存档提交信息：`feat: complete phase 3 ai report mvp`。
- 本次存档包含 AI Report 页面集成、真实 Provider 页面接入、黄金场景自动检查与评估记录；准确提交和远程同步状态以 `git log -1 --oneline`、`git status --short --branch` 为准。
- 文档不记录自身提交 Hash，恢复项目时使用 `git log -1 --oneline` 获取最新提交。
- Phase 1 标签：`v0.1-foundation`，指向 `33befd873438cd65880d66d533620bf2553961fd`。
- Phase 2 标签：`v0.2-dashboard`，指向 `f97e78f193dc7208b9173c7a01292e335d48ecf5`。
- Phase 3 确定性诊断标签：`v0.3-rule-diagnosis`，指向 README 里程碑提交 `2e9139fd49124a93f893cc95fe3fe6c61a45e86a`。
- Phase 3 确定性诊断第 1–5 阶段均已提交并推送。
- Phase 3 第6阶段 Step 1–9 已完成，AI Report MVP 已通过真实 DeepSeek 验证并进入文档冻结状态。

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

确定性诊断部分已完成并提交：

- 第 1 阶段：建立 Phase 1/2 回归基线。
- 第 2 阶段：`DiagnosisContext` 数据结构与构建逻辑。
- 第 3 阶段：确定性规则引擎、Evidence、DiagnosticFinding 和优先级评分。
- 第 4 阶段：唯一 Rule ID、原因候选目录、行动候选目录及 Finding 候选引用。
- 第 5 阶段：确定性 AI 经营诊断页面、筛选、诊断卡片、异常状态和 Dashboard 入口。

Phase 3 第6阶段已完成：

- Step 1：AI Report Models、Payload Builder 和 Report Validator。
- Step 2：`AIProvider` 接口、Fake Provider 和 AI Report Service。
- Step 3：冻结 Prompt 与5个 Golden Scenario 测试。
- Step 4：OpenAI Provider、环境变量/Streamlit secrets 配置读取、Structured Outputs 和 Mock 测试。
- Step 5：AI Report Service 完整链路集成测试。
- Step 6A：使用 Fake Provider 完成 AI Report 页面流程、状态展示和 Session State 范围失效机制。
- Step 6B：页面通过统一 Service 接入真实 Provider，并覆盖无 Key、Provider 失败和 Validator 失败状态。
- Step 7：建立5个黄金业务场景的自动约束检查、人工评估记录模板和规则诊断与 AI 增强对比说明。
- Step 8：新增 DeepSeek Provider 和统一 Provider Factory，页面通过 Factory 接入 DeepSeek；真实评估使用 `deepseek-v4-flash`。
- Step 8.2：Prompt优化后真实报告在20.930秒内成功返回合法JSON，Validator通过，Service状态为 `success`，人工评分4.5/5。
- Step 9：同步 AI Report Schema、PRD 和项目上下文，冻结当前展示版本的产品边界与评估结论。

当前状态：

> Phase 3 AI Report MVP 已完成并通过真实 DeepSeek 验证，达到面试展示标准。当前暂停新增产品功能，下一阶段只进行 Demo 优化和面试材料准备。

当前尚未完成：

- AI Report 典型页面截图与规则诊断对比等 Demo 素材。
- 面试讲解文档，包括产品价值、混合架构、AI 增量价值和能力边界。
- 5个黄金业务场景的多次重复稳定性评估；该项用于提高评估证据强度，不阻塞当前 MVP 展示。

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
AI 能力层（MVP 已完成）
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

### AI 能力层

AI Report MVP 已经实现并通过真实 DeepSeek 验证。Payload Builder 只向模型提供白名单 KPI、Finding、Evidence 及对应 Cause/Action 候选；Prompt 负责假设语气、数字边界、行动具体性和全局行动顺序等输出约束；`AIProvider` 接口隔离具体模型调用；Provider Factory 根据配置创建 DeepSeek、OpenAI 或测试 Provider；Service 负责编排 Payload、Provider 和 Validator；Validator 负责 JSON 结构、全局 Action Sequence 与 ID 引用可靠性。诊断页面只调用 Service，并在报告通过校验后展示经营摘要、问题解释、问题关联、原因假设、行动顺序与数据限制。AI 不重新计算 KPI，也不直接读取原始 CSV。无 API Key 或调用失败时，确定性诊断能力保持可用。

## 4. 当前代码结构

```text
app.py
pages/
  1_经营总览.py
  2_AI经营诊断.py
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
  ai_report_models.py
  ai_report_payload.py
  ai_report_validator.py
  ai_provider.py
  fake_ai_provider.py
  ai_report_service.py
  ai_prompt.py
  providers/
    openai_provider.py
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
  test_diagnosis_page.py
  test_ai_report_models.py
  test_ai_report_payload.py
  test_ai_report_validator.py
  test_ai_provider.py
  test_ai_report_service.py
  test_ai_prompt.py
  test_openai_provider.py
  test_ai_report_page.py
  test_ai_evaluation.py
docs/
  PROJECT_CONTEXT.md
  PHASE3_AI_REPORT_PRD.md
  AI_REPORT_SCHEMA.md
  AI_EVALUATION.md
  AI_EVALUATION_RESULT.md
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

Phase 2 经营 Dashboard。负责日期、类目、商品筛选以及 KPI、趋势、结构和库存展示，并提供进入 AI 经营诊断页面的入口。

#### `pages/2_AI经营诊断.py`

Phase 3 确定性诊断与 AI 增强报告页面。负责日期、类目和商品筛选，调用 DiagnosisContext 与规则引擎，用业务卡片展示数据证据、系统判断、可能原因和行动建议；在其后通过 AI Report Service 生成并展示经过校验的 AI 报告。页面不处理 API Key、不拼接 Prompt，也不直接调用模型 SDK；筛选范围变化时旧报告自动失效。

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

#### `src/ai_report_models.py`

定义经过校验的 AI 报告数据结构与 `success`、`unavailable`、`provider_error`、`validation_error` 等生成状态。

#### `src/ai_report_payload.py`

将 DiagnosisContext 和 Finding 转换为可 JSON 序列化的模型输入，只包含分析范围、KPI 白名单、证据及当前 Finding 允许的 Cause/Action 候选，不序列化原始 DataFrame。

#### `src/ai_report_validator.py`

校验 AIReport JSON 结构、字段类型、Finding 引用，以及 Cause/Action 是否属于对应 Finding 的允许候选。

#### `src/ai_provider.py`

定义 Provider 中立的 `AIProvider` 接口和冻结的 Structured Outputs Schema。

#### `src/ai_provider_factory.py`

根据 `AI_PROVIDER`、环境变量和 Streamlit secrets 创建统一 Provider。当前真实演示默认使用 DeepSeek，页面不直接依赖具体厂商实现。

#### `src/fake_ai_provider.py`

提供不需要网络和 API Key 的确定性 Provider，用于测试和本地后端演示。

#### `src/ai_report_service.py`

作为页面唯一的 AI 报告调用入口，依次执行 Payload 构建、Provider 调用和 Validator 校验，并返回稳定的降级状态。

#### `src/ai_prompt.py`

维护冻结的 System Prompt、用户输入模板和 JSON 输出约束，明确 AI 不读取原始 CSV、不创建新业务 ID、不修改 Finding Priority。

#### `src/providers/openai_provider.py`

保留 OpenAI `AIProvider` 兼容实现，通过 OpenAI Responses API 和 Structured Outputs 调用模型；Provider 内不包含业务判断或报告校验。

#### `src/providers/deepseek_provider.py`

实现第一版真实演示 `AIProvider`。通过 OpenAI Python SDK 的 Chat Completions 兼容接口调用 DeepSeek 官方 API，支持 `AI_API_KEY`、`AI_MODEL` 和 `AI_BASE_URL` 配置，不负责业务判断或报告校验。

#### `tests/`

覆盖 Phase 1 数据入口、Phase 2 指标与 Dashboard、Phase 3 Context、规则、评分、候选目录、确定性诊断页面，以及 AI Report 模型、Payload、Validator、Provider、Prompt、Service、页面集成和黄金场景约束。

#### `docs/screenshots/`

保存 Phase 2 首页、Dashboard、KPI、趋势、商品排名和库存分析截图。

#### `docs/PHASE3_AI_REPORT_PRD.md`

Phase 3 第 6 阶段“AI经营分析报告”的开发冻结版 PRD V0.3。记录产品目标、AI 输入输出、Provider、Report Validator、页面设计、异常处理和明确不开发范围。

#### `docs/AI_REPORT_SCHEMA.md`

冻结 AIReport JSON 结构、字段类型、必填字段、空数组行为、ID 引用约束和页面展示规则。后续 Prompt、Validator、Provider 和页面展示必须共同遵守该文档。

#### `docs/AI_EVALUATION.md`

定义 AI 经营分析报告的5个黄金场景、报告质量评分、规则诊断与“规则 + AI报告”对照评估、自动指标和产品验收标准，用于判断 AI 是否产生规则卡片之外的实际价值。

#### `docs/AI_EVALUATION_RESULT.md`

记录5个黄金业务场景的预期 AI 行为、禁止结论、实际报告记录方式、人工评分标准、自动质量门槛和 Demo 截图规划。当前已记录两次真实 DeepSeek 评估，Prompt优化后的报告通过 Validator，人工评分4.5/5。

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
- 已纳入当前 156 项全量测试。

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
- 当前加入 Phase 3 测试后，全量 156 项仍全部通过。

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
- Streamlit 确定性 AI 经营诊断页面。
- 日期、类目和商品联动筛选。
- 诊断问题数、高优先级数和影响商品数概览。
- 以业务卡片区分展示数据证据、系统判断、可能原因和行动建议。
- 无数据、筛选为空和无诊断结果状态。
- Dashboard 到 AI 经营诊断页面的入口。
- AI Report、FindingExplanation、CrossIssueInsight、CauseHypothesis、RecommendedAction 和生成结果数据模型。
- 只包含白名单数据的 AI Report Payload Builder。
- JSON 结构、Finding/Cause/Action 引用及跨问题引用校验。
- Provider 中立的 `AIProvider` 接口。
- 无网络、无 Key 的 Fake Provider。
- Payload → Provider → Validator 的 AI Report Service。
- 冻结的 System Prompt、用户输入模板和 JSON 输出约束。
- 5个 Golden Scenario Prompt 测试。
- OpenAI Provider兼容实现、Structured Outputs 和配置读取。
- API、超时、空响应、无 Key 及完整 Service 链路的 Mock 测试。
- AI 经营诊断页面中的“AI增强分析”区域、生成按钮、状态提示和结构化报告展示。
- 页面只通过 AI Report Service 调用 Provider，不直接处理密钥、Prompt 或模型 SDK。
- 筛选范围变化时旧 AI 报告自动失效。
- 无 Finding 不调用 Provider；无 Key、Provider 失败和 Validator 失败不影响确定性诊断。
- 5个黄金业务场景的自动约束检查与人工评估结果记录模板。
- DeepSeek Provider、统一 Provider Factory 和页面真实 Provider 接入。
- `deepseek-v4-flash` 真实 API 评估通过：JSON合法、Validator通过、Service为 `success`。
- Prompt优化后的报告级全局 Action Sequence 和结构化行动建议。

测试情况：

- 当前全量结果：`156 passed`。
- 示例数据默认 30 天可稳定产生 4 条规则诊断。

当前限制：

- Phase 3 确定性诊断第 1–5 阶段已完成，并已创建 `v0.3-rule-diagnosis` 稳定标签。
- Phase 3 第6阶段 PRD、AI Report Schema、AI Evaluation 和技术方案已经冻结。
- Phase 3 第6阶段 Step 1–9 已完成，AI Report MVP 可通过 Fake Provider、Mock Client 和真实 DeepSeek API 验证。
- 当前页面已经提供 AI 报告生成按钮、降级状态和经过 Validator 校验的报告展示。
- 自动测试不调用真实 API；真实 DeepSeek 单次展示评估已通过，多场景重复评估仍可继续补充。
- 典型 AI 报告截图、规则诊断与 AI 增强对比素材及面试讲解文档尚未完成。

## 6. 当前设计原则

- AI 不负责计算业务指标，所有数字由 Pandas 确定性计算。
- LLM 不直接读取原始 CSV，也不接收逐行经营明细。
- 规则层负责发现问题、生成证据和确定优先级。
- 规则引擎负责 Finding Priority，表示问题重要程度。
- AI 层负责解释问题、归纳可能原因、选择候选行动并组织 Action Sequence。
- AI 不得修改或重新计算 Finding Priority。
- AI 解释必须建立在 Finding 和候选目录之上。
- AI 调用通过抽象 `AIProvider` 接口与具体模型服务解耦；第一版真实演示使用 DeepSeek Provider，但不开发多 Provider UI。
- Validator 负责结构、类型、全局行动序号和 ID 引用可靠性；Prompt 负责自然语言边界，不能把 Validator 通过等同于全部内容质量通过。
- AI可以引用 Evidence 或 Catalog 已有数字；AI生成的建议性阈值必须明确为建议，不得表达为当前业务事实。
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
- 未经明确指令开始真实 API 联调、扩展 AI 功能或超出冻结 Schema 的开发。

## 8. 下一步工作计划

Phase 3 AI Report MVP 已完成并通过真实 DeepSeek 验证。下一阶段只优化 Demo 表达和面试材料，不新增产品功能。

### Demo 优化

- 使用已通过 Validator 的 DeepSeek 报告检查页面信息层级、文案可读性和截图完整性。
- 明确区分确定性事实、规则判断、AI原因假设和建议性行动阈值。
- 保留无 Key、Provider失败和Validator失败的降级演示，不新增业务能力。

### Demo 素材

- 补充 AI 经营诊断页面、AI 增强报告和典型降级状态截图。
- 准备规则诊断与 AI 增强的对比说明，突出 AI 的综合解释、原因假设、验证路径和行动顺序价值。
- 不伪造真实模型报告或尚未执行的评估结果。

### 面试文档

- 整理产品背景、目标用户、用户痛点和完整演示流程。
- 解释“Pandas 指标 + 规则诊断 + LLM 解读 + Validator”的混合架构。
- 记录 AI 输入边界、可解释性、失败降级、评估方法和当前 MVP 限制。

继续保持的 MVP 边界：

- 不引入数据库、历史报告或长期记忆。
- 不开发自由聊天、复杂 Agent 或自动执行任务。
- 不重构 Phase 2 Dashboard，不修改现有指标公式。
- 不让 LLM 直接读取原始 CSV。
- 不删除 Fake Provider；它继续用于无网络测试和稳定演示验证。

当前状态：AI Report PRD、Schema、Evaluation、技术方案、真实 DeepSeek验证及 Step 1–9 已完成，AI Report MVP 已形成完整可信页面闭环并达到展示标准。当前未完成事项只有 Demo 素材和面试文档。

## 9. 技术约束

### Python 与依赖

- 要求 Python 3.11+。
- 当前虚拟环境：Python 3.11.9。
- Streamlit：`>=1.35,<2.0`。
- Pandas：`>=2.2,<3.0`。
- Plotly：`>=5.22,<7.0`。
- OpenAI Python SDK：`>=2.0,<3.0`。
- pytest：`>=8.0,<9.0`。

### 测试状态

- 当前测试数量：156。
- 最近一次完整测试：`156 passed`。
- 测试命令：

```powershell
.\.venv\Scripts\python.exe -m pytest
```

### Git 状态

- 当前分支：`main`。
- `main` 跟踪 `origin/main`。
- Phase 3 第6阶段 Step 1–5 checkpoint 提交信息：`feat: complete phase 3 ai report backend foundation`。
- Step 6A、Step 6B、Step 7 存档提交信息：`feat: complete phase 3 ai report mvp`。
- 当前最新提交：`6b2ffe5 feat: complete phase 3 ai report mvp`。
- 当前 `main` 比 `origin/main` ahead 1；DeepSeek接入、Prompt优化和Step 8/9评估文档仍在本地工作区等待验收提交。
- 最新提交和同步状态使用 `git log -1 --oneline` 与 `git status --short --branch` 检查。
- 当前未完成事项为 Demo 素材和面试文档。

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
