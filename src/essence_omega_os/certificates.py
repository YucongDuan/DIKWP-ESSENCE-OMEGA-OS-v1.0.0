from __future__ import annotations

from typing import Any

from .models import ScenarioSpec
from .utils import canonical_json, sha256_text, stable_id


def build_residual_frontier(scenario: ScenarioSpec) -> dict[str, Any]:
    type_counts: dict[str, int] = {}
    open_items: list[dict[str, Any]] = []
    settled_items: list[dict[str, Any]] = []
    for item in scenario.residuals:
        item = dict(item)
        residual_type = str(item.get("type", "untyped"))
        type_counts[residual_type] = type_counts.get(residual_type, 0) + 1
        if item.get("status", "open") == "open":
            open_items.append(item)
        else:
            settled_items.append(item)
    return {
        "open_items": open_items,
        "settled_items": settled_items,
        "type_counts": dict(sorted(type_counts.items())),
        "frontier_status": "OPEN" if open_items else "CURRENTLY_EMPTY_WITHIN_DECLARED_SCOPE",
        "rule": "a residual must be typed, scoped, attributable, and linked to a reopening or settlement condition",
    }


def build_status_vector(scenario: ScenarioSpec, evaluation: dict[str, Any]) -> dict[str, Any]:
    selected_map = {
        item["candidate_id"]: item
        for item in evaluation["candidate_evaluations"]
        if item["candidate_id"] in evaluation["selected_candidate_ids"]
    }
    selected_values = list(selected_map.values())
    if selected_values:
        causal = "CERTIFIED_WITHIN_SCOPE"
        cross_world = "CERTIFIED_WITHIN_DECLARED_WORLDS" if all(item["metrics"]["transport"] == 1.0 for item in selected_values) else "OPEN"
        reverse = "CERTIFIED_WITHIN_SCOPE" if all(item["reverse_result"]["passed"] for item in selected_values) else "OPEN"
        minimality = "CERTIFIED_WITHIN_SCOPE" if all(item["minimality_result"]["all_components_necessary"] for item in selected_values) else "OPEN"
    else:
        causal = cross_world = reverse = minimality = "NOT_ESTABLISHED"

    normative_pass = all(item["normative_result"]["passed"] for item in selected_values) if selected_values else False
    ontology = dict(scenario.ontology_claims)
    default_ontology = {
        "ultimate_ontology": "NOT_ESTABLISHED",
        "true_life": "NOT_ESTABLISHED",
        "phenomenal_consciousness": "NOT_ESTABLISHED",
        "unique_final_value_function": "NOT_ESTABLISHED",
    }
    default_ontology.update(ontology)
    return {
        "local_structural_sufficiency": causal,
        "causal_minimality": minimality,
        "cross_world_transport": cross_world,
        "reverse_regeneration": reverse,
        "normative_admissibility": "SATISFIED_FOR_DECLARED_USE" if normative_pass else "NOT_ESTABLISHED_OR_NOT_APPLICABLE",
        "ultimate_essence": evaluation["ultimate_essence_status"],
        "ultimate_ontology": default_ontology["ultimate_ontology"],
        "true_life": default_ontology["true_life"],
        "phenomenal_consciousness": default_ontology["phenomenal_consciousness"],
        "unique_final_value_function": default_ontology["unique_final_value_function"],
        "automatic_external_action_authority": 0,
    }


def build_certificate(
    scenario: ScenarioSpec,
    evaluation: dict[str, Any],
    semantic_graph: dict[str, Any],
    residual_frontier: dict[str, Any],
    probe_plan: dict[str, Any],
    ledger_head_hash: str,
    version: str,
) -> dict[str, Any]:
    evaluation_map = {item["candidate_id"]: item for item in evaluation["candidate_evaluations"]}
    selected = [evaluation_map[item] for item in evaluation["selected_candidate_ids"]]
    certificate: dict[str, Any] = {
        "certificate_type": "DIKWP_ESSENCE_OMEGA_BOUNDED_ESSENCE_CERTIFICATE",
        "system": "DIKWP-ESSENCE-OMEGA-OS",
        "version": version,
        "scenario_id": scenario.scenario_id,
        "title": {"en": scenario.title_en, "zh": scenario.title_zh},
        "scope": scenario.scope,
        "purpose_owner": scenario.purpose.get("owner", "unnamed"),
        "selected_essence_candidates": [
            {
                "candidate_id": item["candidate_id"],
                "name": item["name"],
                "components": item["components"],
                "essence_level": item["essence_level"],
                "falsification_conditions": item["falsification_conditions"],
                "forbidden_inferences": item["forbidden_inferences"],
                "metrics": item["metrics"],
            }
            for item in selected
        ],
        "local_essence_status": evaluation["local_essence_status"],
        "ultimate_essence_status": evaluation["ultimate_essence_status"],
        "status_vector": build_status_vector(scenario, evaluation),
        "residual_frontier": residual_frontier,
        "probe_plan": probe_plan,
        "selection_rule": evaluation["selection_rule"],
        "semantic_graph_digest": sha256_text(canonical_json(semantic_graph)),
        "essence_lattice_digest": sha256_text(canonical_json(evaluation["essence_lattice"])),
        "ledger_head_hash": ledger_head_hash,
        "causal_handoff": {
            "owner": scenario.handoff.get("owner", scenario.purpose.get("owner", "unnamed")),
            "next_action": scenario.handoff.get("next_action", "none declared"),
            "required_artifact": scenario.handoff.get("required_artifact", "written evidence or experiment result"),
            "kill_conditions": scenario.handoff.get("kill_conditions", []),
        },
        "global_boundary": {
            "statement": "local causal-generative sufficiency is not a proof of final metaphysical essence",
            "external_action_authority": 0,
            "no_silent_scope_expansion": True,
            "no_harm_value_aggregation": True,
        },
    }
    certificate["certificate_id"] = stable_id("essence-cert", certificate)
    certificate["certificate_sha256"] = sha256_text(canonical_json(certificate))
    return certificate
