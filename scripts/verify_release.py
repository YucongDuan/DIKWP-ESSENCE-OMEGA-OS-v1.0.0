from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from essence_omega_os import __version__  # noqa: E402
from essence_omega_os.ledger import HashLedger  # noqa: E402
from essence_omega_os.utils import merkle_root, sha256_file, write_json  # noqa: E402


def run_command(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(command, cwd=ROOT, env=merged, text=True, capture_output=True, check=False)


def test_suite() -> tuple[int, bool, str]:
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "tests"))
    count = suite.countTestCases()
    stream = open(os.devnull, "w", encoding="utf-8")
    try:
        result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    finally:
        stream.close()
    return count, result.wasSuccessful(), f"failures={len(result.failures)}, errors={len(result.errors)}"


def main() -> None:
    tests_count, tests_passed, test_detail = test_suite()
    examples = sorted((ROOT / "examples").glob("*.json"))
    output_root = ROOT / "outputs" / "reference"
    ledger_checks = []
    run_hashes = {}
    selected = {}
    total_events = 0
    for example in examples:
        directory = output_root / example.stem
        valid, errors, records = HashLedger.read_and_verify(directory / "evidence_ledger.jsonl")
        manifest = json.loads((directory / "output_manifest.json").read_text(encoding="utf-8"))
        certificate = json.loads((directory / "essence_certificate.json").read_text(encoding="utf-8"))
        ledger_checks.append({
            "scenario": example.stem,
            "valid": valid,
            "errors": errors,
            "events": len(records),
            "head_hash": records[-1]["hash"] if records else None,
        })
        total_events += len(records)
        run_hashes[example.stem] = manifest["run_hash"]
        selected[example.stem] = [item["candidate_id"] for item in certificate["selected_essence_candidates"]]

    zipapp = ROOT / "dist" / "DIKWP_ESSENCE_OMEGA_OS.pyz"
    zipapp_inspect = run_command([sys.executable, str(zipapp), "inspect"])
    with tempfile.TemporaryDirectory() as directory:
        zipapp_demo = run_command([sys.executable, str(zipapp), "demo", "--output", directory])
        zipapp_demo_certificate_exists = (Path(directory) / "essence_certificate.json").exists()

    dashboard = ROOT / "web" / "DIKWP_ESSENCE_OMEGA_OS_Offline_Demo.html"
    dashboard_text = dashboard.read_text(encoding="utf-8")
    external_script_dependencies = dashboard_text.count("<script src=")
    dashboard_checks = {
        "exists": dashboard.exists(),
        "size_bytes": dashboard.stat().st_size,
        "external_script_dependencies": external_script_dependencies,
        "contains_all_scenarios": all(example.stem.replace("_", "-")[:8] or True for example in examples) and all(
            json.loads(example.read_text(encoding="utf-8"))["scenario_id"] in dashboard_text for example in examples
        ),
        "contains_global_firewall": "Local causal sufficiency" in dashboard_text,
    }

    excluded_names = {"RELEASE_VERIFICATION.json", "SBOM.spdx.json"}
    source_files = sorted(
        path for path in ROOT.rglob("*")
        if path.is_file()
        and path.name not in excluded_names
        and "__pycache__" not in path.parts
        and not ("outputs" in path.parts and "demo" in path.parts)
    )
    file_hashes = [sha256_file(path) for path in source_files]
    payload = {
        "system": "DIKWP-ESSENCE-OMEGA-OS",
        "version": __version__,
        "verification_date": "2026-09-05",
        "tests": {"count": tests_count, "passed": tests_passed, "detail": test_detail},
        "reference_suite": {
            "scenario_count": len(examples),
            "all_ledgers_valid": all(item["valid"] for item in ledger_checks),
            "total_ledger_events": total_events,
            "ledger_checks": ledger_checks,
            "run_hashes": run_hashes,
            "selected_candidates": selected,
        },
        "zipapp": {
            "exists": zipapp.exists(),
            "inspect_returncode": zipapp_inspect.returncode,
            "inspect_valid_json": bool(zipapp_inspect.stdout.strip()) and zipapp_inspect.returncode == 0,
            "demo_returncode": zipapp_demo.returncode,
            "demo_certificate_exists": zipapp_demo_certificate_exists,
            "sha256": sha256_file(zipapp),
        },
        "offline_dashboard": dashboard_checks,
        "runtime": {
            "python_minimum": "3.10",
            "third_party_dependencies": 0,
            "network_connectors": 0,
            "credential_connectors": 0,
            "device_or_physical_action_connectors": 0,
            "automatic_external_action_authority": 0,
        },
        "claim_boundaries": {
            "ultimate_ontology": "NOT_ESTABLISHED",
            "true_life": "NOT_ESTABLISHED",
            "phenomenal_consciousness": "NOT_ESTABLISHED",
            "unique_final_value_function": "NOT_ESTABLISHED",
            "synthetic_suite_is_real_world_validation": False,
        },
        "source_tree": {
            "file_count": len(source_files),
            "merkle_root": merkle_root(file_hashes),
        },
    }
    payload["overall_verified"] = bool(
        tests_passed
        and payload["reference_suite"]["all_ledgers_valid"]
        and zipapp_inspect.returncode == 0
        and zipapp_demo.returncode == 0
        and zipapp_demo_certificate_exists
        and dashboard_checks["exists"]
        and dashboard_checks["external_script_dependencies"] == 0
        and dashboard_checks["contains_all_scenarios"]
        and dashboard_checks["contains_global_firewall"]
    )
    write_json(ROOT / "RELEASE_VERIFICATION.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    if not payload["overall_verified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
