from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ScenarioError(ValueError):
    """Raised when a scenario violates the declared protocol."""


@dataclass(frozen=True)
class TestSpec:
    test_id: str
    kind: str
    required: bool = True
    label_en: str = ""
    label_zh: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TestSpec":
        if not data.get("test_id"):
            raise ScenarioError("every test requires test_id")
        kind = str(data.get("kind", "required"))
        if kind not in {"required", "nuisance", "consequential", "reverse", "governance"}:
            raise ScenarioError(f"unsupported test kind: {kind}")
        return cls(
            test_id=str(data["test_id"]),
            kind=kind,
            required=bool(data.get("required", True)),
            label_en=str(data.get("label_en", data.get("test_id", ""))),
            label_zh=str(data.get("label_zh", data.get("test_id", ""))),
        )


@dataclass(frozen=True)
class WorldSpec:
    world_id: str
    carrier: str
    environment: str
    observations: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorldSpec":
        if not data.get("world_id"):
            raise ScenarioError("every world requires world_id")
        observations = data.get("observations")
        if not isinstance(observations, dict) or not observations:
            raise ScenarioError(f"world {data.get('world_id')} requires non-empty observations")
        return cls(
            world_id=str(data["world_id"]),
            carrier=str(data.get("carrier", "unspecified")),
            environment=str(data.get("environment", "unspecified")),
            observations=dict(observations),
        )


@dataclass(frozen=True)
class ContrastSpec:
    test_id: str
    world_a: str
    world_b: str
    relation: str = "different"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContrastSpec":
        required = ["test_id", "world_a", "world_b"]
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise ScenarioError(f"contrast missing: {', '.join(missing)}")
        relation = str(data.get("relation", "different"))
        if relation not in {"different", "same"}:
            raise ScenarioError("contrast relation must be 'different' or 'same'")
        return cls(str(data["test_id"]), str(data["world_a"]), str(data["world_b"]), relation)


@dataclass
class CandidateSpec:
    candidate_id: str
    name_en: str
    name_zh: str
    components: list[str]
    scope_worlds: list[str]
    predictions: dict[str, dict[str, Any]]
    ablations: dict[str, dict[str, dict[str, Any]]]
    reverse_regeneration: dict[str, dict[str, Any]]
    falsification_conditions: list[str]
    forbidden_inferences: list[str]
    lineage: dict[str, Any] = field(default_factory=dict)
    scope_can_change_after_failure: bool = False
    notes: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CandidateSpec":
        if not data.get("candidate_id"):
            raise ScenarioError("every candidate requires candidate_id")
        components = [str(value) for value in data.get("components", [])]
        if not components:
            raise ScenarioError(f"candidate {data['candidate_id']} requires at least one component")
        return cls(
            candidate_id=str(data["candidate_id"]),
            name_en=str(data.get("name_en", data["candidate_id"])),
            name_zh=str(data.get("name_zh", data.get("name_en", data["candidate_id"]))),
            components=components,
            scope_worlds=[str(value) for value in data.get("scope_worlds", [])],
            predictions={str(k): dict(v) for k, v in data.get("predictions", {}).items()},
            ablations={
                str(component): {str(world): dict(predictions) for world, predictions in world_map.items()}
                for component, world_map in data.get("ablations", {}).items()
            },
            reverse_regeneration={str(k): dict(v) for k, v in data.get("reverse_regeneration", {}).items()},
            falsification_conditions=[str(value) for value in data.get("falsification_conditions", [])],
            forbidden_inferences=[str(value) for value in data.get("forbidden_inferences", [])],
            lineage=dict(data.get("lineage", {})),
            scope_can_change_after_failure=bool(data.get("scope_can_change_after_failure", False)),
            notes=dict(data.get("notes", {})),
        )


