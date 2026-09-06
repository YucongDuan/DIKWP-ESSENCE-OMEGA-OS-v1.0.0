from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from typing import Any

from . import __version__
from .certificates import build_certificate, build_residual_frontier
from .essence import EssenceEvaluator
from .ledger import HashLedger
from .models import ScenarioError, ScenarioSpec
from .probes import plan_probes
from .semantics import build_semantic_graph
from .utils import canonical_json, merkle_root, sha256_file, sha256_text, write_json, write_text


class EssenceOmegaEngine:
    def __init__(self, scenario_data: dict[str, Any]):
        self.scenario = ScenarioSpec.from_dict(scenario_data)
        self.ledger = HashLedger()

    def run(self) -> dict[str, Any]:
        scenario = self.scenario
        self.ledger.append(
            "scenario_registered",
            {
                "scenario_id": scenario.scenario_id,
                "scope": scenario.scope,
                "purpose_owner": scenario.purpose.get("owner", "unnamed"),
                "automatic_external_action_authority": 0,
            },
            stage="01_CONTRACT",
        )
        self.ledger.append(
            "world_family_registered",
            {
                "worlds": [
                    {
                        "world_id": world.world_id,
                        "carrier": world.carrier,
                        "environment": world.environment,
                        "observation_count": len(world.observations),
                    }
                    for world in scenario.worlds
                ],
                "test_ids": [test.test_id for test in scenario.tests],
            },
            stage="02_WORLD_FAMILY",
        )
        self.ledger.append(
            "candidate_family_registered",
            {
                "candidate_ids": [candidate.candidate_id for candidate in scenario.candidates],
                "component_sets": {
                    candidate.candidate_id: candidate.components for candidate in scenario.candidates
                },
            },
            stage="03_CANDIDATES",
        )

        evaluation = EssenceEvaluator(scenario).evaluate()
        self.ledger.append(
            "candidate_evaluation_completed",
            {
                "statuses": {
                    item["candidate_id"]: item["status"] for item in evaluation["candidate_evaluations"]
                },
                "selected_candidate_ids": evaluation["selected_candidate_ids"],
            },
            stage="04_FALSIFICATION_ABLATION",
        )
        self.ledger.append(
            "essence_lattice_constructed",
            {
                "node_count": len(evaluation["essence_lattice"]["nodes"]),
                "pareto_frontier": evaluation["essence_lattice"]["pareto_frontier"],
                "subset_edges": len(evaluation["essence_lattice"]["subset_edges"]),
                "lineage_edges": len(evaluation["essence_lattice"]["lineage_edges"]),
            },
            stage="05_ESSENCE_LATTICE",
        )

        probe_plan = plan_probes(scenario.raw, evaluation["candidate_evaluations"])
        self.ledger.append(
            "reality_probe_plan_generated",
            {
                "status": probe_plan["status"],
                "selected_probe_id": probe_plan["selected_probe_id"],
                "evaluated_probe_count": len(probe_plan["evaluated_probes"]),
                "automatic_external_action_authority": 0,
            },
            stage="06_REALITY_PROBE",
        )

        semantic_graph = build_semantic_graph(scenario, evaluation)
        self.ledger.append(
            "dikwp_semantic_graph_generated",
            {
                "closure_vector": semantic_graph["closure_vector"],
                "record_ids": [item["record_id"] for item in semantic_graph["records"]],
                "actual_route_count": len(semantic_graph["routes"]),
                "supported_route_types": len(semantic_graph["supported_route_types"]),
            },
            stage="07_SEMANTIC_REGENERATION",
        )

        residual_frontier = build_residual_frontier(scenario)
        self.ledger.append(
            "residual_frontier_registered",
            {
                "frontier_status": residual_frontier["frontier_status"],
                "open_residual_ids": [
                    str(item.get("residual_id", "unnamed")) for item in residual_frontier["open_items"]
                ],
                "type_counts": residual_frontier["type_counts"],
            },
            stage="08_RESIDUAL_FRONTIER",
        )
        self.ledger.append(
            "causal_handoff_registered",
            {
                "owner": scenario.handoff.get("owner", scenario.purpose.get("owner", "unnamed")),
                "next_action": scenario.handoff.get("next_action", "none declared"),
                "kill_conditions": scenario.handoff.get("kill_conditions", []),
            },
            stage="09_HANDOFF",
        )

        certificate = build_certificate(
            scenario,
            evaluation,
            semantic_graph,
            residual_frontier,
            probe_plan,
            self.ledger.head_hash,
            __version__,
        )
        self.ledger.append(
            "bounded_essence_certificate_issued",
            {
                "certificate_id": certificate["certificate_id"],
                "certificate_sha256": certificate["certificate_sha256"],
                "local_status": certificate["local_essence_status"],
                "ultimate_status": certificate["ultimate_essence_status"],
                "selected_candidate_ids": evaluation["selected_candidate_ids"],
            },
            stage="10_CERTIFICATE",
        )

        run_core = {
            "system": "DIKWP-ESSENCE-OMEGA-OS",
            "version": __version__,
            "scenario_id": scenario.scenario_id,
            "evaluation": evaluation,
            "semantic_graph": semantic_graph,
            "residual_frontier": residual_frontier,
            "probe_plan": probe_plan,
            "certificate_sha256": certificate["certificate_sha256"],
            "ledger_head_hash": self.ledger.head_hash,
        }
        run_hash = sha256_text(canonical_json(run_core))
        return {
            **run_core,
            "certificate": certificate,
            "run_hash": run_hash,
            "automatic_external_action_authority": 0,
        }


