# Release gate — approval required before public release

**Prepared, not published.** GitHub public visibility, tag/release publication and Zenodo archiving are external publication actions. Confirm ALL before making the repository public:

1. Authorized rights holder(s) approve publishing this *original* simulation source, tests, protocol, synthetic data and traces under the selected reuse license. Approval of article authorship/CRediT by itself does not grant a software license.
2. Recommended **MIT license for original software**. Synthetic-record permissions may be declared separately (e.g., CC0-1.0 or CC-BY-4.0) if all rights holders approve; avoid a misleading catch-all license. Put the actual `LICENSE` and Zenodo metadata in the repository only after explicit license choice.
3. Do not upload the old reference PDF/medical thumbnails, NIH/MIT-BIH records, original ECG outputs, third-party Active RCPS source, or unpublished peer-review material.
4. Run `python verify_archived_evidence.py` and `python recompute_recorded_primary.py` on the staged repository. Check for credentials/identifiers and review all files listed by `git status` before the first push.
5. Check seven-author **scholarly** attribution vs **software authorship** with the primary corresponding author; do not automatically list all paper contributors as code maintainers without consent.
6. Confirm the repository's code/Data Availability description faithfully states missing pieces of full medical pipeline reproducibility.
7. Create and publish release `v1.0.0` only after linking the GitHub repository to Zenodo; wait for Zenodo to expose the version DOI and concept DOI. Never invent either.
