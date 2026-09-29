"""Decision Rule Trigger & Effectiveness Auditor for Phase 7.3.

Measures trigger frequencies, correct/incorrect decisions, and precision across all decision rules:
- RULE_INSUFFICIENT_ANCHORS (Rule 1)
- RULE_ADMINISTRATIVE_CONTRADICTION (Rule 2)
- RULE_AMBIGUITY_DETECTED (Rule 3)
- RULE_POSTAL_OR_LOW_SCORE_REVIEW (Rule 4)
- RULE_HIGH_CONFIDENCE_VERIFIED (Rule 5)
- RULE_CONSISTENT_STANDARD (Rule 6)
"""

import os
import csv
from typing import Dict, Any, List
from collections import defaultdict
from pydantic import BaseModel, Field


class RuleTriggerMetric(BaseModel):
    rule_name: str
    trigger_count: int = 0
    correct_trigger_count: int = 0
    incorrect_trigger_count: int = 0
    false_positive_count: int = 0
    false_negative_count: int = 0
    precision: float = 0.0


class DecisionRuleAuditor:
    """Audits the trigger behavior and precision of deterministic decision rules."""

    STANDARD_RULES = [
        "RULE_INSUFFICIENT_ANCHORS",
        "RULE_ADMINISTRATIVE_CONTRADICTION",
        "RULE_AMBIGUITY_DETECTED",
        "RULE_POSTAL_OR_LOW_SCORE_REVIEW",
        "RULE_HIGH_CONFIDENCE_VERIFIED",
        "RULE_CONSISTENT_STANDARD",
        "STATE_VERIFIED",
        "DISTRICT_HIERARCHY_VERIFIED",
        "LOCALITY_VERIFIED",
        "PINCODE_CONSISTENT",
        "BOUNDARY_DISTRICT_CONTAINMENT",
        "NO_COORDINATES",
    ]

    @classmethod
    def audit_rules(cls, cases_data: List[Dict[str, Any]]) -> List[RuleTriggerMetric]:
        metrics_map = {r: RuleTriggerMetric(rule_name=r) for r in cls.STANDARD_RULES}

        for d in cases_data:
            rules = d.get("triggered_rules", [])
            correct = d.get("correct", False)
            status = d.get("predicted_status", "")

            for r in rules:
                if r not in metrics_map:
                    metrics_map[r] = RuleTriggerMetric(rule_name=r)
                m = metrics_map[r]
                m.trigger_count += 1
                if correct:
                    m.correct_trigger_count += 1
                else:
                    m.incorrect_trigger_count += 1
                    m.false_positive_count += 1

        # Calculate precisions
        results = []
        for r, m in metrics_map.items():
            if m.trigger_count > 0:
                m.precision = round(m.correct_trigger_count / m.trigger_count * 100.0, 2)
            results.append(m)

        return results

    @classmethod
    def export_csv(cls, metrics: List[RuleTriggerMetric], output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "rule_name",
                "trigger_count",
                "correct_trigger_count",
                "incorrect_trigger_count",
                "false_positive_count",
                "false_negative_count",
                "precision",
            ])
            for m in metrics:
                writer.writerow([
                    m.rule_name,
                    m.trigger_count,
                    m.correct_trigger_count,
                    m.incorrect_trigger_count,
                    m.false_positive_count,
                    m.false_negative_count,
                    m.precision,
                ])
