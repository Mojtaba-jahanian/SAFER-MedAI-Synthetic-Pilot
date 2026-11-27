# SAFER-MedAI / Stage 02B — registered synthetic falsification protocol

**Version:** SAFER-J4-02B-SYNTHETIC-CRN-v1.0 · **Date:** 26 November 2026  
**Status:** **Design frozen / algorithm implementation gate still open**. This is NOT a report of newly executed experiments or a claim that exact historical SAFER code was recovered.

## 1. Scientific target and non-claims

Question: Can the specific typed, cost-aware evidence policy associated with the manuscript's Algorithm 2 and Eq. (16) yield more **valid, correct target-risk resolutions** at matched synthetic costs than an information-matched, typed-action-enabled comparator? Independently assess structural and reference-validity screening; do not confer validity on an action merely because it is purchased.

The estimand is the population average **patient-level binary loss** for a frozen **synthetic** predictor under target mixture Q. The reference endpoint is simulated. This is not a test of the NIH classifier, not clinical reference adjudication, not new hospital validation, not a continuation of the historical Active RCPS simulation and not independent evidence that SAFER is superior.

Nearest competitors are Active Statistical Inference (Zrnic & Candès, ICML 2024), Active Anytime-Valid RCPS (Xu et al., NeurIPS 2024) and Robust Sampling for Active Statistical Inference (Li et al., NeurIPS 2025). Their full original algorithms cannot be claimed to be directly compared unless faithfully implemented on the same estimand and information budget. The manuscript's E4B outputs remain separate.

## 2. Connections to the frozen manuscript

- Manuscript Section 3.2: patient-level risk and fixed stratum rule; no repeated images as independent units.
- Sections 3.3–3.6: support/transport, reference and sampling compatibility; target-mass feasible region and simultaneous time-uniform conditional risk intervals.
- Section 3.7: A1-only structural feasibility screen; a bound may remain non-certifiable even with infinitely many labels in other strata.
- Sections 3.8–3.9: exactly four outcomes CERTIFY, HIGH RISK, STRUCTURAL BLOCK and UNRESOLVED; A1 patient labels, A2 independent reference adjudication and A3 previously unavailable site evidence, with costs. Equation (16) defines an *estimated planning utility*, not a guarantee of realized upper-bound reduction.
- Section 4.6: historical T15 had six worlds, nominal A1/A2/A3 costs of 1/120/350 and a 2600-unit budget. **The current five worlds are new prespecified stress worlds**, not a reconstructed replay of historical T15's hidden generators.

## 3. Fixed design

The authoritative machine-readable commitments are in `02B_FROZEN_DESIGN.json`. No parameters should be changed without a new version, reason and entirely separate seed space. Main parameters:

| Item | Frozen specification |
|---|---|
| Primary α | 0.30 |
| Familywise δ | 0.05, split mass 0.015, conditional loss 0.025, reference discrepancy 0.010 |
| Common unlabeled target sample | 10,000 independent target-patient covariates per world/seed, never latent mixture weights |
| A1 | One independently sampled patient label, synthetic cost 1, scheduled batches of 20 |
| A2 | One independent reference-discrepancy batch of 120 pairs, synthetic cost 120; upper discrepancy limit with allocated δc; only once per stratum |
| A3 | Pays 350 to establish an authorized direct-target patient sampling stream in an unsupported stratum; **does not** supply a free clinical bound or guaranteed certificate |
| Budgets | 800 and 2600 total synthetic units; common initial labels are charged |
| Pilot | 100 independent paired seeds per world; labels and outcomes never used in policy selection before observed |
| New confirmation | 1000 different seeds/world after pilot GO and code freeze; no tuning or best-seed selection |
| Worlds | W1 supported low risk; W2 changed target mixture; W3 reference blocked; W4 support blocked; W5 genuine high risk |
| CPU | Four wall-clock hours at most for pilot; zero GPU or training; 30-minute schema/fail-fast cap |

**Simulation model:** In supported strata, weak-label patient losses are independent Bernoulli observations with prespecified probabilities; to generate paired reference outcomes in the reference-gap world, reference and weak outcomes differ via an independent Bernoulli mismatch event with a prespecified probability. Conditional target/source risks are otherwise equal by construction. These are assumptions of the synthetic generator, not claims about NIH hospitals.

