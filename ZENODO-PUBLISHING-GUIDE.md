# Zenodo Publishing Guide — IMM-Core

**Concept DOI (all versions):** https://doi.org/10.5281/zenodo.20507328

**Status:** v1.0 published 2026-06-02 (10.5281/zenodo.20507329); 1.1.0 published 2026-10-06 (10.5281/zenodo.23190815); 1.2.0 with version DOI 10.5281/zenodo.23295846 and publication date 2026-10-11.

---

## Publishing a new version (procedure used for 1.2.0)

1. **Draft and DOI.** Open the published previous record on https://zenodo.org and click **New version**. Under "Do you already have a DOI?" choose **No** and click **Get a DOI now!**. Do not import files from the previous version. Click **Save draft**. Use this one draft for every later step.
2. **Release commit.** On the release branch, after all accepted changes, set version, publication date and the reserved version DOI in `CITATION.cff`, `.zenodo.json`, `CHANGELOG.md`, `README.md`, `docs/README.md` and the crosswalk heads. Commit once, signed, and record the commit:

```bash
IMM_RELEASE_COMMIT=$(git rev-parse HEAD)
```

3. **Checks** on that commit: `python scripts/check_consistency.py`, `python tools/validate.py --self-test`, `python tools/imm2dataverse.py --self-test`, `python -m unittest discover -s tests/tools`, ajv on `examples/*.json`.
4. **Bundle** from that commit only:

```bash
git archive --format=zip --output=imm-core-v1.2.0.zip "$IMM_RELEASE_COMMIT" \
  README.md LICENSE CITATION.cff CHANGELOG.md \
  tap/core.csv schema/core.schema.json \
  vocabs profiles crosswalks \
  examples/core-generic.json examples/core-oral-history.json examples/core-minimal.json \
  methodological-positions docs tools scripts tests
shasum -a 256 imm-core-v1.2.0.zip
```

The bundle carries `tools/data/LICENSE-dataverse.md` (the Dataverse source licence). **Excluded** (do not upload): `.zenodo.json`, `ZENODO-PUBLISHING-GUIDE.md`, `.github/`, `.gitignore`.

5. **CI before the tag.** Push the release branch and wait until CI is green for `IMM_RELEASE_COMMIT`.
6. **Main and tag.** Fast-forward `main` to the same commit, then tag and push both together; wait for green CI on `main`:

```bash
git tag -a v1.2.0 "$IMM_RELEASE_COMMIT" -m "IMM-Core v1.2.0"
git push --atomic origin main refs/tags/v1.2.0
```

7. **Upload and form.** Upload `imm-core-v1.2.0.zip` to the draft from step 1. The DOI stays in the Zenodo-generated (reserved) mode; do not enter it as an existing external DOI. Fill in the form from `.zenodo.json`:

| Field | Value |
|---|---|
| **Upload type** | Dataset |
| **Title** | IMM-Core: Interview Metadata Model — Core Profile |
| **Authors** | Behnam Shad, Klaus · ORCID `0000-0002-3601-9024` · C²DH, University of Luxembourg |
| **Description** | Paste the `description` value from `.zenodo.json` |
| **License** | Creative Commons Attribution 4.0 International |
| **Version** | the value in `.zenodo.json` |
| **Publication date** | the date set in step 2 |
| **Keywords** | interview metadata; qualitative research; oral history; metadata model; FAIR data; GDPR; DCTAP; JSON Schema; Dublin Core; REFI-QDA; QDPX; schema.org; minimal metadata; research data management |
| **Notes** | DCTAP-as-SSoT: tap/core.csv is authoritative; schema/core.schema.json is a derived artefact. Working repository: https://github.com/klausbehnamshad/imm-core |

   **Communities:** apply for `dariah` and `clarin` via the Communities tab; approval can come after publication.

8. **Preview and publish.** Confirm DOI, author, ORCID, affiliation, licence, version, date and the single ZIP. Click **Publish**. Download the public ZIP and compare its SHA-256 with step 4. Tag and files are not changed afterwards.

> **Post-publication corrections:** Zenodo lets you edit metadata (title, description, keywords) without creating a new version — use **Edit** on the published record. To change files, you must create a new version (new DOI). The original version and its DOI are always preserved.

---

## History: v1.0 (published 2026-06-02, record only)

The steps below are the closed v1.0 record. For new versions follow "Publishing a new version" above.

### Step 1 — Create draft deposit and reserve DOI *(v1.0, done)*

Draft created at https://zenodo.org. DOI reserved: `10.5281/zenodo.20507329`.

### Step 2 — Update files with real DOI *(v1.0, done)*

All `XXXXXXX` instances replaced with `20507329` across:
`README.md`, `docs/README.md`, `schema/core.schema.json`, `CITATION.cff`.

### Step 3 — Prepare the upload bundle *(v1.0, done)*

Bundle built from the accepted v1.0 state (same file list as in step 4 above, with `imm-core-v1.0.zip`).

### Step 4 — Upload files to the Zenodo draft *(v1.0, done)*

1. Open your draft at https://zenodo.org/uploads.
2. Upload `imm-core-v1.0.zip`.
3. Optionally also upload these three files individually alongside the zip:
   - `tap/core.csv`
   - `schema/core.schema.json`
   - `docs/README.md`

### Step 5 — Fill in the metadata form *(v1.0, done)*

Form filled from `.zenodo.json` (same fields as in step 7 above, with version 1.0).

### Step 6 — Preview and publish *(v1.0, done)*

1. Click **Preview** — confirm the DOI shown is `10.5281/zenodo.20507329`.
2. Confirm author name, ORCID, and affiliation.
3. Click **Publish**. The record is now live and immutable.

### Step 7 — Post-publication: update the working repository *(v1.0, done)*

After publishing:

**1. Commit the updated files** with message:
```
chore: add Zenodo DOI 10.5281/zenodo.20507329 (v1.0)
```

**2. Add the DOI badge** to the top of `README.md` (below the version line):
```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20507329.svg)](https://doi.org/10.5281/zenodo.20507329)
```

**3. Tag the release:**
```bash
git tag -a v1.0 -m "IMM-Core v1.0 — DOI 10.5281/zenodo.20507329"
git push origin v1.0
```

**4. (Phase 2) GitHub–Zenodo integration:** Once the repo is on GitHub, connect it via *Zenodo → Settings → GitHub*. Future releases will auto-deposit, with `.zenodo.json` providing the metadata automatically.

---

## Checklist (historical: completed releases, kept as record)

### v1.0 (published 2026-06-02, historical)

- [x] Step 1: Draft created, DOI `10.5281/zenodo.20507329` reserved
- [x] Step 2: DOI filled in all files
- [x] Step 3: bundle created
- [x] Step 4: files uploaded
- [x] Step 5: metadata form filled (no communities listed on the record as of 2026-10-06)
- [x] Step 6: preview checked, published
- [x] Step 7: working repo committed, badge added, `v1.0` tag pushed

### v1.1.0 (published 2026-10-06, historical)

- [x] Release branch merged into `main`, CI green
- [x] `imm-core-v1.1.0.zip` built from `main` at `ca0afb0` (files byte-identical)
- [x] New version created on Zenodo, files uploaded, form filled from `.zenodo.json`
- [x] Preview checked, published
- [x] Dates set in `CITATION.cff`, `.zenodo.json`, `CHANGELOG.md`; commit on `main`
- [x] `v1.1.0` tag pushed
