# Experiment Protocol

## Registration before results

Before a run, declare:

- worlds and carriers;
- test kinds and required tests;
- observed consequences;
- candidate components;
- candidate predictions;
- component-wise ablations;
- reverse-regeneration outputs;
- falsification conditions;
- hard value and permission constraints;
- forbidden inferences;
- residuals and reopening conditions.

## Test classes

- `required`: necessary for the local claim;
- `nuisance`: should not alter the relation;
- `consequential`: should expose a meaningful difference;
- `reverse`: checks return from the candidate to effects;
- `governance`: checks value, permission, refusal, or audit behaviour.

## Evidence discipline

The reference runtime does not infer missing predictions, synthesize unstated ablations, or repair a candidate after observing failure. Missing content remains missing. Wildcards are treated as self-sealing.

## Real-world deployment boundary

The included scenarios are offline and synthetic. A real probe requires separate named authority, data governance, reversibility, stopping conditions, risk review, and outcome custody. The runtime has no external-action connector and records automatic external action authority as zero.
