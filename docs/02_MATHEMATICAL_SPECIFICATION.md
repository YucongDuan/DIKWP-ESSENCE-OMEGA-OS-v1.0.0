# Mathematical Specification

## 1. World and test contract

Let \(\mathcal W=\{w_1,\dots,w_n\}\) be a declared family of worlds and \(\mathcal T=\{t_1,\dots,t_m\}\) a declared family of tests. The observation function is

\[
Y:\mathcal W\times\mathcal T\to\mathcal O\cup\{\bot\}.
\]

A candidate essence \(E\) contains a component set \(C_E\), prediction map \(\widehat Y_E\), scope \(S_E\subseteq\mathcal W\), falsification conditions, and reverse generator \(G_E\).

## 2. Fidelity and coverage

\[
\operatorname{Fidelity}(E)=
\frac{|\{(w,t):\widehat Y_E(w,t)=Y(w,t)\}|}
{|\{(w,t):t\text{ is required in }w\}|}.
\]

A missing or wildcard prediction does not count as a match.

## 3. Component necessity

For component \(c\in C_E\), let \(E\setminus c\) be the predeclared ablated candidate. Then

\[
\operatorname{Necessary}(c;E)=1
\iff
\exists(w,t)\;\widehat Y_{E\setminus c}(w,t)\neq Y(w,t)
\land
\widehat Y_E(w,t)=Y(w,t).
\]

The candidate is minimal only if every component has been tested and is necessary.

## 4. Nuisance invariance and consequential sensitivity

For nuisance transformations \(N\), the required relation is preserved. For consequential contrasts \((w_a,w_b,t)\), the candidate must reproduce the observed equality or inequality of outcomes. Invariance alone is not sufficient; a candidate invariant to every change is self-sealing or uninformative.

## 5. Reverse regeneration

\[
G_E(E,w,t)=Y(w,t)
\]

must hold over the required scope. Reverse regeneration prevents a candidate from being only a post-hoc description of already observed outputs.

## 6. Bounded essence certificate

\[
\operatorname{Cert}_{S_E}(E)=1
\]

only if fidelity, coverage, transport, contrasts, minimality, reverse regeneration, falsifiability, and hard value/permission constraints all pass, and no declared blocking residual remains.

## 7. Anti-self-sealing condition

A candidate is rejected when any of the following holds:

- wildcard predictions absorb possible outcomes;
- no falsification condition is declared;
- scope is allowed to shrink after a failure;
- a residual is renamed rather than linked to a reopening condition.

## 8. Local and ultimate statuses

\[
\operatorname{Cert}_{S_E}(E)=1
\not\Rightarrow
\operatorname{UltimateOntology}(E)=1.
\]

Only a fully enumerated finite formal world with no open residual can receive `FORMAL_ESSENCE_COMPLETE_WITHIN_ENUMERATED_WORLD`. Even that status does not imply final reality-wide ontology.
