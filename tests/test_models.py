from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from essence_omega_os.models import ScenarioError, ScenarioSpec

ROOT = Path(__file__).resolve().parents[1]


def example() -> dict:
    return json.loads((ROOT / "examples" / "01_minimal_causal_kernel.json").read_text(encoding="utf-8"))


class ScenarioValidationTests(unittest.TestCase):
    def test_valid_example_loads(self):
        scenario = ScenarioSpec.from_dict(example())
        self.assertEqual(scenario.scenario_id, "minimal-causal-kernel")

    def test_missing_scenario_id_rejected(self):
        data = example()
        data.pop("scenario_id")
        with self.assertRaises(ScenarioError):
            ScenarioSpec.from_dict(data)

    def test_missing_tests_rejected(self):
        data = example()
        data["tests"] = []
        with self.assertRaises(ScenarioError):
            ScenarioSpec.from_dict(data)

    def test_missing_worlds_rejected(self):
        data = example()
        data["worlds"] = []
        with self.assertRaises(ScenarioError):
            ScenarioSpec.from_dict(data)

    def test_missing_candidates_rejected(self):
        data = example()
        data["candidates"] = []
        with self.assertRaises(ScenarioError):
            ScenarioSpec.from_dict(data)

    def test_duplicate_test_ids_rejected(self):
        data = example()
        data["tests"].append(copy.deepcopy(data["tests"][0]))
        with self.assertRaises(ScenarioError):
            ScenarioSpec.from_dict(data)

    def test_duplicate_world_ids_rejected(self):
        data = example()
        data["worlds"].append(copy.deepcopy(data["worlds"][0]))
        with self.assertRaises(ScenarioError):
            ScenarioSpec.from_dict(data)

    def test_unknown_world_observation_rejected(self):
        data = example()
        data["worlds"][0]["observations"]["UNKNOWN"] = "x"
        with self.assertRaises(ScenarioError):
            ScenarioSpec.from_dict(data)

    def test_unknown_candidate_scope_world_rejected(self):
        data = example()
        data["candidates"][0]["scope_worlds"].append("UNKNOWN")
        with self.assertRaises(ScenarioError):
            ScenarioSpec.from_dict(data)

    def test_nonzero_external_authority_rejected(self):
        data = example()
        data["purpose"]["automatic_external_action_authority"] = 1
        with self.assertRaises(ScenarioError):
            ScenarioSpec.from_dict(data)

    def test_empty_candidate_scope_defaults_to_all_worlds(self):
        data = example()
        data["candidates"][0]["scope_worlds"] = []
        scenario = ScenarioSpec.from_dict(data)
        self.assertEqual(set(scenario.candidates[0].scope_worlds), {item.world_id for item in scenario.worlds})

    def test_duplicate_components_rejected(self):
        data = example()
        data["candidates"][0]["components"] = ["x", "x"]
        with self.assertRaises(ScenarioError):
            ScenarioSpec.from_dict(data)

    def test_unknown_contrast_world_rejected(self):
        data = example()
        data["contrasts"][0]["world_a"] = "UNKNOWN"
        with self.assertRaises(ScenarioError):
            ScenarioSpec.from_dict(data)

    def test_unknown_test_kind_rejected(self):
        data = example()
        data["tests"][0]["kind"] = "magic"
        with self.assertRaises(ScenarioError):
            ScenarioSpec.from_dict(data)


if __name__ == "__main__":
    unittest.main()
