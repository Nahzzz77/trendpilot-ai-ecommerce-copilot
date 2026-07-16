# TrendPilot Phase 3 第6阶段 PRD

## AI经营分析报告

版本：V0.3

状态：开发冻结版

项目：TrendPilot

目标：
在已有确定性经营诊断基础上，引入受约束的大语言模型能力，生成可信、可解释、有明确行动顺序的经营分析报告。

---

# 1. 背景

TrendPilot 当前已经完成：

- CSV 数据上传与校验
- 经营 Dashboard
- KPI 指标计算
- 周期对比分析
- 商品、类目、库存分析
- 确定性规则诊断
- Finding / Evidence 数据结构
- Cause Catalog
- Action Catalog
- AI经营诊断页面


当前系统已经可以回答：

- 发生了什么问题？
- 哪些指标异常？
- 哪些问题优先级更高？
- 每个问题有哪些候选原因和行动？


但仍存在不足：

1. 用户需要自己综合多个问题。
2. 系统不能解释多个问题之间的关系。
3. 原因候选没有结合当前业务情况排序。
4. 行动建议缺少清晰的执行顺序。
5. 当前没有真正体现 AI 能力。


因此增加 AI经营分析报告。

---

# 2. 产品目标

AI经营分析报告不是替代运营人员决策。

目标：

> 基于系统已经计算完成的经营事实和规则诊断结果，帮助运营人员快速理解重点问题、可能原因、验证方式以及行动顺序。


AI主要完成：

1. 总结当前经营状态。
2. 综合多个诊断问题。
3. 解释问题之间可能关系。
4. 从候选原因中选择可能假设。
5. 对候选行动进行排序。

---

# 3. AI产品原则

## 3.1 事实与解释分离

系统分为三层：

### 数据事实

来源：

- Pandas指标计算

例如：

- 销售额变化
- 转化率变化
- ROAS变化


### 系统诊断

来源：

- Rule Engine

例如：

- 销售下降
- 广告效率下降
- 库存风险


### AI分析

来源：

- LLM

负责：

- 综合解释
- 原因假设
- 行动排序
- 验证建议


三者必须在页面中明确区分。

---

# 4. AI能力边界

## AI允许：

- 总结经营表现
- 综合多个Finding
- 分析Finding之间关系
- 从Cause Catalog选择原因假设
- 从Action Catalog选择行动建议
- 给出验证方式
- 指出数据不足


## AI禁止：

- 读取原始CSV
- 重新计算指标
- 创建新的Finding
- 创建规则之外的问题
- 修改规则Priority
- 重新计算 Finding Priority
- 生成 Payload 或 Catalog 之外的未经验证业务事实数字
- 将AI生成的建议性阈值表达为当前业务事实
- 将相关性描述为确定因果
- 自动执行业务操作


核心原则：

> 业务事实数字由系统提供，解释由AI生成。AI可以提出明确标注的建议性阈值，但不能把建议写成已经验证的事实。

优先级职责必须分离：

- 规则引擎负责计算 `Finding Priority`，表示经营问题的重要程度。
- AI 只能解释已有 `Finding Priority`，不能修改或重新计算它。
- AI 负责 `Action Sequence`，即在候选行动中选择、组织并说明建议执行顺序。

---

# 5. 用户流程


## Step 1

用户上传数据。

流程：

```

上传数据
↓
Dashboard
↓
AI经营诊断页面

```


## Step 2

系统生成确定性诊断：

展示：

- 数据证据
- 系统判断
- 优先级
- 候选原因
- 候选行动


该部分不依赖AI。


## Step 3

用户点击：

```

生成AI经营分析报告

```


按钮说明：

> AI仅使用当前筛选范围内的汇总指标、诊断结果和候选建议，不读取原始CSV。


## Step 4

AI生成报告。


展示：

```

确定性诊断层

↓

AI增强分析层

```

---

# 6. AI输入设计


AI禁止接收：

- 原始CSV
- DataFrame
- Session State
- 无关字段


AI输入：

## 分析范围

包括：

- 日期范围
- 商品范围
- 类目范围


## KPI摘要

包括：

- 销售额
- 销售变化
- 访客
- 转化率
- 广告投入
- ROAS
- 毛利率
- 退款率
- 库存状态


