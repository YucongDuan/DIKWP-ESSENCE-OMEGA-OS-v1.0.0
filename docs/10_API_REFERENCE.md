# API Reference

## `ScenarioSpec.from_dict(data)`

Validates scenario identity, worlds, tests, candidate scopes, component uniqueness, contrasts, and the zero external-action-authority invariant.

## `EssenceEvaluator(scenario).evaluate()`

Returns candidate evaluations, the essence lattice, selected plural minimum-component candidates, local status, ultimate status, and the non-aggregate selection rule.

## `EssenceOmegaEngine(data).run()`

Runs the ten-stage pipeline and returns the certificate, semantic graph, residual frontier, probe plan, ledger head, and deterministic run hash.

## `write_run_outputs(path, engine, result)`

Writes the complete artifact bundle and a Merkle-rooted output manifest.

## `HashLedger.read_and_verify(path)`

Validates indexes, predecessor hashes, stable event identifiers, and event hashes.

## `plan_probes(raw_scenario, candidate_evaluations)`

Filters probes by authority, reversibility, lease, harm, and irreversibility, then applies a declared lexicographic rule based on discrimination and cost.

## `federate_certificates(certificates)`

Returns shared components, local-only components, residual types, and forbidden inferences without constructing a global ontology.
