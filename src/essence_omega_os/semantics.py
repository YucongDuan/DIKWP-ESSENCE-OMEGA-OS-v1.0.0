from __future__ import annotations

from typing import Any

from .models import ScenarioSpec
from .utils import stable_id

POSITIONS = ("D", "I", "K", "W", "P")
ROUTE_TYPES = tuple(f"{source}->{target}" for source in POSITIONS for target in POSITIONS)


def make_record(position: str, content: dict[str, Any], *, provenance: list[str]) -> dict[str, Any]:
    if position not in POSITIONS:
        raise ValueError(f"unknown DIKWP position: {position}")
    record = {
        "position": position,
        "content": content,
        "provenance": sorted(provenance),
        "status": "active",
    }
    record["record_id"] = stable_id(position.lower(), record)
    return record


def make_route(source: dict[str, Any], target: dict[str, Any], generated_content: dict[str, Any]) -> dict[str, Any]:
    route = {
        "route_type": f"{source['position']}->{target['position']}",
        "source_record_id": source["record_id"],
        "target_record_id": target["record_id"],
        "generated_content": generated_content,
    }
    route["route_id"] = stable_id("route", route)
    return route


def build_semantic_graph(scenario: ScenarioSpec, evaluation: dict[str, Any]) -> dict[str, Any]:
    candidates = {item["candidate_id"]: item for item in evaluation["candidate_evaluations"]}
    selected = [candidates[item] for item in evaluation["selected_candidate_ids"]]
    failed = [item for item in evaluation["candidate_evaluations"] if not item["local_certifiable"]]

    d_record = make_record(
        "D",
        {
            "same_semantics": "declared observations and replayable test outcomes",
            "worlds": [
                {
                    "world_id": world.world_id,
                    "carrier": world.carrier,
                    "environment": world.environment,
                    "observations": world.observations,
                }
                for world in scenario.worlds
            ],
        },
        provenance=[f"scenario:{scenario.scenario_id}"],
    )
    i_record = make_record(
        "I",
        {
            "different_semantics": "candidate disagreements, consequential contrasts, failures, and preserved residuals",
            "failed_candidates": [item["candidate_id"] for item in failed],
            "contrasts": [
                {
                    "test_id": contrast.test_id,
                    "world_a": contrast.world_a,
                    "world_b": contrast.world_b,
                    "relation": contrast.relation,
                }
                for contrast in scenario.contrasts
            ],
            "residual_ids": [str(item.get("residual_id", "unnamed")) for item in scenario.residuals],
        },
        provenance=[f"evaluation:{scenario.scenario_id}"],
    )
    k_record = make_record(
        "K",
        {
            "complete_semantics": "locally certified causal-generative essence candidates within the declared world family",
            "local_status": evaluation["local_essence_status"],
            "selected_candidates": [
                {
                    "candidate_id": item["candidate_id"],
                    "components": item["components"],
                    "essence_level": item["essence_level"],
                }
                for item in selected
            ],
            "ultimate_status": evaluation["ultimate_essence_status"],
        },
        provenance=[f"essence-evaluation:{scenario.scenario_id}"],
    )
    w_record = make_record(
        "W",
        {
            "value_information": "compression may not erase harm, permission, provenance, refusal, or ontological residuals",
            "constraints": scenario.value_constraints,
            "forbidden_inferences": sorted(
                {
                    inference
                    for item in evaluation["candidate_evaluations"]
                    for inference in item["forbidden_inferences"]
                }
            ),
            "non_aggregation": True,
        },
        provenance=[f"purpose:{scenario.purpose.get('owner', 'unnamed')}"],
    )
    p_record = make_record(
        "P",
        {
            "input_output": {
                "input": "declared observations, worlds, tests, candidates, constraints, and residuals",
                "output": "bounded essence certificate, lattice, residual frontier, and causal handoff",
            },
            "purpose_contract": scenario.purpose,
            "next_action": scenario.handoff.get("next_action", "no next action declared"),
            "automatic_external_action_authority": 0,
        },
        provenance=[f"scenario:{scenario.scenario_id}"],
    )

    records = [d_record, i_record, k_record, w_record, p_record]
    by_position = {item["position"]: item for item in records}
    routes = [
        make_route(by_position["D"], by_position["I"], {"operation": "differentiate observations through candidate comparison"}),
        make_route(by_position["I"], by_position["K"], {"operation": "retain only candidates surviving falsification and ablation"}),
        make_route(by_position["W"], by_position["P"], {"operation": "bind value and permission constraints into the executable purpose"}),
        make_route(by_position["P"], by_position["D"], {"operation": "request the next discriminating observation"}),
        make_route(by_position["K"], by_position["P"], {"operation": "convert local essence into a bounded next-step contract"}),
        make_route(by_position["P"], by_position["K"], {"operation": "reverse-regenerate selected consequences from the bounded essence"}),
        make_route(by_position["K"], by_position["D"], {"operation": "register regenerated consequences as explicitly checked sameness"}),
        make_route(by_position["I"], by_position["P"], {"operation": "turn unresolved differences into successor obligations"}),
        make_route(by_position["D"], by_position["P"], {"operation": "allow new evidence to revise or cancel the current purpose"}),
        make_route(by_position["W"], by_position["K"], {"operation": "reopen a causal closure when consequence or permission changes"}),
    ]
    closure_vector = "".join("1" if any(record["position"] == position for record in records) else "0" for position in POSITIONS)
    return {
        "native_positions": list(POSITIONS),
        "supported_route_types": list(ROUTE_TYPES),
        "records": records,
        "routes": routes,
        "closure_vector": closure_vector,
        "carrier_authority": 0,
        "concept_aliases": [
            {
                "alias": "essence",
                "resolves_to": [k_record["record_id"], i_record["record_id"], w_record["record_id"]],
                "authority": "readable alias only; no native semantic generation authority",
            }
        ],
    }
