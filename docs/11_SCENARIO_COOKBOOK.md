# Scenario Cookbook

A scenario contains:

```json
{
  "scenario_id": "example",
  "scope": {"world_type": "synthetic_finite", "formal_closed_exhaustive": false},
  "purpose": {"owner": "named-owner", "automatic_external_action_authority": 0},
  "tests": [{"test_id": "T1", "kind": "required", "required": true}],
  "worlds": [{"world_id": "W1", "carrier": "sim", "environment": "lab", "observations": {"T1": "yes"}}],
  "candidates": [{
    "candidate_id": "E1",
    "components": ["mechanism"],
    "scope_worlds": ["W1"],
    "predictions": {"W1": {"T1": "yes"}},
    "ablations": {"mechanism": {"W1": {"T1": "no"}}},
    "reverse_regeneration": {"W1": {"T1": "yes"}},
    "falsification_conditions": ["T1 is not yes"],
    "forbidden_inferences": ["local result is universal"]
  }],
  "value_constraints": [],
  "residuals": [],
  "handoff": {"owner": "named-owner", "next_action": "replicate"}
}
```

Do not use wildcards. Do not define an ablation after looking at its result. Do not omit an uncomfortable residual merely to obtain a certificate.
