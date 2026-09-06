from __future__ import annotations

import json
import unittest
from pathlib import Path

from essence_omega_os.essence import EssenceEvaluator
from essence_omega_os.models import ScenarioSpec

ROOT = Path(__file__).resolve().parents[1]


def evaluate(name: str) -> dict:
    data = json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))
    return EssenceEvaluator(ScenarioSpec.from_dict(data)).evaluate()


def by_id(result: dict, candidate_id: str) -> dict:
    return next(item for item in result["candidate_evaluations"] if item["candidate_id"] == candidate_id)


class EvaluatorTests(unittest.TestCase):
    def test_minimal_kernel_selected(self):
        result = evaluate("01_minimal_causal_kernel.json")
        self.assertEqual(result["selected_candidate_ids"], ["E_FEEDBACK_GATE"])

    def test_overcomplete_candidate_detected(self):
        result = evaluate("01_minimal_causal_kernel.json")
        item = by_id(result, "E_OVERCOMPLETE")
        self.assertEqual(item["status"], "OVERCOMPLETE_NONMINIMAL")
        self.assertIn("casing_colour", item["minimality_result"]["redundant_components"])

    def test_correlation_candidate_falsified(self):
        result = evaluate("01_minimal_causal_kernel.json")
        item = by_id(result, "E_CLOCK_CORRELATION")
        self.assertEqual(item["status"], "INSUFFICIENT_OR_FALSIFIED")
        self.assertLess(item["metrics"]["fidelity"], 1.0)

    def test_hysteresis_successor_selected(self):
        result = evaluate("02_essence_split_after_counterexample.json")
        self.assertEqual(result["selected_candidate_ids"], ["E_HYSTERESIS"])
        self.assertTrue(result["essence_lattice"]["lineage_edges"])

    def test_surface_token_rejected_by_outcomes(self):
        result = evaluate("03_cross_carrier_refusal.json")
        item = by_id(result, "E_LITERAL_TOKEN")
        self.assertFalse(item["local_certifiable"])
        self.assertEqual(result["selected_candidate_ids"], ["E_REFUSAL_CORE"])

    def test_normative_violation_blocks_bare_action(self):
        result = evaluate("04_normative_essence_and_permission.json")
        item = by_id(result, "E_BARE_ACTUATION")
        self.assertEqual(item["status"], "INSUFFICIENT_OR_FALSIFIED")
        self.assertFalse(item["normative_result"]["passed"])
        self.assertEqual(result["selected_candidate_ids"], ["E_LEGITIMATE_ACTION"])

    def test_reduction_is_local_not_ultimate(self):
        result = evaluate("05_reduction_is_not_proof.json")
        self.assertEqual(result["selected_candidate_ids"], ["E_FINITE_REDUCTION"])
        self.assertEqual(result["ultimate_essence_status"], "ULTIMATE_ESSENCE_NOT_ESTABLISHED")

    def test_overclaim_is_self_sealing(self):
        result = evaluate("05_reduction_is_not_proof.json")
        item = by_id(result, "E_GLOBAL_OVERCLAIM")
        self.assertEqual(item["status"], "SELF_SEALING_REJECTED")
        self.assertGreaterEqual(len(item["self_sealing_reasons"]), 2)

    def test_operational_continuity_selected(self):
        result = evaluate("06_operational_continuity_not_consciousness.json")
        self.assertEqual(result["selected_candidate_ids"], ["E_OPERATIONAL_CONTINUITY"])

    def test_phenomenal_residual_does_not_become_fact(self):
        result = evaluate("06_operational_continuity_not_consciousness.json")
        item = by_id(result, "E_OPERATIONAL_CONTINUITY")
        types = {residual["type"] for residual in item["residual_result"]["items"]}
        self.assertIn("phenomenal", types)

    def test_all_explaining_candidate_rejected(self):
        result = evaluate("07_anti_self_sealing.json")
        item = by_id(result, "E_ALL_EXPLAINING")
        self.assertEqual(item["status"], "SELF_SEALING_REJECTED")
        self.assertGreater(item["metrics"]["wildcard_rate"], 0)

    def test_plural_candidates_retained(self):
        result = evaluate("08_plural_incomparable_essences.json")
        self.assertEqual(result["selected_candidate_ids"], ["E_DYNAMICAL", "E_SYMBOLIC"])

    def test_observational_equivalence_edge_present(self):
        result = evaluate("08_plural_incomparable_essences.json")
        self.assertEqual(len(result["essence_lattice"]["equivalence_edges"]), 1)

    def test_selection_does_not_use_aggregate_score(self):
        result = evaluate("01_minimal_causal_kernel.json")
        self.assertFalse(result["selection_rule"]["aggregate_score_used"])

    def test_certified_candidate_reaches_level_five(self):
        result = evaluate("01_minimal_causal_kernel.json")
        item = by_id(result, "E_FEEDBACK_GATE")
        self.assertEqual(item["essence_level"], "L5_REVERSIBLE_GENERATIVE_ESSENCE")

    def test_every_component_is_necessary_for_selected_core(self):
        result = evaluate("01_minimal_causal_kernel.json")
        item = by_id(result, "E_FEEDBACK_GATE")
        self.assertTrue(item["minimality_result"]["all_components_necessary"])


if __name__ == "__main__":
    unittest.main()
