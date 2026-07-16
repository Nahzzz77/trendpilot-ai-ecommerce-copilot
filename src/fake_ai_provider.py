"""Deterministic, offline AI provider used for tests and local demonstrations."""

import json
from collections.abc import Mapping
from typing import Any


class FakeAIProvider:
    """Generate a predictable valid report without credentials or network calls."""

    def generate_report(
        self,
        payload: Mapping[str, object],
        schema: Mapping[str, object],
    ) -> str:
        del schema
        findings = payload.get("findings")
        if not isinstance(findings, list) or not findings:
            raise ValueError("FakeAIProvider 需要至少一个 Finding。")

        finding_rows = [self._require_mapping(item) for item in findings]
        finding_explanations = [
            {
                "finding_id": str(item["finding_id"]),
                "explanation": f"系统已识别“{item['title']}”，建议结合确定性证据进一步分析。",
                "why_priority": f"该问题沿用规则引擎给出的 {item['priority']} 优先级。",
            }
            for item in finding_rows
        ]

        finding_ids = [str(item["finding_id"]) for item in finding_rows]
        cross_issue_insights = []
        if len(finding_ids) >= 2:
            cross_issue_insights.append(
                {
                    "finding_ids": finding_ids[:2],
                    "insight": "这两个问题可能同时影响当前经营表现，建议结合验证结果综合判断。",
                }
            )

        cause_hypotheses = []
        recommended_actions = []
        action_sequence = 1
        for item in finding_rows:
            finding_id = str(item["finding_id"])
            cause_candidates = item.get("cause_candidates")
            if isinstance(cause_candidates, list) and cause_candidates:
                cause = self._require_mapping(cause_candidates[0])
                cause_hypotheses.append(
                    {
                        "finding_id": finding_id,
                        "cause_id": str(cause["cause_id"]),
                        "hypothesis": f"“{cause['cause_name']}”可能与该问题相关，仍需进一步验证。",
                        "validation_method": "按照候选原因描述核对对应业务数据和运营记录。",
                    }
                )

            action_candidates = item.get("action_candidates")
            if isinstance(action_candidates, list) and action_candidates:
                action = self._require_mapping(action_candidates[0])
                recommended_actions.append(
                    {
                        "finding_id": finding_id,
                        "action_id": str(action["action_id"]),
                        "action_sequence": action_sequence,
                        "reason": f"建议按顺序执行“{action['action_name']}”，并观察目录定义的指标变化。",
                    }
                )
                action_sequence += 1

        report = {
            "executive_summary": "当前存在需要关注的经营问题，建议结合规则证据依次验证原因并执行候选行动。",
            "finding_explanations": finding_explanations,
            "cross_issue_insights": cross_issue_insights,
            "cause_hypotheses": cause_hypotheses,
            "recommended_actions": recommended_actions,
            "limitations": ["本报告为离线 Fake Provider 输出，不代表真实模型分析结果。"],
        }
        return json.dumps(report, ensure_ascii=False)

    @staticmethod
    def _require_mapping(value: Any) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            raise ValueError("FakeAIProvider 收到的 Finding 结构无效。")
        return value


__all__ = ["FakeAIProvider"]