@dataclass
class ScenarioSpec:
    raw: dict[str, Any]
    scenario_id: str
    title_en: str
    title_zh: str
    description_en: str
    description_zh: str
    scope: dict[str, Any]
    purpose: dict[str, Any]
    tests: list[TestSpec]
    worlds: list[WorldSpec]
    contrasts: list[ContrastSpec]
    candidates: list[CandidateSpec]
    value_constraints: list[dict[str, Any]]
    residuals: list[dict[str, Any]]
    ontology_claims: dict[str, str]
    handoff: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScenarioSpec":
        if not isinstance(data, dict):
            raise ScenarioError("scenario must be a JSON object")
        scenario_id = str(data.get("scenario_id", "")).strip()
        if not scenario_id:
            raise ScenarioError("scenario_id is required")
        tests = [TestSpec.from_dict(item) for item in data.get("tests", [])]
        worlds = [WorldSpec.from_dict(item) for item in data.get("worlds", [])]
        candidates = [CandidateSpec.from_dict(item) for item in data.get("candidates", [])]
        if not tests:
            raise ScenarioError("at least one test is required")
        if not worlds:
            raise ScenarioError("at least one world is required")
        if not candidates:
            raise ScenarioError("at least one essence candidate is required")

        test_ids = [item.test_id for item in tests]
        world_ids = [item.world_id for item in worlds]
        candidate_ids = [item.candidate_id for item in candidates]
        for label, values in (("test", test_ids), ("world", world_ids), ("candidate", candidate_ids)):
            if len(values) != len(set(values)):
                raise ScenarioError(f"duplicate {label} identifiers are not allowed")

        known_tests = set(test_ids)
        for world in worlds:
            unknown = set(world.observations) - known_tests
            if unknown:
                raise ScenarioError(f"world {world.world_id} contains unknown tests: {sorted(unknown)}")

        known_worlds = set(world_ids)
        for candidate in candidates:
            if not candidate.scope_worlds:
                candidate.scope_worlds = list(world_ids)
            unknown = set(candidate.scope_worlds) - known_worlds
            if unknown:
                raise ScenarioError(
                    f"candidate {candidate.candidate_id} contains unknown scope worlds: {sorted(unknown)}"
                )
            if len(candidate.components) != len(set(candidate.components)):
                raise ScenarioError(f"candidate {candidate.candidate_id} has duplicate components")

        contrasts = [ContrastSpec.from_dict(item) for item in data.get("contrasts", [])]
        for contrast in contrasts:
            if contrast.test_id not in known_tests:
                raise ScenarioError(f"contrast uses unknown test: {contrast.test_id}")
            if contrast.world_a not in known_worlds or contrast.world_b not in known_worlds:
                raise ScenarioError("contrast uses an unknown world")

        purpose = dict(data.get("purpose", {}))
        if int(purpose.get("automatic_external_action_authority", 0)) != 0:
            raise ScenarioError("automatic_external_action_authority must be 0 in this reference runtime")

        title = data.get("title", {})
        description = data.get("description", {})
        return cls(
            raw=data,
            scenario_id=scenario_id,
            title_en=str(title.get("en", scenario_id)),
            title_zh=str(title.get("zh", title.get("en", scenario_id))),
            description_en=str(description.get("en", "")),
            description_zh=str(description.get("zh", description.get("en", ""))),
            scope=dict(data.get("scope", {})),
            purpose=purpose,
            tests=tests,
            worlds=worlds,
            contrasts=contrasts,
            candidates=candidates,
            value_constraints=[dict(item) for item in data.get("value_constraints", [])],
            residuals=[dict(item) for item in data.get("residuals", [])],
            ontology_claims={str(k): str(v) for k, v in data.get("ontology_claims", {}).items()},
            handoff=dict(data.get("handoff", {})),
        )

    @property
    def world_map(self) -> dict[str, WorldSpec]:
        return {item.world_id: item for item in self.worlds}

    @property
    def test_map(self) -> dict[str, TestSpec]:
        return {item.test_id: item for item in self.tests}
