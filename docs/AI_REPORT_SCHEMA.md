# TrendPilot AI Report Schema

版本：V0.3

状态：开发冻结版

适用阶段：Phase 3 第6阶段“AI经营分析报告”

---

## 1. Schema目的

本文冻结 AI 经营分析报告的产品接口，作为后续 Prompt、Report Validator、AI Provider 和页面展示的共同依据。

目标：

- 让模型只在确定性事实和候选目录范围内进行解释与排序。
- 让所有 AI 输出都可以通过固定结构解析和校验。
- 防止 AI 创建新的 Finding、Cause ID、Action ID 或业务数字。
- 保证 Provider 失败或输出非法时，确定性诊断仍然独立可用。

本文定义的是产品数据契约，不绑定具体 Provider、模型或 SDK 实现。后续代码通过 `AIProvider` 接口使用该契约，第一版实现 OpenAI Provider，但 Schema 不因此增加厂商专属字段。

---

## 2. 输入输出关系

### 2.1 AI输入

AI只接收经过白名单转换的结构化输入：

- 当前分析日期、类目和商品范围。
- 确定性 KPI 摘要及其单位、基准和变化类型。
- 当前诊断结果中的 Finding、Rule ID、规则 Priority 和 Evidence。
- 每个 Finding 对应的 `cause_candidate_ids` 及 Cause Catalog 内容。
- 每个 Finding 对应的 `action_candidate_ids` 及 Action Catalog 内容。

AI不接收：

- 原始 CSV。
- Pandas DataFrame。
- Streamlit Session State。
- 商品逐行经营明细。
- 与当前 Finding 无关的 Cause 或 Action。

### 2.2 AI输出

AI只返回：

- 经营状态总结。
- 对已有 Finding 的解释。
- 已有 Finding 之间的可能关系。
- 从允许候选中选择的原因假设。
- 从允许候选中选择并排序的行动。
- 数据限制与不能确认的内容。

AI不返回业务数字。页面中的销售额、变化率、ROAS、库存天数等数字，必须根据 `finding_id` 从确定性 Finding 和 Evidence 中渲染。

---

## 3. AIReport JSON结构

```json
{
  "executive_summary": "当前经营状态的综合总结。",
  "finding_explanations": [
    {
      "finding_id": "已有的 finding_id",
      "explanation": "对该问题的业务解释。",
      "why_priority": "说明现有规则优先级为什么值得关注，但不修改优先级。"
    }
  ],
  "cross_issue_insights": [
    {
      "finding_ids": [
        "已有的 finding_id 1",
        "已有的 finding_id 2"
      ],
      "insight": "多个已有问题之间可能存在的关系。"
    }
  ],
  "cause_hypotheses": [
    {
      "finding_id": "已有的 finding_id",
      "cause_id": "该 Finding 允许的 cause_id",
      "hypothesis": "使用可能、假设或待验证语气描述原因。",
      "validation_method": "运营人员可以执行的验证方式。"
    }
  ],
  "recommended_actions": [
    {
      "finding_id": "已有的 finding_id",
      "action_id": "该 Finding 允许的 action_id",
      "action_sequence": 1,
      "reason": "为什么建议按该顺序执行该行动。"
    }
  ],
  "limitations": [
    "当前数据不足以确认的内容。"
  ]
}
```

固定规则：

- 顶层只能包含上述6个字段。
- 所有6个顶层字段均为必填。
- 子项只能包含本文列出的字段。
- Provider 返回其他字段时视为结构不符合要求。

---

## 4. 字段说明

### 4.1 `executive_summary`

- 类型：字符串。
- 必填：是。
- 允许为空：否。
- 用途：综合当前筛选范围内的主要经营状态。
- 约束：不能包含输入中不存在的数字，不能创建新的经营问题。

### 4.2 `finding_explanations`

- 类型：对象数组。
- 必填：是。
- 报告生成成功时至少包含1项。
- 用途：解释值得关注的已有 Finding。

子字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `finding_id` | 字符串 | 是 | 必须引用当前诊断结果中的 Finding |
| `explanation` | 字符串 | 是 | 对已有问题的业务解释，不得创建新问题 |
| `why_priority` | 字符串 | 是 | 解释现有规则 Priority 的业务意义，不得修改 Priority |

### 4.3 `cross_issue_insights`

- 类型：对象数组。
- 必填：是。
- 允许为空数组：是。
- 用途：描述两个或以上已有 Finding 之间的可能关系。

子字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `finding_ids` | 字符串数组 | 是 | 至少包含2个不同且有效的当前 Finding ID |
| `insight` | 字符串 | 是 | 使用可能关系表达，不得描述为确定因果 |

如果当前只有一个 Finding，或数据不足以支持问题关联，必须返回空数组，不得为了填充结构编造关联。

### 4.4 `cause_hypotheses`

- 类型：对象数组。
- 必填：是。
- 允许为空数组：是。
- 用途：从对应 Finding 允许的 Cause Catalog 候选中选择待验证原因。

