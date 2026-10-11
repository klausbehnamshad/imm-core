# Zenodo Publishing Guide — IMM-Core

**Concept DOI (all versions):** https://doi.org/10.5281/zenodo.20507328

**Status:** v1.0 published 2026-06-02 (10.5281/zenodo.20507329); 1.1.0 published 2026-10-06 (10.5281/zenodo.23190815). 1.2.0 is unreleased. This guide reserves no new DOI and executes no release; it only describes the steps.

---

## Publishing 1.2.0 (current procedure; no release executed here)

1. Create the version draft once: open the published 1.1.0 record at https://zenodo.org and click **New version**. Reserve the DOI shown in that draft. Carry out every step below in this same draft; never create a second draft afterwards.
2. Set the final metadata on the release branch: version `1.2.0`, the concept DOI and the reserved version DOI in `CITATION.cff`, `.zenodo.json` and `CHANGELOG.md`; bring `README.md` and `docs/` to the release state.
3. Merge the release branch into `main`; CI must be green. Record the accepted source commit hash.
4. Build the bundle exactly from that accepted commit (check it out first):

```bash
zip -r imm-core-v1.2.0.zip \
  README.md LICENSE CITATION.cff CHANGELOG.md \
  tap/core.csv schema/core.schema.json \
  vocabs/ profiles/ crosswalks/ \
  examples/core-generic.json examples/core-oral-history.json examples/core-minimal.json \
  methodological-positions/ docs/ \
  tools/ scripts/ tests/ \
  -x '*/__pycache__/*'
```

The bundle carries `tools/data/LICENSE-dataverse.md` (the Dataverse
source licence) inside `tools/`. Generated `__pycache__` directories
stay out.

**Excluded** (do not upload): `.zenodo.json`, `ZENODO-PUBLISHING-GUIDE.md`, `.github/`.

5. Upload `imm-core-v1.2.0.zip` to the same draft from step 1. Optionally also upload these three files individually alongside the zip (makes them directly browsable without unzipping):
   - `tap/core.csv`
   - `schema/core.schema.json`
   - `docs/README.md`

   Fill in the metadata form from `.zenodo.json`:

| Field | Value |
|---|---|
| **Upload type** | Dataset |
| **Title** | IMM-Core: Interview Metadata Model — Core Profile |
| **Authors** | Behnam Shad, Klaus · ORCID `0000-0002-3601-9024` · C²DH, University of Luxembourg |
| **Description** | Paste the `description` value from `.zenodo.json` |
| **License** | Creative Commons Attribution 4.0 International |
| **Version** | type 1.2.0 into the Version field (the value in .zenodo.json) |
| **Publication date** | today |
| **Keywords** | interview metadata; qualitative research; oral history; metadata model; FAIR data; GDPR; DCTAP; JSON Schema; Dublin Core; REFI-QDA; QDPX; schema.org; minimal metadata; research data management |
| **Notes** | DCTAP-as-SSoT: tap/core.csv is authoritative; schema/core.schema.json is a derived artefact. Working repository: https://github.com/klausbehnamshad/imm-core |

   **Communities** — apply via the Communities tab (applications are reviewed; approval can happen post-publication):
   - `dariah`
   - `clarin`

   Check that the draft shows the reserved DOI from step 1 before publishing.

6. Click **Preview** — confirm the DOI shown is the reserved DOI from step 1. Confirm author name, ORCID, and affiliation. Click **Publish**. The record is now live and immutable.

7. Tag the release on the archived source state:

```bash
git tag -a v1.2.0 <commit-hash-from-step-3> -m "IMM-Core v1.2.0"
```

   Record later publication dates in a follow-up commit on `main`; that commit neither moves the tag nor changes any archived file. No change to archived files is a prerequisite for this tag.

> **Post-publication corrections:** Zenodo lets you edit metadata (title, description, keywords) without creating a new version — use **Edit** on the published record. To change files, you must create a new version (new DOI). The original version and its DOI are always preserved.

No release is executed as part of this guide update; no new DOI is reserved here.

---

## History: v1.0 (published 2026-06-02, record only)

The steps below are the closed v1.0 record. For 1.2.0 follow "Publishing 1.2.0" above.

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

Form filled from `.zenodo.json` (same fields as in step 5 above, with version 1.0).

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
