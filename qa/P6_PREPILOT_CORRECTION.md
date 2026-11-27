# 02C-1 bounded pre-pilot correction — P6 Ablation, not P4/P5

- 02B prespecified P6 **SAFER without typed repair** to estimate typed-action contribution.
- In Stage 02C-0, P6 was mistakenly implemented as the P0 uniform allocation alias (`if policy_id in ("P0","P6")`). That did NOT test the prescribed ablation.
- Before ANY registered pilot or confirmation seed was opened, a single correction implemented P6 using the same P4 planning-only A1 expected-envelope-reduction-per-cost ranking but barred A2/A3.
- P4 and P5 policy implementations, simulator, statistical tests, seed lists, parameters, thresholds and budget remain unchanged.
- This change modifies the SHA256 of `src/safer_cpu.py` and is to be disclosed as a pre-pilot conformance correction, NOT a post-hoc improvement.
- Code must pass all previous tests plus new P6 tests. The original Stage02C0 package remains unchanged and retained for traceability.
