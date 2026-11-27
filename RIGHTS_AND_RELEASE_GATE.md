# Rights, license, and scientific release boundaries — Stage 02C-1

## Authorization recorded

On 27 November 2026, Mojtaba Jahanian, primary corresponding and senior author of the related manuscript, explicitly confirmed authority to release the **original Stage 02C-1 implementation** and the **fully synthetic accompanying pilot records** publicly under the MIT License. The `LICENSE` file records the chosen terms.

This approval does **not** grant rights in third-party source code, external data, biomedical images, clinical labels, patient records, or other research projects. Such materials are excluded from this repository. Manuscript coauthorship/CRediT does not automatically determine software authorship; `CITATION.cff` separately describes the software citation.

## Scientific boundary

- This release covers the frozen Stage 02C-1 **synthetic** pilot only.
- Preserve the recorded negative primary effect (P4 versus repair-first P5: **-0.50** averaged over W3/W4).
- Do **not** claim clinical risk certification, task-matched superiority against Active RCPS, or external hospital validation.
- The planned 1,000 confirmatory seeds were **not** run after the pilot failed its GO criterion.
- No NIH ChestXray14 images/identifiers, MIT-BIH patient records, historical ECG output files or third-party Active RCPS source are included.
- Existing code and pilot traces remain byte-identical to their frozen archives; this licensing change modifies **metadata and documentation only**.

## Publication and DOI order

1. Push the MIT License and amended metadata, verifying the frozen scientific hashes.
2. Make the GitHub repository Public once its sensitive-content review is complete.
3. **Connect and enable the repository in Zenodo before publishing** a GitHub Release.
4. Publish GitHub Release `v1.0.0` from the approved commit.
5. Confirm Zenodo has archived that release; use the actual issued version DOI in the software citation and manuscript. Do not invent a DOI.

A MIT license allows redistribution under its conditions. Attribution, warranty limits and license terms are defined in `LICENSE`.