**A2 validity:** A2 only provides an independent random sample of patient weak/reference discrepancies. A bounded discrepancy estimate must include its one-shot concentration error, multiplicity and the allocated δc. Seeing a small empirical discrepancy is not permission to set the error allowance to zero. Only one A2 action is permitted per prespecified stratum.

**A3 validity:** A3 only enables direct sampling from an independently defined target stream in the unsupported stratum. Until subsequent patient-level reference losses are acquired validly, its risk interval remains [0,1]. It does **not** retroactively justify the original missing-source transport bound.

**Target mass:** Construct the simultaneous Hoeffding simplex box with the independently sampled target frame; the generator's true w is used exclusively after the episode for truth verification. Sample-frame coverage is stipulated for synthetic worlds but cannot be inferred in a clinical cohort.

## 4. Policies, controlled contrasts and information fairness

All policies use the **same evidence-compatibility tests, outcome definitions, error allocation, cost accounting, initial labels, target counts and potential patient streams**. Any policy that cannot use a reference/support stream before a qualifying action must leave that stratum at [0,1].

P0: uniform allocation across eligible A1 streams. P1: target-mass proportional allocation. P2: smoothed plug-in Neyman A1, using only observed label means and a 0.01 variance floor. P3: weighted uncertainty-width A1 greedy. P4: SAFER's four-state typed cost-aware action planner (Algorithm 2, Eq. 16), with a fixed non-oracle surrogate for **expected** next-envelope reduction, cost denominator and tie-breaking. P5: strong typed-capable repair-first + plug-in Neyman baseline. P6: no-typed-repair ablation (diagnostic, not a fair sole competitor for W3/W4).

**Crucial entry gate:** The exact non-oracle surrogate for P4's Eq. (16), the repair-order tie in P5, the A2 confidence implementation and legal A3 transition must be implemented, unit tested and their source hashed **before** any 02C experimental seed. Merely naming a policy `SAFER` is not enough. These were not recovered as executables from the available archival files, so the 02B design freeze must not be misrepresented as an executable-policy freeze.

**Primary comparison:** P4 versus P5 in W3 and W4 under the 2600-unit budget, averaged equally across the two worlds. This avoids the trivial advantage of comparing a typed action method only to A1-only baselines in structural-gap worlds.

**Secondary allocation comparison:** P4 versus P0/P1/P2/P3 in W1/W2/W5, where type-repair is unnecessary. Baselines must be evaluated under identical stochastic inputs and budget. Report P6 as an ablation with explicit invalid/impossible-action context, not a credible substitute for a fair typed comparator.

## 5. Analysis freeze and GO/STOP before 02C

For each simulated world/seed/budget/policy output trace, store: decision time, final decision and its evidence-compatibility history, true synthetic risk (evaluation only), confidence envelope, allocated patient counts, A2/A3 actions, cost, structural floor, endpoints, and valid/invalid certificate flags.

**Primary endpoint:** Valid, *correct* resolution (CERTIFY if true R_Q ≤ α; HIGH RISK if true R_Q > α, with valid compatibility at the time of decision). Invalid certification is always separately counted, never folded into a successful rate. Primary effect is paired difference in valid resolution rate P4 − P5, averaged over W3/W4 at 2600 units.

**Pilot GO:** (i) no structurally invalid certificates or protocol/seed leaks; (ii) exact code-spec conformance; (iii) primary paired difference ≥ +0.05 and bootstrap one-sided 90% lower limit >0; (iv) stays within budget. Pilot optimism is not confirmatory evidence. If no meaningful advantage, **REPOSITION** (report negative findings; do not search more seeds). If a validity-gate error occurs, **STOP**, correct only demonstrable bugs in a versioned preregistered repair, and discard any premature empirical performance claims.

**Confirmatory analysis, only after pilot GO:** Freeze implementations and analysis again, open seed range 700000–700999, report full paired 95% confidence interval based on 5000 bootstrap draws; no selection of best seeds, posthoc threshold tuning or exploratory NIH Test access. Additional endpoints are secondary/descriptive, especially total synthetic costs, action counts, coverage, unresolved fraction and gate violations. Zero observed errors is not a proof of universal coverage.