def _counterfactual_csv(evaluation: dict[str, Any]) -> str:
    output = StringIO()
    fieldnames = [
        "candidate_id",
        "component",
        "tested",
        "necessary",
        "failed_world",
        "failed_test",
        "observed",
        "ablated_prediction",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for candidate in evaluation["candidate_evaluations"]:
        for item in candidate["minimality_result"]["component_results"]:
            failures = item["failed_cells"] or [{}]
            for failure in failures:
                writer.writerow(
                    {
                        "candidate_id": candidate["candidate_id"],
                        "component": item["component"],
                        "tested": item["tested"],
                        "necessary": item["necessary"],
                        "failed_world": failure.get("world_id", ""),
                        "failed_test": failure.get("test_id", ""),
                        "observed": failure.get("observed", ""),
                        "ablated_prediction": failure.get("ablated_prediction", ""),
                    }
                )
    return output.getvalue()


def _report_en(engine: EssenceOmegaEngine, result: dict[str, Any]) -> str:
    scenario = engine.scenario
    selected = result["evaluation"]["selected_candidate_ids"]
    lines = [
        f"# {scenario.title_en}",
        "",
        "## Bounded result",
        "",
        f"- Scenario: `{scenario.scenario_id}`",
        f"- Local essence status: **{result['evaluation']['local_essence_status']}**",
        f"- Ultimate essence status: **{result['evaluation']['ultimate_essence_status']}**",
        f"- Selected candidates: {', '.join(selected) if selected else 'none'}",
        f"- Run hash: `{result['run_hash']}`",
        "- Automatic external action authority: `0`",
        "",
        "## Interpretation",
        "",
        "The runtime uses the word *essence* operationally: the smallest declared causal-generative invariant that survives the registered transformations, requires every retained component under ablation, transports across the stated world family, and reverse-regenerates the declared consequences. It does not infer a final metaphysical substance from local success.",
        "",
        "## Candidate results",
        "",
        "| Candidate | Status | Level | Components | Fidelity | Reverse |",
        "|---|---|---|---:|---:|---:|",
    ]
    for item in result["evaluation"]["candidate_evaluations"]:
        lines.append(
            f"| {item['candidate_id']} | {item['status']} | {item['essence_level']} | {item['component_count']} | {item['metrics']['fidelity']:.3f} | {item['metrics']['reverse_regeneration']:.3f} |"
        )
    lines.extend(["", "## Residual frontier", ""])
    if result["residual_frontier"]["open_items"]:
        for residual in result["residual_frontier"]["open_items"]:
            lines.append(
                f"- `{residual.get('residual_id', 'unnamed')}` [{residual.get('type', 'untyped')}]: {residual.get('description', '')}"
            )
    else:
        lines.append("No open residual is registered inside the declared finite scope.")
    lines.extend(
        [
            "",
            "## Prohibited inference",
            "",
            "Local certification must not be inflated into a claim about ultimate ontology, true life, phenomenal consciousness, or a unique final value function. Those positions remain separately registered in the status vector.",
            "",
            "## Causal handoff",
            "",
            f"- Owner: {result['certificate']['causal_handoff']['owner']}",
            f"- Next action: {result['certificate']['causal_handoff']['next_action']}",
            f"- Required artifact: {result['certificate']['causal_handoff']['required_artifact']}",
        ]
    )
    return "\n".join(lines) + "\n"


def _report_zh(engine: EssenceOmegaEngine, result: dict[str, Any]) -> str:
    scenario = engine.scenario
    selected = result["evaluation"]["selected_candidate_ids"]
    lines = [
        f"# {scenario.title_zh}",
        "",
        "## 有界结算",
        "",
        f"- 场景：`{scenario.scenario_id}`",
        f"- 局部本质状态：**{result['evaluation']['local_essence_status']}**",
        f"- 终极本质状态：**{result['evaluation']['ultimate_essence_status']}**",
        f"- 入选候选：{', '.join(selected) if selected else '无'}",
        f"- 运行哈希：`{result['run_hash']}`",
        "- 自动外部行动权限：`0`",
        "",
        "## 解释",
        "",
        "系统对“本质”采用操作性定义：在声明的变换下保持、每一保留组件经消融均不可缺少、能够跨声明世界运输，并能反向再生已登记后果的最小因果生成不变量。局部成功不被外推为终极形而上实体。",
        "",
        "## 候选结果",
        "",
        "| 候选 | 状态 | 层级 | 组件数 | 保真度 | 反向再生 |",
        "|---|---|---|---:|---:|---:|",
    ]
    for item in result["evaluation"]["candidate_evaluations"]:
        lines.append(
            f"| {item['candidate_id']} | {item['status']} | {item['essence_level']} | {item['component_count']} | {item['metrics']['fidelity']:.3f} | {item['metrics']['reverse_regeneration']:.3f} |"
        )
    lines.extend(["", "## 余量前沿", ""])
    if result["residual_frontier"]["open_items"]:
        for residual in result["residual_frontier"]["open_items"]:
            lines.append(
                f"- `{residual.get('residual_id', 'unnamed')}`［{residual.get('type', 'untyped')}］：{residual.get('description_zh', residual.get('description', ''))}"
            )
    else:
        lines.append("声明的有限范围内当前未登记开放余量。")
    lines.extend(
        [
            "",
            "## 禁止外推",
            "",
            "局部证书不得被夸大为对宇宙最终本体、真正生命、现象意识或唯一终极价值函数的证明；这些位置在状态向量中分开结算。",
            "",
            "## 因果交接",
            "",
            f"- 责任主体：{result['certificate']['causal_handoff']['owner']}",
            f"- 下一行动：{result['certificate']['causal_handoff']['next_action']}",
            f"- 所需成果：{result['certificate']['causal_handoff']['required_artifact']}",
        ]
    )
    return "\n".join(lines) + "\n"


def write_run_outputs(output_dir: Path, engine: EssenceOmegaEngine, result: dict[str, Any]) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "result.json", {key: value for key, value in result.items() if key != "certificate"})
    write_json(output_dir / "essence_certificate.json", result["certificate"])
    write_json(output_dir / "essence_lattice.json", result["evaluation"]["essence_lattice"])
    write_json(output_dir / "candidate_evaluations.json", result["evaluation"]["candidate_evaluations"])
    write_json(output_dir / "semantic_graph.json", result["semantic_graph"])
    write_json(output_dir / "residual_frontier.json", result["residual_frontier"])
    write_json(output_dir / "probe_plan.json", result["probe_plan"])
    write_json(output_dir / "causal_handoff.json", result["certificate"]["causal_handoff"])
    write_text(output_dir / "counterfactual_ablation_matrix.csv", _counterfactual_csv(result["evaluation"]))
    write_text(output_dir / "report.en.md", _report_en(engine, result))
    write_text(output_dir / "report.zh-CN.md", _report_zh(engine, result))
    engine.ledger.write(output_dir / "evidence_ledger.jsonl")

    artifact_paths = sorted(
        path for path in output_dir.iterdir() if path.is_file() and path.name != "output_manifest.json"
    )
    artifacts = [
        {"path": path.name, "sha256": sha256_file(path), "size_bytes": path.stat().st_size}
        for path in artifact_paths
    ]
    manifest = {
        "system": "DIKWP-ESSENCE-OMEGA-OS",
        "version": __version__,
        "scenario_id": engine.scenario.scenario_id,
        "run_hash": result["run_hash"],
        "ledger_head_hash": engine.ledger.head_hash,
        "artifacts": artifacts,
        "merkle_root": merkle_root(item["sha256"] for item in artifacts),
    }
    write_json(output_dir / "output_manifest.json", manifest)
    return {
        "scenario_id": engine.scenario.scenario_id,
        "output": str(output_dir),
        "run_hash": result["run_hash"],
        "ledger_head_hash": engine.ledger.head_hash,
        "selected_candidate_ids": result["evaluation"]["selected_candidate_ids"],
        "local_essence_status": result["evaluation"]["local_essence_status"],
        "ultimate_essence_status": result["evaluation"]["ultimate_essence_status"],
        "artifact_count": len(artifacts) + 1,
        "manifest_merkle_root": manifest["merkle_root"],
    }


__all__ = ["EssenceOmegaEngine", "ScenarioError", "write_run_outputs"]
