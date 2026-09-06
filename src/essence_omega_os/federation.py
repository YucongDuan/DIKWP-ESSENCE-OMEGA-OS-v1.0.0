from __future__ import annotations

from typing import Any

from .utils import canonical_json, sha256_text, stable_id


def federate_certificates(certificates: list[dict[str, Any]]) -> dict[str, Any]:
    """Construct a non-annexing comparison of bounded essence certificates.

    The function reports intersections and differences. It never rewrites a local
    certificate into a single global ontology.
    """
    if not certificates:
        raise ValueError("at least one certificate is required")
    component_sets: list[set[str]] = []
    certificate_rows: list[dict[str, Any]] = []
    residual_types: set[str] = set()
    forbidden: set[str] = set()
    for certificate in certificates:
        components = {
            component
            for candidate in certificate.get("selected_essence_candidates", [])
            for component in candidate.get("components", [])
        }
        component_sets.append(components)
        for candidate in certificate.get("selected_essence_candidates", []):
            forbidden.update(str(item) for item in candidate.get("forbidden_inferences", []))
        for residual in certificate.get("residual_frontier", {}).get("open_items", []):
            residual_types.add(str(residual.get("type", "untyped")))
        certificate_rows.append(
            {
                "certificate_id": certificate.get("certificate_id"),
                "scenario_id": certificate.get("scenario_id"),
                "local_status": certificate.get("local_essence_status"),
                "ultimate_status": certificate.get("ultimate_essence_status"),
                "selected_components": sorted(components),
            }
        )
    shared = set.intersection(*component_sets) if component_sets else set()
    union = set.union(*component_sets) if component_sets else set()
    local_only = {
        str(certificate_rows[index]["certificate_id"]): sorted(component_sets[index] - shared)
        for index in range(len(component_sets))
    }
    result: dict[str, Any] = {
        "federation_type": "NON_ANNEXING_ESSENCE_FEDERATION",
        "certificates": certificate_rows,
        "shared_component_core": sorted(shared),
        "component_union": sorted(union),
        "local_only_components": local_only,
        "open_residual_types": sorted(residual_types),
        "combined_forbidden_inferences": sorted(forbidden),
        "status": "SHARED_COMPONENT_CORE_FOUND" if shared else "NO_SHARED_COMPONENT_CORE",
        "boundary": "intersection is a comparison result, not a final global essence; local residuals and scopes remain sovereign",
        "automatic_external_action_authority": 0,
    }
    result["federation_id"] = stable_id("essence-fed", result)
    result["sha256"] = sha256_text(canonical_json(result))
    return result
