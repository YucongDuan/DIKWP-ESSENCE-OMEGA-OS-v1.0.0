from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from essence_omega_os.engine import EssenceOmegaEngine, write_run_outputs
from essence_omega_os.ledger import HashLedger

ROOT = Path(__file__).resolve().parents[1]


def load_example(name: str = "01_minimal_causal_kernel.json") -> dict:
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


class EngineTests(unittest.TestCase):
    def test_engine_run_is_deterministic(self):
        first = EssenceOmegaEngine(load_example()).run()
        second = EssenceOmegaEngine(load_example()).run()
        self.assertEqual(first["run_hash"], second["run_hash"])

    def test_engine_has_ten_ledger_events(self):
        engine = EssenceOmegaEngine(load_example())
        engine.run()
        self.assertEqual(len(engine.ledger.records), 10)

    def test_semantic_graph_supports_25_routes(self):
        result = EssenceOmegaEngine(load_example()).run()
        self.assertEqual(len(result["semantic_graph"]["supported_route_types"]), 25)

    def test_semantic_graph_has_five_native_records(self):
        result = EssenceOmegaEngine(load_example()).run()
        self.assertEqual(result["semantic_graph"]["closure_vector"], "11111")
        self.assertEqual(len(result["semantic_graph"]["records"]), 5)

    def test_external_action_authority_is_zero(self):
        result = EssenceOmegaEngine(load_example()).run()
        self.assertEqual(result["automatic_external_action_authority"], 0)
        self.assertEqual(result["certificate"]["status_vector"]["automatic_external_action_authority"], 0)

    def test_ultimate_ontology_not_established(self):
        result = EssenceOmegaEngine(load_example()).run()
        self.assertEqual(result["certificate"]["status_vector"]["ultimate_ontology"], "NOT_ESTABLISHED")

    def test_write_outputs_creates_expected_files(self):
        engine = EssenceOmegaEngine(load_example())
        result = engine.run()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            summary = write_run_outputs(output, engine, result)
            expected = {
                "result.json",
                "essence_certificate.json",
                "essence_lattice.json",
                "candidate_evaluations.json",
                "semantic_graph.json",
                "residual_frontier.json",
                "probe_plan.json",
                "causal_handoff.json",
                "counterfactual_ablation_matrix.csv",
                "report.en.md",
                "report.zh-CN.md",
                "evidence_ledger.jsonl",
                "output_manifest.json",
            }
            self.assertTrue(expected.issubset({path.name for path in output.iterdir()}))
            self.assertEqual(summary["artifact_count"], 13)

    def test_written_ledger_verifies(self):
        engine = EssenceOmegaEngine(load_example())
        result = engine.run()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_run_outputs(output, engine, result)
            valid, errors, records = HashLedger.read_and_verify(output / "evidence_ledger.jsonl")
            self.assertTrue(valid)
            self.assertEqual(errors, [])
            self.assertEqual(len(records), 10)

    def test_manifest_has_merkle_root(self):
        engine = EssenceOmegaEngine(load_example())
        result = engine.run()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_run_outputs(output, engine, result)
            manifest = json.loads((output / "output_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["merkle_root"]), 64)
            self.assertEqual(manifest["run_hash"], result["run_hash"])

    def test_certificate_hash_is_stable(self):
        first = EssenceOmegaEngine(load_example()).run()["certificate"]["certificate_sha256"]
        second = EssenceOmegaEngine(load_example()).run()["certificate"]["certificate_sha256"]
        self.assertEqual(first, second)

    def test_plural_example_proposes_safe_probe(self):
        result = EssenceOmegaEngine(load_example("08_plural_incomparable_essences.json")).run()
        self.assertEqual(result["probe_plan"]["selected_probe_id"], "P_PATH_PERTURBATION")

    def test_destructive_probe_is_filtered(self):
        result = EssenceOmegaEngine(load_example("08_plural_incomparable_essences.json")).run()
        item = next(p for p in result["probe_plan"]["evaluated_probes"] if p["probe_id"] == "P_DESTRUCTIVE_INTERNAL_EDIT")
        self.assertFalse(item["hard_filter_passed"])


if __name__ == "__main__":
    unittest.main()