## Findings

包括：

- finding_id
- rule_id
- 问题名称
- 优先级
- Evidence


## Cause Catalog

包括：

- cause_id
- 原因描述

只提供当前 Finding 的 `cause_candidate_ids` 对应条目。


## Action Catalog

包括：

- action_id
- 行动描述
- 观察指标

只提供当前 Finding 的 `action_candidate_ids` 对应条目。

---

# 7. AI输出结构


AI必须返回符合固定 Schema 的结构化 JSON。


冻结结构：

```text
AIReport
├── executive_summary
├── finding_explanations[]
│   ├── finding_id
│   ├── explanation
│   └── why_priority
├── cross_issue_insights[]
│   ├── finding_ids[]
│   └── insight
├── cause_hypotheses[]
│   ├── finding_id
│   ├── cause_id
│   ├── hypothesis
│   └── validation_method
├── recommended_actions[]
│   ├── finding_id
│   ├── action_id
│   ├── action_sequence
│   └── reason
└── limitations[]
```

冻结规则：

- `executive_summary`：总结当前筛选范围内的经营状态。
- `finding_explanations`：只能解释当前已有 Finding，不能创建新的问题，也不能修改规则 Priority。
- `cross_issue_insights`：每条关联分析必须通过 `finding_ids` 引用两个或以上当前已有 Finding。
- `cause_hypotheses`：`cause_id` 必须来自对应 Finding 的 `cause_candidate_ids`。
- `recommended_actions`：`action_id` 必须来自对应 Finding 的 `action_candidate_ids`；`action_sequence` 只表示行动建议的组织顺序，不改变 Finding Priority。
- `limitations`：列出数据不足、不能确认的关系或报告适用边界。
- AI不得生成 Payload 或 Catalog 之外的未经验证业务事实数字；允许引用 Evidence 已有数字，也允许生成明确标注为建议的阈值，但不得复制为新的当前业务事实或重新计算 KPI。
- 页面根据 `finding_id` 从确定性系统取得并渲染 Evidence、指标值和规则 Priority。

字段类型、必填性、空数组行为和页面渲染规则以 `docs/AI_REPORT_SCHEMA.md` 为唯一依据。

---

# 8. 原因假设设计


原因不是事实。

必须使用：

- 可能原因
- 待验证假设
- 建议检查


禁止：

错误：

> 销售下降原因是商品竞争力下降。


正确：

> 商品竞争力下降可能影响转化表现，建议结合价格、评价和商品页面数据进一步验证。

---

# 9. 行动建议设计


行动必须：

- 有清晰顺序
- 有对应问题
- 有验证指标


AI 不自由生成 `observation_metric`。

原因：

Action Catalog 已经为每个行动定义对应观察指标。允许 AI 自由生成可能导致观察指标与行动目录不一致。

职责划分：

AI负责：

- 选择 `action_id`
- 通过 `action_sequence` 组织行动执行顺序
- 解释推荐原因
- 不修改或重新计算 Finding Priority


系统负责：

- 校验 `action_id` 是否属于对应 Finding 的候选行动
- 根据 `action_id` 从 Action Catalog 渲染观察指标
- 根据 Action Catalog 渲染负责人和建议周期

如 AI 在行动理由中生成建议性阈值，必须明确使用“建议”“可作为观察条件”等措辞。该阈值用于帮助运营人员判断行动效果，不属于当前经营事实，也不能覆盖 Action Catalog 的观察指标和建议周期。


示例：

错误：

> 优化广告。


正确：

> 优先检查低ROAS广告计划，观察调整后3-7天ROAS和转化率变化。

---

# 10. Report Validator


第一版 Validator 必须校验：

## 10.1 JSON结构

- 顶层及子项必填字段完整
- 字段数据类型正确
- 数组和字符串符合 `docs/AI_REPORT_SCHEMA.md` 定义
- 不展示任何未通过结构校验的模型输出


## 10.2 Finding引用

所有 `finding_id` 必须存在于当前诊断结果。

AI不能创建新的 Finding，也不能引用当前筛选范围之外的 Finding。


## 10.3 Cause引用

不能只校验 `cause_id` 在全局 Cause Catalog 中存在。

必须满足：

