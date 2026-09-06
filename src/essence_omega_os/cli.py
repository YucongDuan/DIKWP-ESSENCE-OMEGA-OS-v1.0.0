from __future__ import annotations

import argparse
import json
import sys
from importlib import resources
from pathlib import Path
from typing import Any

from . import __version__
from .engine import EssenceOmegaEngine, ScenarioError, write_run_outputs
from .federation import federate_certificates
from .ledger import HashLedger
from .utils import read_json


def _project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "examples").exists() and (parent / "src").exists():
            return parent
    return Path.cwd()


def _packaged_example_names() -> list[str]:
    root = resources.files("essence_omega_os").joinpath("data", "examples")
    return sorted(item.name for item in root.iterdir() if item.name.endswith(".json"))


def _packaged_example(name: str) -> dict[str, Any]:
    text = resources.files("essence_omega_os").joinpath("data", "examples", name).read_text(encoding="utf-8")
    return json.loads(text)


def run_scenario_data(data: dict[str, Any], output: Path, source: str) -> dict[str, Any]:
    engine = EssenceOmegaEngine(data)
    result = engine.run()
    summary = write_run_outputs(output, engine, result)
    summary["scenario_source"] = source
    return summary


def run_scenario(path: Path, output: Path) -> dict[str, Any]:
    return run_scenario_data(read_json(path), output, str(path))


def command_run(args: argparse.Namespace) -> int:
    try:
        summary = run_scenario(Path(args.scenario), Path(args.output))
    except (OSError, ValueError, ScenarioError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_demo(args: argparse.Namespace) -> int:
    root = _project_root()
    local = root / "examples" / "01_minimal_causal_kernel.json"
    try:
        if local.exists():
            summary = run_scenario(local, Path(args.output))
        else:
            summary = run_scenario_data(
                _packaged_example("01_minimal_causal_kernel.json"),
                Path(args.output),
                "package:data/examples/01_minimal_causal_kernel.json",
            )
    except (OSError, ValueError, ScenarioError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_suite(args: argparse.Namespace) -> int:
    examples_dir = Path(args.examples)
    output_root = Path(args.output)
    if examples_dir.exists():
        items = [(path.name, read_json(path), str(path)) for path in sorted(examples_dir.glob("*.json"))]
    elif args.examples == "examples":
        items = [(name, _packaged_example(name), f"package:data/examples/{name}") for name in _packaged_example_names()]
    else:
        print(f"ERROR: examples directory not found: {examples_dir}", file=sys.stderr)
        return 2
    runs: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for name, data, source in items:
        try:
            runs.append(run_scenario_data(data, output_root / Path(name).stem, source))
        except Exception as exc:  # individual scenarios are isolated at the CLI boundary
            failures.append({"scenario": source, "error": str(exc)})
    print(json.dumps({"version": __version__, "runs": runs, "failures": failures}, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if failures else 0


def command_verify(args: argparse.Namespace) -> int:
    try:
        valid, errors, records = HashLedger.read_and_verify(Path(args.ledger))
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    payload = {
        "valid": valid,
        "record_count": len(records),
        "head_hash": records[-1]["hash"] if records else None,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if valid else 1


def command_inspect(args: argparse.Namespace) -> int:
    payload = {
        "system": "DIKWP-ESSENCE-OMEGA-OS",
        "version": __version__,
        "essence_definition": "minimum causal-generative invariant that survives declared transformations, passes ablation, transports across declared worlds, and reverse-regenerates registered consequences",
        "five_levels": [
            "L1 partial description",
            "L2 predictive core",
            "L3 causal-minimal core",
            "L4 cross-world core",
            "L5 reversible-generative essence",
        ],
        "ultimate_boundary": "local certification never self-authorizes final metaphysical ontology",
        "selection": "hard constraints + ablation necessity + plural minimum-component retention; no aggregate score",
        "external_action_authority": 0,
        "examples": _packaged_example_names(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_compare(args: argparse.Namespace) -> int:
    try:
        left = read_json(Path(args.left))
        right = read_json(Path(args.right))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    left_ids = {item["candidate_id"] for item in left.get("selected_essence_candidates", [])}
    right_ids = {item["candidate_id"] for item in right.get("selected_essence_candidates", [])}
    payload = {
        "left_certificate": left.get("certificate_id"),
        "right_certificate": right.get("certificate_id"),
        "selected_only_left": sorted(left_ids - right_ids),
        "selected_only_right": sorted(right_ids - left_ids),
        "selected_in_both": sorted(left_ids & right_ids),
        "ultimate_status_changed": left.get("ultimate_essence_status") != right.get("ultimate_essence_status"),
        "residual_frontier_changed": left.get("residual_frontier") != right.get("residual_frontier"),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0



def command_federate(args: argparse.Namespace) -> int:
    try:
        certificates = [read_json(Path(path)) for path in args.certificates]
        payload = federate_certificates(certificates)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"output": str(output), "federation_id": payload["federation_id"], "status": payload["status"]}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dikwp-essence-omega",
        description="Open ultimate-essence runtime for minimal causal-generative invariants and residual frontiers",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="evaluate one declared scenario")
    run.add_argument("scenario")
    run.add_argument("--output", required=True)
    run.set_defaults(func=command_run)

    demo = sub.add_parser("demo", help="run the packaged minimal causal-kernel example")
    demo.add_argument("--output", default="outputs/demo")
    demo.set_defaults(func=command_demo)

    suite = sub.add_parser("suite", help="run all scenarios in a directory or the packaged suite")
    suite.add_argument("--examples", default="examples")
    suite.add_argument("--output", default="outputs/reference")
    suite.set_defaults(func=command_suite)

    verify = sub.add_parser("verify", help="verify a hash-chained evidence ledger")
    verify.add_argument("ledger")
    verify.set_defaults(func=command_verify)

    inspect = sub.add_parser("inspect", help="print the runtime contract")
    inspect.set_defaults(func=command_inspect)

    compare = sub.add_parser("compare", help="compare two bounded essence certificates")
    compare.add_argument("left")
    compare.add_argument("right")
    compare.set_defaults(func=command_compare)

    federate = sub.add_parser("federate", help="build a non-annexing federation of bounded certificates")
    federate.add_argument("certificates", nargs="+")
    federate.add_argument("--output", required=True)
    federate.set_defaults(func=command_federate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
