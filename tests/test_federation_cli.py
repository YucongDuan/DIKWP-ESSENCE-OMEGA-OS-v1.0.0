from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from essence_omega_os.cli import main
from essence_omega_os.engine import EssenceOmegaEngine, write_run_outputs
from essence_omega_os.federation import federate_certificates

ROOT = Path(__file__).resolve().parents[1]


def certificate(name: str) -> dict:
    data = json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))
    return EssenceOmegaEngine(data).run()["certificate"]


class FederationTests(unittest.TestCase):
    def test_requires_certificate(self):
        with self.assertRaises(ValueError):
            federate_certificates([])

    def test_federation_preserves_local_rows(self):
        result = federate_certificates([
            certificate("01_minimal_causal_kernel.json"),
            certificate("02_essence_split_after_counterexample.json"),
        ])
        self.assertEqual(len(result["certificates"]), 2)

    def test_federation_does_not_claim_global_essence(self):
        result = federate_certificates([
            certificate("01_minimal_causal_kernel.json"),
            certificate("03_cross_carrier_refusal.json"),
        ])
        self.assertIn("not a final global essence", result["boundary"])
        self.assertEqual(result["automatic_external_action_authority"], 0)

    def test_shared_component_core_can_be_empty(self):
        result = federate_certificates([
            certificate("01_minimal_causal_kernel.json"),
            certificate("03_cross_carrier_refusal.json"),
        ])
        self.assertEqual(result["status"], "NO_SHARED_COMPONENT_CORE")


class CliTests(unittest.TestCase):
    def test_inspect_command(self):
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            code = main(["inspect"])
        self.assertEqual(code, 0)
        payload = json.loads(capture.getvalue())
        self.assertEqual(payload["external_action_authority"], 0)

    def test_demo_command(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                code = main(["demo", "--output", directory])
            self.assertEqual(code, 0)
            self.assertTrue((Path(directory) / "essence_certificate.json").exists())

    def test_run_command(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                code = main([
                    "run",
                    str(ROOT / "examples" / "07_anti_self_sealing.json"),
                    "--output",
                    directory,
                ])
            self.assertEqual(code, 0)
            payload = json.loads(capture.getvalue())
            self.assertEqual(payload["selected_candidate_ids"], ["E_BOUNDED_CAUSE"])

    def test_verify_command(self):
        data = json.loads((ROOT / "examples" / "01_minimal_causal_kernel.json").read_text(encoding="utf-8"))
        engine = EssenceOmegaEngine(data)
        result = engine.run()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_run_outputs(output, engine, result)
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                code = main(["verify", str(output / "evidence_ledger.jsonl")])
            self.assertEqual(code, 0)
            payload = json.loads(capture.getvalue())
            self.assertTrue(payload["valid"])

    def test_compare_command(self):
        left = certificate("01_minimal_causal_kernel.json")
        right = certificate("02_essence_split_after_counterexample.json")
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            left_path = directory / "left.json"
            right_path = directory / "right.json"
            left_path.write_text(json.dumps(left), encoding="utf-8")
            right_path.write_text(json.dumps(right), encoding="utf-8")
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                code = main(["compare", str(left_path), str(right_path)])
            self.assertEqual(code, 0)
            payload = json.loads(capture.getvalue())
            self.assertTrue(payload["selected_only_left"])
            self.assertTrue(payload["selected_only_right"])

    def test_federate_command(self):
        left = certificate("01_minimal_causal_kernel.json")
        right = certificate("03_cross_carrier_refusal.json")
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            left_path = directory / "left.json"
            right_path = directory / "right.json"
            output = directory / "federation.json"
            left_path.write_text(json.dumps(left), encoding="utf-8")
            right_path.write_text(json.dumps(right), encoding="utf-8")
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                code = main(["federate", str(left_path), str(right_path), "--output", str(output)])
            self.assertEqual(code, 0)
            self.assertTrue(output.exists())
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["automatic_external_action_authority"], 0)


if __name__ == "__main__":
    unittest.main()