```text
cause_id ∈ 当前 finding 的 cause_candidate_ids
```


## 10.4 Action引用

不能只校验 `action_id` 在全局 Action Catalog 中存在。

必须满足：

```text
action_id ∈ 当前 finding 的 action_candidate_ids
```


## 10.5 跨问题引用

`cross_issue_insights` 中的所有 `finding_ids` 必须存在于当前诊断结果，且每条关联分析至少引用两个不同 Finding。


第一版不做：

- 自然语言事实审核
- 因果判断审核
- Prompt Injection检测
- 复杂内容安全审核

职责边界：

- Validator 负责结构可靠性，包括必填字段、字段类型、全局 Action Sequence 和 Finding/Cause/Action 引用有效性。
- Prompt 负责自然语言输出约束，包括假设语气、数字边界、行动具体性和建议性阈值表达。
- 第一版 Validator 不审核自然语言中的事实、因果或建议阈值，因此通过 Validator 不等于自然语言质量已经自动验收。

---

# 11. Provider设计

系统先定义与具体模型服务解耦的 `AIProvider` 接口。页面、Prompt、Report Validator 和报告展示只依赖该接口，不直接依赖具体厂商 SDK。

第一版真实演示 Provider：

- `DeepSeek Provider`，通过 OpenAI Python SDK 的 Chat Completions 兼容接口调用 DeepSeek 官方 API。

设计目标：

- 保持未来替换模型服务的能力。
- 不在本阶段实现多 Provider 并存、切换或管理能力。
- 不提供多 Provider UI。

要求：

- `AIProvider` 接口独立封装。
- `DeepSeek Provider` 作为第一版真实演示实现。
- 保留 OpenAI Provider 兼容实现和 Fake Provider 测试实现，但不提供多 Provider UI。
- API Key不进入代码
- 支持无Key状态
- 支持Mock测试


配置：

```

AI_PROVIDER=deepseek
AI_API_KEY
AI_MODEL=deepseek-v4-flash
AI_BASE_URL=https://api.deepseek.com

```

---

# 12. 页面设计


保持：

pages/2_AI经营诊断.py


新增区域：

## AI增强分析


包含：

1. 生成按钮

2. 生成状态

3. AI报告


报告展示：

### 经营摘要

### 重点问题分析

### 问题关联

### 原因假设

### 验证方式

### 行动计划

### 数据限制


---

# 13. 异常处理


## 无API Key

展示：

> 当前未配置AI服务，可继续查看确定性诊断结果。


## API失败

展示：

> AI报告生成失败，确定性诊断结果不受影响。


## JSON错误

不展示未验证内容。


## 无诊断问题

不调用AI。

---

# 14. AI价值验收标准


完成后必须满足：


## 产品价值

用户能够：

- 快速理解重点问题
- 知道下一步做什么


## AI价值

AI不能只是：

“重新描述规则结果”。


必须体现：

- 多问题综合
- 原因假设
- 验证路径
- 行动顺序组织


## 技术价值

满足：

- AI不读取原始数据
- AI失败不影响核心功能
- 输出可校验

## 已完成真实模型评估

Phase 3 AI Report MVP 已使用 DeepSeek 官方 API 完成真实验证：

- Provider：DeepSeek。
- Model：`deepseek-v4-flash`。
- Prompt优化后响应时间：20.930秒。
- 返回 JSON 合法。
- Validator通过，Service状态为 `success`。
- Action Sequence在整份报告中从1开始连续且不重复。
- 人工质量评分：4.5/5。

当前结论：AI Report MVP 已达到面试展示标准。仍需在 Demo 文案中说明，原因假设不是确定因果，AI建议性阈值也不是当前业务事实。

---

# 15. 明确不开发


本阶段禁止：

- 自由聊天
- Agent
- 多Agent
- RAG
- 数据库
- 历史报告
- 自动执行
- 销售预测
- 多模型切换
- Prompt编辑器
- 权限系统


---

# 16. 面试展示重点


最终需要向面试官说明：

TrendPilot不是让LLM直接分析业务数据。

而是：

```

确定性指标
-
规则诊断
-
LLM解释与规划
-
输出校验

=
可信AI经营助手

```


AI负责理解和组织。

系统负责事实和约束。

这是本项目核心设计理念。
