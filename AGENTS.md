# AGENTS.md

## 项目目标

TrendPilot 是用于 AI 产品经理面试展示的 MVP，面向潮流服饰品牌运营人员。当前阶段通过确定性计算呈现流量、销售、毛利和库存表现。

## 当前阶段约束

- 当前为 Phase 2：只实现确定性经营指标和 Streamlit Dashboard。
- 不实现异常检测、原因解释、LLM 接入或 AI 建议。
- 不加入真实 API Key、密钥文件或模型依赖。
- 不创建没有实际功能的占位页面。
- 保留 Phase 1 的 CSV 上传、字段校验和 Session State 流程。

## 技术与结构

- 使用 Python 3.11+、Streamlit、Pandas、Plotly 和 pytest。
- 页面只负责交互与展示；数据准备、指标和图表分别位于 `src/` 模块。
- 指标层保留完整精度，页面层负责人民币、百分比和小数格式。
- 图表只消费指标层输出，不重复计算 KPI。
- 比率必须先汇总分子和分母再相除，不平均行级或日级比率。

## 数据规则

- 上传数据必须包含 `src/data_validator.py` 中定义的全部必填字段。
- 标识字段不得为空；分析数值必须可解析且非负；评分范围为 0–5。
- 日期筛选为闭区间；空类目或商品筛选表示全部。
- 支付转化率固定为 `Σorders / Σvisitors`。
- 任何示例数据修改都应通过 `scripts/generate_sample_data.py` 可复现生成。

## 修改与验证

- 新功能或修复先补测试，再实现最小必要逻辑。
- 保持既有上传和校验测试通过。
- 完成修改后运行 `python -m pytest`、Streamlit 启动检查和 `git diff --check`。
- 验收前不提交、不推送，也不进入 Phase 3。
