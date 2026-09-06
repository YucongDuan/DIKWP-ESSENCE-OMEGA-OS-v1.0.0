from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import CandidateSpec, ScenarioSpec
from .utils import canonical_json, ratio, sha256_text

WILDCARD_VALUES = {"*", "ANY", "any", "wildcard", "WILDCARD"}


@dataclass(frozen=True)
class Cell:
    world_id: str
    test_id: str
    observed: Any
    predicted: Any
    required: bool
    kind: str

    @property
    def is_missing(self) -> bool:
        return self.predicted is None

    @property
    def is_wildcard(self) -> bool:
        return isinstance(self.predicted, str) and self.predicted in WILDCARD_VALUES

    @property
    def is_correct(self) -> bool:
        return not self.is_missing and not self.is_wildcard and self.predicted == self.observed


class EssenceEvaluator:
    """Evaluate bounded essence candidates without granting metaphysical authority.

    An essence candidate must do more than fit observations. It must survive declared
    nuisance transformations, discriminate consequential changes, expose falsifiers,
    demonstrate component necessity, and regenerate its observable consequences in the
    reverse direction. The result is always scoped to the declared world family.
    """

    def __init__(self, scenario: ScenarioSpec):
        self.scenario = scenario

    def _cells(self, candidate: CandidateSpec, predictions: dict[str, dict[str, Any]] | None = None) -> list[Cell]:
        predictions = predictions if predictions is not None else candidate.predictions
        cells: list[Cell] = []
        test_map = self.scenario.test_map
        for world_id in candidate.scope_worlds:
            world = self.scenario.world_map[world_id]
            world_predictions = predictions.get(world_id, {})
            for test_id, observed in sorted(world.observations.items()):
                spec = test_map[test_id]
                cells.append(
                    Cell(
                        world_id=world_id,
                        test_id=test_id,
                        observed=observed,
                        predicted=world_predictions.get(test_id),
                        required=spec.required,
                        kind=spec.kind,
                    )
                )
        return cells

    def _contrast_result(self, candidate: CandidateSpec) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []
        for contrast in self.scenario.contrasts:
            if contrast.world_a not in candidate.scope_worlds or contrast.world_b not in candidate.scope_worlds:
                continue
            prediction_a = candidate.predictions.get(contrast.world_a, {}).get(contrast.test_id)
            prediction_b = candidate.predictions.get(contrast.world_b, {}).get(contrast.test_id)
            observed_a = self.scenario.world_map[contrast.world_a].observations.get(contrast.test_id)
            observed_b = self.scenario.world_map[contrast.world_b].observations.get(contrast.test_id)
            expected_relation = observed_a != observed_b if contrast.relation == "different" else observed_a == observed_b
            candidate_relation = prediction_a != prediction_b if contrast.relation == "different" else prediction_a == prediction_b
            explicit = (
                prediction_a is not None
                and prediction_b is not None
                and prediction_a not in WILDCARD_VALUES
                and prediction_b not in WILDCARD_VALUES
            )
            passed = bool(explicit and expected_relation and candidate_relation and prediction_a == observed_a and prediction_b == observed_b)
            checks.append(
                {
                    "test_id": contrast.test_id,
                    "world_a": contrast.world_a,
                    "world_b": contrast.world_b,
                    "relation": contrast.relation,
                    "observed": [observed_a, observed_b],
                    "predicted": [prediction_a, prediction_b],
                    "passed": passed,
                }
            )
        return {"checks": checks, "passed": all(item["passed"] for item in checks) if checks else True}

    def _reverse_result(self, candidate: CandidateSpec) -> dict[str, Any]:
        cells = self._cells(candidate, candidate.reverse_regeneration)
        required_cells = [cell for cell in cells if cell.required]
        correct = [cell for cell in required_cells if cell.is_correct]
        failures = [
            {
                "world_id": cell.world_id,
                "test_id": cell.test_id,
                "observed": cell.observed,
                "regenerated": cell.predicted,
            }
            for cell in required_cells
            if not cell.is_correct
        ]
        return {
            "required_cells": len(required_cells),
            "correct_cells": len(correct),
            "score": ratio(len(correct), len(required_cells), empty=0.0),
            "passed": bool(required_cells) and len(correct) == len(required_cells),
            "failures": failures,
        }

    def _minimality_result(self, candidate: CandidateSpec, base_cells: list[Cell]) -> dict[str, Any]:
        base_required = [cell for cell in base_cells if cell.required]
        base_correct_keys = {(cell.world_id, cell.test_id) for cell in base_required if cell.is_correct}
        component_results: list[dict[str, Any]] = []
        for component in candidate.components:
            ablated_predictions = candidate.ablations.get(component)
            if ablated_predictions is None:
                component_results.append(
                    {
                        "component": component,
                        "tested": False,
                        "necessary": None,
                        "failed_cells": [],
                    }
                )
                continue
            ablated_cells = self._cells(candidate, ablated_predictions)
            failed_cells = [
                {
                    "world_id": cell.world_id,
                    "test_id": cell.test_id,
                    "observed": cell.observed,
                    "ablated_prediction": cell.predicted,
                }
                for cell in ablated_cells
                if cell.required
                and (cell.world_id, cell.test_id) in base_correct_keys
                and not cell.is_correct
            ]
            component_results.append(
                {
                    "component": component,
                    "tested": True,
                    "necessary": bool(failed_cells),
                    "failed_cells": failed_cells,
                }
            )
        all_tested = bool(component_results) and all(item["tested"] for item in component_results)
        all_necessary = all_tested and all(item["necessary"] is True for item in component_results)
        redundant = [item["component"] for item in component_results if item["necessary"] is False]
        untested = [item["component"] for item in component_results if not item["tested"]]
        return {
            "all_components_tested": all_tested,
            "all_components_necessary": all_necessary,
            "redundant_components": redundant,
            "untested_components": untested,
            "component_results": component_results,
        }

    def _normative_result(self, candidate: CandidateSpec) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []
        for constraint in self.scenario.value_constraints:
            status_map = constraint.get("status_by_candidate", {})
            status = status_map.get(candidate.candidate_id, constraint.get("default_status", "not_applicable"))
            checks.append(
                {
                    "constraint_id": str(constraint.get("constraint_id", "unnamed")),
                    "description": str(constraint.get("description", "")),
                    "status": str(status),
                    "hard": bool(constraint.get("hard", True)),
                }
            )
        violated = [item for item in checks if item["hard"] and item["status"] == "violated"]
        unknown = [item for item in checks if item["hard"] and item["status"] == "unknown"]
        return {
            "checks": checks,
            "passed": not violated and not unknown,
            "violations": violated,
            "unknown": unknown,
        }

    def _residual_result(self, candidate: CandidateSpec) -> dict[str, Any]:
        applicable: list[dict[str, Any]] = []
        for residual in self.scenario.residuals:
            candidate_ids = [str(item) for item in residual.get("candidate_ids", [])]
            if candidate_ids and candidate.candidate_id not in candidate_ids:
                continue
            applicable.append(dict(residual))
        blocking = [item for item in applicable if item.get("status", "open") == "open" and item.get("blocks_local_certification", False)]
        critical = [item for item in applicable if item.get("status", "open") == "open" and item.get("critical", False)]
        return {
            "items": applicable,
            "open_count": sum(1 for item in applicable if item.get("status", "open") == "open"),
            "critical_open_count": len(critical),
            "blocking_open_count": len(blocking),
            "blocks_local_certification": bool(blocking),
        }

    def evaluate_candidate(self, candidate: CandidateSpec) -> dict[str, Any]:
        cells = self._cells(candidate)
        required_cells = [cell for cell in cells if cell.required]
        explicit_cells = [cell for cell in required_cells if not cell.is_missing and not cell.is_wildcard]
        correct_cells = [cell for cell in required_cells if cell.is_correct]
        wildcard_cells = [cell for cell in required_cells if cell.is_wildcard]
        missing_cells = [cell for cell in required_cells if cell.is_missing]
        mismatch_cells = [cell for cell in explicit_cells if not cell.is_correct]
        kinds: dict[str, dict[str, Any]] = {}
        for kind in sorted({cell.kind for cell in required_cells}):
            group = [cell for cell in required_cells if cell.kind == kind]
            correct = [cell for cell in group if cell.is_correct]
            kinds[kind] = {
                "cells": len(group),
                "correct": len(correct),
                "score": ratio(len(correct), len(group)),
                "passed": len(correct) == len(group),
            }

        world_results: list[dict[str, Any]] = []
        for world_id in candidate.scope_worlds:
            group = [cell for cell in required_cells if cell.world_id == world_id]
            correct = [cell for cell in group if cell.is_correct]
            world_results.append(
                {
                    "world_id": world_id,
                    "carrier": self.scenario.world_map[world_id].carrier,
                    "required_cells": len(group),
                    "correct_cells": len(correct),
                    "passed": bool(group) and len(correct) == len(group),
                }
            )

        contrast = self._contrast_result(candidate)
        reverse = self._reverse_result(candidate)
        minimality = self._minimality_result(candidate, cells)
        normative = self._normative_result(candidate)
        residual = self._residual_result(candidate)

        falsifiable = bool(candidate.falsification_conditions) and not candidate.scope_can_change_after_failure
        self_sealing_reasons: list[str] = []
        if wildcard_cells:
            self_sealing_reasons.append("wildcard predictions absorb possible counterexamples")
        if not candidate.falsification_conditions:
            self_sealing_reasons.append("no declared falsification condition")
        if candidate.scope_can_change_after_failure:
            self_sealing_reasons.append("scope may be changed after failure")

        required_passed = bool(required_cells) and len(correct_cells) == len(required_cells)
        transport_passed = bool(world_results) and all(item["passed"] for item in world_results)
        structural_passed = required_passed and contrast["passed"]
        causal_minimal_passed = structural_passed and minimality["all_components_necessary"]
        generative_passed = causal_minimal_passed and reverse["passed"]
        local_certifiable = (
            generative_passed
            and transport_passed
            and falsifiable
            and not self_sealing_reasons
            and normative["passed"]
            and not residual["blocks_local_certification"]
        )

        if self_sealing_reasons:
            status = "SELF_SEALING_REJECTED"
            essence_level = "L0_REJECTED"
        elif not required_passed:
            status = "INSUFFICIENT_OR_FALSIFIED"
            essence_level = "L1_PARTIAL_DESCRIPTION"
        elif not minimality["all_components_tested"]:
            status = "MINIMALITY_NOT_ESTABLISHED"
            essence_level = "L2_PREDICTIVE_CORE"
        elif not minimality["all_components_necessary"]:
            status = "OVERCOMPLETE_NONMINIMAL"
            essence_level = "L2_PREDICTIVE_CORE"
        elif not contrast["passed"] or not transport_passed:
            status = "LOCAL_CAUSAL_CORE_ONLY"
            essence_level = "L3_CAUSAL_MINIMAL_CORE"
        elif not reverse["passed"]:
            status = "REVERSE_REGENERATION_OPEN"
            essence_level = "L4_CROSS_WORLD_CORE"
        elif not normative["passed"]:
            status = "BLOCKED_BY_VALUE_OR_PERMISSION"
            essence_level = "L4_CROSS_WORLD_CORE"
        elif residual["blocks_local_certification"]:
            status = "BLOCKED_BY_DECLARED_RESIDUAL"
            essence_level = "L4_CROSS_WORLD_CORE"
        else:
            status = "ESSENCE_CERTIFIED_WITHIN_DECLARED_SCOPE"
            essence_level = "L5_REVERSIBLE_GENERATIVE_ESSENCE"

        failure_cells = [
            {
                "world_id": cell.world_id,
                "test_id": cell.test_id,
                "observed": cell.observed,
                "predicted": cell.predicted,
                "failure_type": "wildcard" if cell.is_wildcard else "missing" if cell.is_missing else "mismatch",
            }
            for cell in required_cells
            if not cell.is_correct
        ]

        signature = {
            world_id: {test_id: candidate.predictions.get(world_id, {}).get(test_id) for test_id in sorted(self.scenario.world_map[world_id].observations)}
            for world_id in candidate.scope_worlds
        }
        return {
            "candidate_id": candidate.candidate_id,
            "name": {"en": candidate.name_en, "zh": candidate.name_zh},
            "components": list(candidate.components),
            "component_count": len(candidate.components),
            "scope_worlds": list(candidate.scope_worlds),
            "status": status,
            "essence_level": essence_level,
            "local_certifiable": local_certifiable,
            "metrics": {
                "coverage": ratio(len(explicit_cells), len(required_cells), empty=0.0),
                "fidelity": ratio(len(correct_cells), len(required_cells), empty=0.0),
                "transport": ratio(sum(1 for item in world_results if item["passed"]), len(world_results), empty=0.0),
                "reverse_regeneration": reverse["score"],
                "contrast": ratio(sum(1 for item in contrast["checks"] if item["passed"]), len(contrast["checks"])),
                "minimality": 1.0 if minimality["all_components_necessary"] else 0.0,
                "falsifiability": 1.0 if falsifiable else 0.0,
                "wildcard_rate": ratio(len(wildcard_cells), len(required_cells), empty=0.0),
                "description_length_proxy": len(canonical_json({"components": candidate.components, "predictions": signature})),
            },
            "kind_results": kinds,
            "world_results": world_results,
            "contrast_result": contrast,
            "reverse_result": reverse,
            "minimality_result": minimality,
            "normative_result": normative,
            "residual_result": residual,
            "falsifiable": falsifiable,
            "self_sealing_reasons": self_sealing_reasons,
            "failure_cells": failure_cells,
            "falsification_conditions": list(candidate.falsification_conditions),
            "forbidden_inferences": list(candidate.forbidden_inferences),
            "lineage": dict(candidate.lineage),
            "prediction_signature_sha256": sha256_text(canonical_json(signature)),
        }

    @staticmethod
    def _dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
        positive = ["fidelity", "coverage", "transport", "reverse_regeneration", "contrast", "minimality", "falsifiability"]
        a_metrics = a["metrics"]
        b_metrics = b["metrics"]
        no_worse = all(a_metrics[key] >= b_metrics[key] for key in positive)
        no_worse = no_worse and a_metrics["wildcard_rate"] <= b_metrics["wildcard_rate"]
        no_worse = no_worse and a["component_count"] <= b["component_count"]
        strictly_better = any(a_metrics[key] > b_metrics[key] for key in positive)
        strictly_better = strictly_better or a_metrics["wildcard_rate"] < b_metrics["wildcard_rate"]
        strictly_better = strictly_better or a["component_count"] < b["component_count"]
        return bool(no_worse and strictly_better)

    def build_lattice(self, evaluations: list[dict[str, Any]]) -> dict[str, Any]:
        candidate_map = {candidate.candidate_id: candidate for candidate in self.scenario.candidates}
        subset_edges: list[dict[str, str]] = []
        equivalent_edges: list[dict[str, str]] = []
        lineage_edges: list[dict[str, str]] = []
        dominance_edges: list[dict[str, str]] = []

        for left in evaluations:
            left_candidate = candidate_map[left["candidate_id"]]
            parent = left_candidate.lineage.get("parent")
            if parent and parent in candidate_map:
                lineage_edges.append(
                    {
                        "from": str(parent),
                        "to": left_candidate.candidate_id,
                        "relation": str(left_candidate.lineage.get("relation", "successor")),
                    }
                )
            for right in evaluations:
                if left["candidate_id"] == right["candidate_id"]:
                    continue
                right_candidate = candidate_map[right["candidate_id"]]
                if set(left_candidate.components) < set(right_candidate.components):
                    subset_edges.append(
                        {"from": left_candidate.candidate_id, "to": right_candidate.candidate_id, "relation": "component_subset"}
                    )
                if (
                    left["prediction_signature_sha256"] == right["prediction_signature_sha256"]
                    and left_candidate.scope_worlds == right_candidate.scope_worlds
                    and left_candidate.candidate_id < right_candidate.candidate_id
                ):
                    equivalent_edges.append(
                        {"from": left_candidate.candidate_id, "to": right_candidate.candidate_id, "relation": "observationally_equivalent"}
                    )
                if self._dominates(left, right):
                    dominance_edges.append(
                        {"from": left_candidate.candidate_id, "to": right_candidate.candidate_id, "relation": "pareto_dominates"}
                    )

        # Remove exact duplicate edges while retaining deterministic order.
        def dedupe(items: list[dict[str, str]]) -> list[dict[str, str]]:
            seen: set[tuple[str, str, str]] = set()
            result: list[dict[str, str]] = []
            for item in sorted(items, key=lambda x: (x["from"], x["to"], x["relation"])):
                key = (item["from"], item["to"], item["relation"])
                if key not in seen:
                    seen.add(key)
                    result.append(item)
            return result

        dominated = {edge["to"] for edge in dominance_edges}
        pareto_frontier = sorted(item["candidate_id"] for item in evaluations if item["candidate_id"] not in dominated)
        return {
            "nodes": [
                {
                    "candidate_id": item["candidate_id"],
                    "components": item["components"],
                    "status": item["status"],
                    "essence_level": item["essence_level"],
                }
                for item in sorted(evaluations, key=lambda x: x["candidate_id"])
            ],
            "subset_edges": dedupe(subset_edges),
            "equivalence_edges": dedupe(equivalent_edges),
            "lineage_edges": dedupe(lineage_edges),
            "dominance_edges": dedupe(dominance_edges),
            "pareto_frontier": pareto_frontier,
        }

    def evaluate(self) -> dict[str, Any]:
        evaluations = [self.evaluate_candidate(candidate) for candidate in self.scenario.candidates]
        lattice = self.build_lattice(evaluations)
        certified = [item for item in evaluations if item["local_certifiable"]]
        if certified:
            minimum_components = min(item["component_count"] for item in certified)
            selected = sorted(item["candidate_id"] for item in certified if item["component_count"] == minimum_components)
            local_status = "LOCAL_ESSENCE_CERTIFIED"
        else:
            selected = []
            local_status = "NO_LOCAL_ESSENCE_CERTIFIED"

        formal_closed = bool(self.scenario.scope.get("formal_closed_exhaustive", False))
        no_open_residuals = not any(item.get("status", "open") == "open" for item in self.scenario.residuals)
        if formal_closed and selected and no_open_residuals:
            ultimate_status = "FORMAL_ESSENCE_COMPLETE_WITHIN_ENUMERATED_WORLD"
        else:
            ultimate_status = "ULTIMATE_ESSENCE_NOT_ESTABLISHED"

        return {
            "candidate_evaluations": evaluations,
            "essence_lattice": lattice,
            "selected_candidate_ids": selected,
            "local_essence_status": local_status,
            "ultimate_essence_status": ultimate_status,
            "selection_rule": {
                "hard_filter": [
                    "complete required predictions",
                    "declared contrasts preserved",
                    "all components ablation-tested and necessary",
                    "reverse regeneration complete",
                    "falsification conditions declared before evaluation",
                    "no wildcard or post-failure scope escape",
                    "no declared blocking residual",
                ],
                "tie_rule": "retain all minimum-component certified candidates; do not force a single ontology",
                "aggregate_score_used": False,
            },
        }