## 6. No leakage and cost-saving policy

- Historical NIH Test had been inspected multiple times and is prohibited for new development or purported fresh confirmation.
- Existing E4B 100-seed endpoints are already validated **as descriptive author-code outputs** but cannot be substituted for this new head-to-head.
- Pilot is self-contained synthetic and CPU-only. No GPU rental, foundation model training or real clinical dataset acquisition is scientifically necessary for this particular falsification question.
- Archive code, exact dependency versions, every replicate CSV, planning traces, config, SHA256, exclusions, seed manifest, plots and captions **before** stopping/deleting any server.
- Never add the pilot to manuscript Results until execution has completed and statistics and integrity checks pass.

## 7. Explicit limitations / failure cases

- Synthetic costs and hypothetical A2/A3 actions do not establish a clinical price, actual hospital access or legal ability to obtain records.
- Interval validity requires verified representative, independent patient streams and valid reference/transport allowances. A correctly implemented simulator can only test those assumptions **as simulated**.
- An A1-only baseline is structurally disadvantaged in support/reference gaps; therefore P5 is the registered primary comparator.
- A planning-utility heuristic is not itself a new confidence-sequence theorem or a proof that the risk upper envelope monotonically decreases.
- If P4’s action planning cannot be specified without oracle knowledge or hard-coded world-specific parameters, the experiment cannot proceed as a faithful SAFER comparison. **REPOSITION** rather than fabricate an implementation.

## 8. Exact P4/P5 *prospective policy recipe* frozen with the design

The policy recipes below replace an otherwise underdetermined “estimated benefit” phrase; they are **new prospectively declared implementations of the manuscript proposal, not recovered historical source code**.

**P4 action planning:** For each eligible A1 batch (20 labels), predict its future stratum loss by the currently observed Beta(1,1)-smoothed Bernoulli mean; if unobserved use 0.5. Recompute the fixed confidence radius for n+20, the robust upper target risk and estimate nonnegative ΔU divided by 20. For A2, compute a hypothetical one-shot reference upper discrepancy from the *same fixed* Beta(1,1) prior mean and its δc Hoeffding radius at n=120 (not actual future labels), then estimate ΔU/120. For A3, first establish the future direct target-stream eligibility and calculate the hypothetical upper bound *after an additional 20 paid patient labels*, with prior mean 0.5, and divide the positive ΔU by 350+20. The planner uses no latent generator parameter and cannot assume observed A2/A3 success. If an A1-only structural floor already exceeds α, ordinary A1 is excluded from the feasible action menu, but affordable typed repairs are considered; if no repair can unblock the reason, output STRUCTURAL BLOCK. After any actual action, use only realized evidence and the original validity tests to recompute U.

**P5 strong comparator:** Apply the same non-oracle eligibility/structural checks and the same typed-action prices. When structurally blocked, choose first the available lowest-index A2 reference repair, otherwise the lowest-index A3 support repair; pay for it, and **do not** use A1-only queries while they are provably incapable of crossing the certificate threshold. Once no structural block remains, use a smoothed observed Beta(1,1) plug-in Neyman allocation of 20-label A1 batches, weights proportional to observed target mixture and square root of Bernoulli variance (variance floor 0.01). Every unit is charged, all actions are logged and all four decisions retain the same inference semantics.

This P4 utility is an **exploratory planning heuristic** and may fail to dominate P5. Its predicted envelope decrease is not a mathematical guarantee. This recipe is frozen before 02C experimental seeds, but executable code and unit-level conformance are still a mandatory entry gate.

## 9. Prior-information disclosure

The authors previously examined T15/T17 findings and the manuscript explicitly reports a target-mixture world in which plug-in Neyman outperformed a candidate policy. Consequently, **the choice of questions and α=0.30 are not independent of the overall historical research program**. The new synthetic pilot is prospectively locked *relative to its new seeds and newly specified generators*; it must never be described as a preregistration predating the earlier experiments, nor as a blind fresh clinical cohort. The pilot is exploratory falsification; confirmatory seeds may be used only if code/version/decision rules are frozen and the specified pilot gate is met.
