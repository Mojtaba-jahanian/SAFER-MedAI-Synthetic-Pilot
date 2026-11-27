# SAFER-MedAI — GitHub and Zenodo publication guide

**Repository:** https://github.com/Mojtaba-jahanian/SAFER-MedAI-Synthetic-Pilot

The initial private Git push of the Stage 02C-1 code has succeeded. The primary corresponding author confirmed public release and MIT licensing of the **original** code and **fully synthetic** pilot artifacts on 27 November 2026. See `LICENSE` and `RIGHTS_AND_RELEASE_GATE.md`.

## Sequence — do not release before enabling Zenodo

1. Commit and push the authorized `LICENSE`, updated `CITATION.cff`, `README.md`, `RIGHTS_AND_RELEASE_GATE.md`, release notes and updated file manifest (using the provided PowerShell patch).
2. Verify the GitHub repository contains the MIT License, expected code, and synthetic traces **without** medical images, patient tables or credentials.
3. GitHub → Settings → General → Danger Zone → Change repository visibility → **Public**.
4. Log into https://zenodo.org with GitHub and open GitHub settings. Click **Sync now**, then enable `SAFER-MedAI-Synthetic-Pilot` with the toggle. See https://help.zenodo.org/docs/github/enable-repository/.
5. GitHub → Releases → Draft a new release → Create new tag `v1.0.0` from the approved `main` commit → use title `SAFER-MedAI Synthetic Pilot v1.0.0` and text in `RELEASE_NOTES_v1.0.0.md` → **Publish release**.
6. Inspect the imported record in Zenodo and copy the real **version DOI** and (if shown) **concept DOI**. Never insert placeholder DOI strings.
7. Only after the DOI exists, update README and the manuscript Code Availability in a **new documented editing step**; preserve the released v1.0.0 tag.

## Local verification from the repository root

```bash
python verify_archived_evidence.py
python recompute_recorded_primary.py
python -m unittest discover -s tests -p 'test_safer_cpu.py' -v
```

These commands verify archived **synthetic** results; they do not validate clinical safety. The GitHub Release must not imply the planned 1,000-seed confirmation took place.
