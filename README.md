# SAFER-MedAI — Synthetic Typed-Evidence Pilot (Stage 02C-1)

**Reproducibility archive of a prospective, synthetic falsification pilot.**

This repository accompanies the research manuscript entitled:

> **When Medical AI Risk Cannot Be Certified: Support-Aware Statistical Risk Assessment and Cost-Aware Evidence Acquisition under Patient and Hospital Shift**

**Repository scope:** Synthetic Stage 02C-1 experiments only. This repository is **not** a clinically deployed AI system, a medical risk certificate, or a complete reproduction of the paper's retrospective NIH ChestXray14 and ECG analyses. The paper is not represented here as formally published. No manuscript DOI, software DOI, or repository license has yet been issued or authorized.

## Manuscript authors and affiliations

The following **seven manuscript authors** and their order are reproduced from the author-approved manuscript, Stage 02C-2N. Affiliation numbers refer to the institutional list immediately below.

| Order | Manuscript author | Affiliation(s) | Correspondence |
|---:|---|:---:|---|
| 1 | **Mehdi Hosseinzadeh** | 1 | — |
| 2 | **Parisa Khoshvaght** | 2 | — |
| 3 | **Ayoub Alsarhan** | 3 | — |
| 4 | **Ali Wagdy Mohamed** | 4 | — |
| 5 | **Thantrira Porntaveetus** | 5 | — |
| 6 | **Sadia Din** | 6 | Co-corresponding author |
| 7 | **Mojtaba Jahanian** | 7, 8 | **Primary corresponding author; senior author** |

### Institutional affiliations

1. School of Engineering & Technology, Duy Tan University, Da Nang, Vietnam.
2. Institute of Research and Development, Duy Tan University, Da Nang, Vietnam.
3. Department of Data Science and Artificial Intelligence, Hourani Center for Applied Scientific Research, Al-Ahliyya Amman University, Amman, Jordan.
4. Department of Operations Research, Faculty of Graduate Studies for Statistical Research, Cairo University, Giza 12613, Egypt.
5. Center of Excellence in Precision Medicine and Digital Health, Chulalongkorn University, Bangkok, Thailand.
6. Department of Computer Engineering, Gachon University, Seongnam-si, South Korea.
7. Department of Computer Engineering, National University of Skills (NUS), Tehran, Iran.
8. Department of Computer, Hmd.C., Islamic Azad University, Hamadan, Iran.

### Corresponding authors

- **Primary corresponding / senior author:** **Mojtaba Jahanian** — [mojtaba160672000@aut.ac.ir](mailto:mojtaba160672000@aut.ac.ir)
- **Co-corresponding author:** **Sadia Din** — [sadiadin@gachon.ac.kr](mailto:sadiadin@gachon.ac.kr)

### Author contributions (CRediT)

The responsibilities below reproduce the author contributions **approved for the associated manuscript** by its primary corresponding author. These are manuscript-level scientific contributions; they do **not**, by themselves, identify each person's software copyright ownership or individual authorship of this repository's source code.

| Author | Manuscript CRediT roles |
|---|---|
| Mehdi Hosseinzadeh | Methodology; Formal analysis; Validation; Writing – review & editing |
| Parisa Khoshvaght | Investigation; Visualization; Validation; Writing – review & editing |
| Ayoub Alsarhan | Methodology; Validation; Writing – review & editing |
| Ali Wagdy Mohamed | Formal analysis; Validation; Writing – review & editing |
| Thantrira Porntaveetus | Investigation; Validation; Writing – review & editing |
| Sadia Din | Conceptualization; Supervision; Validation; Writing – review & editing |
| Mojtaba Jahanian | Conceptualization; Methodology; Software; Data curation; Formal analysis; Validation; Visualization; Project administration; Writing – original draft; Writing – review & editing |

**Manuscript declarations (confirmed by the primary corresponding author):** No specific funding was received for this research; the authors declare no competing interests. The manuscript includes a disclosure of ChatGPT assistance in research planning, code review, and scientific editing. All scientific claims remain the responsibility of the human authors. These declarations concern the manuscript and do not constitute a software-license grant.

## Scientific scope and negative finding

The frozen pilot evaluated **5 synthetic worlds × 7 policies × 2 budgets × 100 seeds = 7,000 policy episodes**. A non-oracle one-step SAFER typed-action planner (P4) was compared against a repair-first Neyman policy (P5) using matched synthetic patient streams, hypothetical action prices and common validity gates.

