# Stage 02C-0 prospective implementation conformance audit

Status: **implementation and CPU preflight passed; prospective pilot and confirmatory experimental evidence NOT started**.

## Frozen sources used
- `configs/02B_FROZEN_DESIGN.json` original JSON SHA256 in `configs/02B_SHA256.txt`.
- `reference/02B_PROTOCOL_EN.md` originally frozen before implementation.
- `reference/METHOD_SOURCE_UNCHANGED.tex`, which contains original manuscript Eqs.(7)-(16), and `reference/ALGORITHM_02_EXACT_VECTOR_CROP.pdf`.
- This is **not historical recovered SAFER source code**; it is a new prospective reference implementation of a predeclared policy specification.

## Coverage mapping

| Frozen scientific rule | Source implementation | Verification |
|---|---|---|
| Eq.7-8 independent target covariate mixture and simultaneous box/simplex | `mixture_box`, `SyntheticEnvironment._draw_masses` | mass bounds, CRN mixture equality |
| Eq.9-11 time-uniform conditional Hoeffding; K prespecified | `radius_hoeffding_anytime`, `EvidenceLedger.snapshot` | numerical equation tests |
| Eq.12 and Algorithm1 min/max constrained simplex | `extreme_simplex` | constructive tests and exhaustive 2/3/4-d vertex enumeration |
| Eq.14 A1-only structural floor (not a measure of true risk) | `EvidenceLedger.snapshot` | reference and support block fixtures |
| Eq.15 four exclusive states | `EvidenceLedger.snapshot` | constructive four-state fixtures |
| Eq.16 P4 *planning-only* beta-smoothed future expected upper change | `projected_upper`, `choose_action` | observed-only interface; no mutation before action; deterministic tie |
| P5 typed repairs + observed plugin Neyman | `choose_action('P5')` | repair-first tests |
| Independent A1 patient-level source / target streams | `SyntheticEnvironment.draw_a1` | uniqueness, reproducibility, barred A1 for unsupported |
| A2 real independent paired discrepancy audit and one-shot confidence | `draw_a2`, `execute(A2)` | audit cohort distinct; one-shot; price and delta checks |
| A3 grants only valid direct target clinical-reference stream | `execute(A3)` | no free label, opens A1 later |
| Configured A1/A2/A3 costs, shared warm start | `EvidenceLedger`, `execute` | budget enforcement and price consistency |
| Non-oracle policy receives no latent true risk or true mixture | immutable `EvidenceView` | negative field test; code inspection |
| Same potential outcomes across policies and budgets | `derived_seed` and per-stream RNG | identical prefix checks |
| Experimental seed seal for 02C-0 | `run_episode` guard | pilot/confirmatory seed refusal tests |

## Important honest limitations
1. Unit tests are not a theorem proving all program paths. Prospective synthetic pilot will test empirical behavior separately; no model efficacy may be inferred from this preflight.
2. The synthetic source and target conditional weak risks are equal by generating assumption; this is not learned or verified clinical transport. `source_masses` are generator scenario metadata; actual labels are sampled by prespecified stratum streams rather than drawing a finite source-population cohort. No conclusion about empirical hospital shift follows.
3. `A2` is a synthetic paired weak/reference difference audit; it cannot establish availability of such adjudication in a real hospital.
4. `A3` creates independent synthetic direct clinical-reference target samples; no real hospital data acquired.
5. The planning heuristic in P4 is frozen and *not guaranteed* to beat P5, to monotonically decrease a confidence upper bound, or to optimize real costs.
6. Performance of the methods must be decided solely after the registered pilot; the pilot must not be used to tune the code except transparent, documented correction of proven validity bugs.
7. Current synthetic test is NOT patient-holdout NIH evaluation, does not replace historical T15/T17 and does not provide a new Active RCPS head-to-head.
8. For internal `STRUCTURAL_BLOCK`, the ledger computes the A1-only floor even if an A2/A3 repair is still available; the actual policy continues valid repairs and only *returns* a terminal structural block when no useful affordable repair is available.
9. No medical/patient identifiers stored in artifacts. Python `tracemalloc` reports Python allocation peak, not total system RAM.
10. Further automated external code review would strengthen implementation confidence before any manuscript claim; successful unit tests alone do not establish inferential correctness for arbitrary clinical data.

## G4/G5 data boundary
- Internal preflight seed is 52026, outside the registered pilot (600000..600099) and confirmation (700000..700999).
- No experiment runs on registered seeds, no manuscript Results changes, no threshold/model/code selection based on pilot outcomes.
