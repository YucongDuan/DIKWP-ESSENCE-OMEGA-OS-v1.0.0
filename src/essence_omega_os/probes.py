from __future__ import annotations

from itertools import combinations
from typing import Any


def _pairwise_disagreement(predictions: dict[str, Any], candidate_ids: list[str]) -> tuple[int, int, float]:
    pairs = list(combinations(candidate_ids, 2))
    if not pairs:
        return 0, 0, 0.0
    disagreements = 0
    evaluable = 0
    for left, right in pairs:
        left_value = predictions.get(left)
        right_value = predictions.get(right)
        if left_value is None or right_value is None:
            continue
        evaluable += 1
        if left_value != right_value:
            disagreements += 1
    score = disagreements / evaluable if evaluable else 0.0
    return disagreements, evaluable, score


def plan_probes(raw_scenario: dict[str, Any], candidate_evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    catalog = raw_scenario.get("probe_catalog", [])
    active_candidates = [
        item["candidate_id"]
        for item in candidate_evaluations
        if item["status"] not in {"SELF_SEALING_REJECTED", "INSUFFICIENT_OR_FALSIFIED"}
    ]
    evaluated: list[dict[str, Any]] = []
    for probe in catalog:
        probe_id = str(probe.get("probe_id", "unnamed"))
        authorized = bool(probe.get("authorized", False))
        reversible = bool(probe.get("reversible", False))
        lease_valid = bool(probe.get("lease_valid", False))
        cost = float(probe.get("cost", 0.0))
        harm = float(probe.get("harm", 0.0))
        irreversibility = float(probe.get("irreversibility", 0.0))
        harm_limit = float(probe.get("harm_limit", 0.0))
        irreversibility_limit = float(probe.get("irreversibility_limit", 0.0))
        hard_pass = authorized and reversible and lease_valid and harm <= harm_limit and irreversibility <= irreversibility_limit
        predictions = {str(k): v for k, v in probe.get("predictions_by_candidate", {}).items()}
        disagreements, pair_count, discrimination = _pairwise_disagreement(predictions, active_candidates)
        evaluated.append(
            {
                "probe_id": probe_id,
                "description": str(probe.get("description", "")),
                "owner": str(probe.get("owner", "unnamed")),
                "hard_filter_passed": hard_pass,
                "authorized": authorized,
                "reversible": reversible,
                "lease_valid": lease_valid,
                "cost": cost,
                "harm": harm,
                "irreversibility": irreversibility,
                "stop_condition": str(probe.get("stop_condition", "not declared")),
                "predictions_by_candidate": predictions,
                "disagreement_pairs": disagreements,
                "evaluable_pairs": pair_count,
                "discrimination": discrimination,
            }
        )

    eligible = [item for item in evaluated if item["hard_filter_passed"]]
    # Declared lexicographic order: maximum discrimination, then minimum harm,
    # minimum irreversibility, minimum cost, stable identifier.
    eligible.sort(
        key=lambda item: (
            -item["discrimination"],
            item["harm"],
            item["irreversibility"],
            item["cost"],
            item["probe_id"],
        )
    )
    selected = eligible[0]["probe_id"] if eligible and eligible[0]["discrimination"] > 0 else None
    return {
        "active_candidate_ids": active_candidates,
        "evaluated_probes": sorted(evaluated, key=lambda item: item["probe_id"]),
        "selected_probe_id": selected,
        "selection_rule": "hard authorization/reversibility/lease/risk filter, then lexicographic discrimination-harm-irreversibility-cost order",
        "aggregate_score_used": False,
        "automatic_external_action_authority": 0,
        "status": "DISCRIMINATING_PROBE_PROPOSED" if selected else "NO_SAFE_DISCRIMINATING_PROBE_DECLARED",
    }