Prespecified primary W3/W4 contrast at a budget of **2,600 hypothetical cost units**:

| World | P4: valid correct resolution | P5: valid correct resolution |
|---|---:|---:|
| W3 — reference gap | 100/100 | 100/100 |
| W4 — support gap | 0/100 | 100/100 |
| Equal-weight primary average | **50%** | **100%** |

Observed paired effect (P4 minus P5): **−50 percentage points**; exploratory paired percentile-bootstrap 90% CI **[−50, −50] pp**. The interval is degenerate in the recorded finite pilot; it does **not** prove that population uncertainty is zero.

The prespecified improvement gate **failed**. Accordingly, the planned 1,000-seed confirmatory experiment **was not run**. In W4, P4 paid for action A3 but did not request any A1 labels from the newly enabled stratum, whereas P5 did. There is **no claim of superiority, clinical-risk certification, real expert adjudication or external-hospital generalization**.

## Files and reproducibility

- `src/safer_cpu.py` — frozen Stage 02C-1 simulator and policy implementation.
- `src/pilot_02C1.py` — original pilot runner (provided for inspection; **not** evidence of a new historical run).
- `src/preflight.py` and `tests/test_safer_cpu.py` — preflight, smoke checks, unit tests.
- `configs/02B_FROZEN_DESIGN.json` — frozen prospective protocol configuration.
- `reference/02B_PROTOCOL_EN.md` — textual description of the prespecified synthetic study.
- `qa/` — code lock, documented pre-pilot P6 correction and audit evidence.
- `pilot_02C1/per_seed/` — 100 seed-specific metric files, 100 compressed action traces and 100 completion markers.
- `pilot_02C1/` — original aggregate files and SHA-256 manifest.
- `verify_archived_evidence.py` — check source/code lock and archived evidence hashes.
- `recompute_recorded_primary.py` — independently recompute primary comparison from stored episodes.
- `PROVENANCE_AND_LIMITATIONS.md` — full limitations and boundaries of this release.

### Verify and recompute the archived analysis

With **Python 3.10+** (no external Python packages needed for these checks), run in the repository root:

```bash
python verify_archived_evidence.py
python recompute_recorded_primary.py
python -m unittest discover -s tests -p 'test_safer_cpu.py' -v
```

These commands validate/reanalyze stored synthetic evidence. They are not a reproduction of original medical image inference, nor a clinical validation. Do not present newly executed simulations as the original frozen pilot, or treat unopened confirmatory seeds as if their registered gate had passed.

## Data, research ethics and public release boundaries

This repository deliberately excludes NIH ChestXray14 images, patient-indexed score tables, MIT–BIH records, historical ECG outputs, full manuscripts/medical figures and third-party Active RCPS source code. The study's retrospective imaging and ECG components have separate evidence limitations; this software release alone cannot reproduce their original fitted models or full inference environments.

The archive is **prepared for review**, not yet publicly released. Before changing visibility from **Private** to **Public**, confirm software and synthetic-data rights and select an explicit license. Read [`RIGHTS_AND_RELEASE_GATE.md`](RIGHTS_AND_RELEASE_GATE.md). In particular, manuscript coauthorship does not automatically establish software rights or permission to license all components under MIT.

## Citation and DOI

The associated **research manuscript** has the seven authors listed above in the stated order, with its full title given at the beginning of this README. Its citation should not claim journal publication until one actually occurs.

For **this code archive**, see [`CITATION.cff`](CITATION.cff): its current software-specific citation credits Mojtaba Jahanian as the listed software author, and is **not** intended to replace the manuscript's full author list. Software authorship/licensing can be revised if the rights and contribution record warrants it.

Target repository: `SAFER-MedAI-Synthetic-Pilot` · Proposed release: `v1.0.0`. **No Zenodo DOI exists yet.** After a GitHub Release is actually archived in Zenodo, record its **version DOI** and (when applicable) its **concept DOI** here and in the manuscript's Code Availability statement. Do not cite a placeholder DOI.

## Contact

**Mojtaba Jahanian**, primary corresponding author — [mojtaba160672000@aut.ac.ir](mailto:mojtaba160672000@aut.ac.ir)

Co-correspondence: **Sadia Din** — [sadiadin@gachon.ac.kr](mailto:sadiadin@gachon.ac.kr)