子字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `finding_id` | 字符串 | 是 | 原因假设对应的当前 Finding |
| `cause_id` | 字符串 | 是 | 必须属于该 Finding 的 `cause_candidate_ids` |
| `hypothesis` | 字符串 | 是 | 必须使用可能、假设或待验证语气 |
| `validation_method` | 字符串 | 是 | 说明如何进一步验证该原因假设 |

### 4.5 `recommended_actions`

- 类型：对象数组。
- 必填：是。
- 允许为空数组：是。
- 用途：从对应 Finding 允许的 Action Catalog 候选中选择行动并排序。

子字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `finding_id` | 字符串 | 是 | 行动对应的当前 Finding |
| `action_id` | 字符串 | 是 | 必须属于该 Finding 的 `action_candidate_ids` |
| `action_sequence` | 正整数 | 是 | 表示整份报告中的行动建议顺序，从1开始连续编号且不得重复 |
| `reason` | 字符串 | 是 | 解释为什么建议按该顺序执行 |

页面按 `action_sequence` 从小到大展示行动。`action_sequence` 只负责组织行动建议，不得修改、替代或重新计算 Finding 的规则 Priority。

AI不返回 `observation_metric`。页面根据 `action_id` 从 Action Catalog 确定性渲染观察指标、负责人和建议周期。

### 4.6 `limitations`

- 类型：字符串数组。
- 必填：是。
- 允许为空数组：是。
- 用途：说明当前数据不足、无法确认的因果关系或报告适用边界。
- 约束：不能通过虚构内容消除真实限制。

---

## 5. 必填字段

顶层必填字段：

- `executive_summary`
- `finding_explanations`
- `cross_issue_insights`
- `cause_hypotheses`
- `recommended_actions`
- `limitations`

所有数组子项都必须包含各自定义的全部子字段。字符串字段必须为字符串，数组字段必须为数组；不能使用 `null` 代替必填字符串或数组。

---

## 6. 空数组行为

| 字段 | 是否允许空数组 | 行为 |
|---|---|---|
| `finding_explanations` | 否 | 有 Finding 才调用 AI，因此成功报告至少解释1个 Finding |
| `cross_issue_insights` | 是 | Finding 少于2个或没有可靠关联时返回 `[]` |
| `cause_hypotheses` | 是 | 没有足够依据选择原因候选时返回 `[]` |
| `recommended_actions` | 是 | 没有适用候选行动时返回 `[]` |
| `limitations` | 是 | 没有额外限制时返回 `[]` |

当当前诊断结果为空时，系统不得调用 AI Provider，也不得生成 AIReport。

---

## 7. ID引用规则

### 7.1 Finding

以下字段中的 Finding ID 都必须存在于当前诊断结果：

- `finding_explanations[].finding_id`
- `cross_issue_insights[].finding_ids[]`
- `cause_hypotheses[].finding_id`
- `recommended_actions[].finding_id`

### 7.2 Cause

每个原因假设必须满足：

```text
cause_hypotheses[].cause_id
∈ 对应 finding_id 的 cause_candidate_ids
```

只在全局 Cause Catalog 中存在但不属于对应 Finding 的 `cause_id`，仍然属于无效引用。

### 7.3 Action

每个推荐行动必须满足：

```text
recommended_actions[].action_id
∈ 对应 finding_id 的 action_candidate_ids
```

只在全局 Action Catalog 中存在但不属于对应 Finding 的 `action_id`，仍然属于无效引用。

任何无效引用都会使整份报告校验失败；页面不得展示部分未验证内容。

---

## 8. 页面展示规则

页面保持两层信息结构：

```text
确定性诊断层
↓
AI增强分析层
```

展示规则：

1. 经营摘要展示 `executive_summary`。
2. 重点问题分析展示 `finding_explanations`，并根据 `finding_id` 追加确定性 Evidence。
3. 问题关联展示 `cross_issue_insights` 引用的 Finding 标题和 `insight`。
4. 原因假设展示 `hypothesis` 与 `validation_method`，并明确标注为待验证假设。
5. 行动计划按照 `action_sequence` 展示 `reason`；观察指标、负责人和建议周期由系统根据 `action_id` 从 Action Catalog 渲染。
6. 数据限制展示 `limitations`。
7. 页面不直接展示 Provider 返回的原始 JSON。
8. 只有整份报告通过 Validator 后才能展示 AI 内容。
9. 日期、类目、商品或 Finding 集合变化后，之前的 AIReport 必须失效。
10. 无 API Key、Provider 失败或校验失败时，只展示确定性诊断和友好提示。

---

## 9. 共同依据

后续模块必须共同遵守本文：

- Prompt：要求模型严格返回本文结构。
- Validator：按本文检查结构、类型和 ID 引用。
- AIProvider：定义与具体模型服务解耦的调用接口，只传递白名单输入并返回待校验 JSON；第一版 OpenAI Provider 必须遵守同一接口和 Schema。
- 页面：只渲染已通过校验的 AIReport，并从确定性系统补充业务数字和 Action Catalog 信息。

如需变更字段，必须先更新本文和 PRD，再进入代码修改。
