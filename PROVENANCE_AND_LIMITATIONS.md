# Evidence provenance and reproducibility boundary

This release is limited to the Stage 02C-1 newly implemented prospective **synthetic** policy test. The implementation is **not** the previously frozen T14-B/T15/T17 historical code. Stage 02C-0 originally contained a mislabeled P6 ablation. `qa/P6_PREPILOT_CORRECTION.md` explains its repair **before** registered pilot seeds were used. Stage 02C-1 source and runner code were then frozen, as verified by `qa/02C1_LOCKED_HASHES.json`.

Do not conflate (1) Stage 02C-1 synthetic planner vs repair-first Neyman, (2) separate published Active RCPS author-code simulations on their own synthetic task, (3) retrospective NIH report-derived weak-label results, or (4) older ECG outputs. No task-matched full SAFER versus Active RCPS clinical comparison was performed.

Internal source used to assemble this release candidate: `SAFER_02C2J_SYNTHETIC_RELEASE_CANDIDATE_20261127.zip` (the local 02C-2J synthetic-release candidate). The release construction deliberately excludes old draft manuscripts, medical illustrations, reference PDF snapshots and unrelated source bundles. It preserves the original Python policy code, runner, registered protocol, generated synthetic records, and checksums byte for byte.

Unit tests, replayed results, and synthetic world checks do not demonstrate external-hospital generalization, clinically adjudicated labels, statistically optimal evidence acquisition or patient safety. Report negative findings transparently.

Release-date metadata and DOI must be populated only when publication has actually occurred.
