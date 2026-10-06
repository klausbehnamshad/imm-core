# Zenodo Publishing Guide — IMM-Core

**DOI:** https://doi.org/10.5281/zenodo.20507329

**Status:** v1.0 published 2026-06-02 (Steps 1–7 done). For 1.1.0 and later follow "Publishing a new version" below.

---

## Step 1 — Create draft deposit and reserve DOI *(done)*

Draft created at https://zenodo.org. DOI reserved: `10.5281/zenodo.20507329`.

## Step 2 — Update files with real DOI *(done)*

All `XXXXXXX` instances replaced with `20507329` across:
`README.md`, `docs/README.md`, `schema/core.schema.json`, `CITATION.cff`.

---

## Step 3 — Prepare the upload bundle

From the repository root, run:

```bash
zip -r imm-core-v1.1.0.zip \
  README.md LICENSE CITATION.cff CHANGELOG.md \
  tap/core.csv schema/core.schema.json \
  vocabs/ profiles/ crosswalks/ \
  examples/core-generic.json examples/core-luxoh.json examples/core-minimal.json \
  methodological-positions/ docs/
```

**Excluded** (do not upload): `.zenodo.json`, `ZENODO-PUBLISHING-GUIDE.md`, `tests/`, `scripts/`, `.github/`.

---

## Step 4 — Upload files to the Zenodo draft

1. Open your draft at https://zenodo.org/uploads.
2. Upload `imm-core-v1.1.0.zip`.
3. Optionally also upload these three files individually alongside the zip (makes them directly browsable without unzipping):
   - `tap/core.csv`
   - `schema/core.schema.json`
   - `docs/README.md`

---

## Step 5 — Fill in the metadata form

Use `.zenodo.json` as your reference. Paste into the form:

| Field | Value |
|---|---|
| **Upload type** | Dataset |
| **Title** | IMM-Core: Interview Metadata Model — Core Profile |
| **Authors** | Behnam Shad, Klaus · ORCID `0000-0002-3601-9024` · C²DH, University of Luxembourg |
| **Description** | Paste the `description` value from `.zenodo.json` |
| **License** | Creative Commons Attribution 4.0 International |
| **Version** | 1.1.0 (the value in .zenodo.json) |
| **Publication date** | today |
| **Keywords** | interview metadata; qualitative research; oral history; metadata model; FAIR data; GDPR; DCTAP; JSON Schema; Dublin Core; REFI-QDA; QDPX; schema.org; minimal metadata; research data management |
| **Related identifier** | `https://gitlab.uni.lu/c2dh/lhi/luxoh-cmdi` · relation: *is supplemented by* · type: Dataset |
| **Notes** | DCTAP-as-SSoT: tap/core.csv is authoritative; schema/core.schema.json is a derived artefact. Working repository: https://github.com/klausbehnamshad/imm-core |

**Communities** — apply via the Communities tab (applications are reviewed; approval can happen post-publication):
- `dariah`
- `clarin`

---

## Step 6 — Preview and publish

1. Click **Preview** — confirm the DOI shown is `10.5281/zenodo.20507329`.
2. Confirm author name, ORCID, and affiliation.
3. Click **Publish**. The record is now live and immutable.

> **Post-publication corrections:** Zenodo lets you edit metadata (title, description, keywords) without creating a new version — use **Edit** on the published record. To change files, you must create a new version (new DOI). The original version and its DOI are always preserved.

---

## Publishing a new version (1.1.0 and later)

Zenodo versions are immutable; a file change needs a new version with its own DOI. The concept DOI 10.5281/zenodo.20507329 keeps resolving to the latest version.

1. Merge the release branch into `main`; CI must be green.
2. From `main`, build the bundle (Step 3 with the new version number) and open the published record on Zenodo, then click **New version**.
3. Upload the bundle (Step 4), fill the form from `.zenodo.json` (Step 5; version and description are already updated on `main`), preview and publish (Step 6).
4. Post-publication: set `date-released` in `CITATION.cff`, `publication_date` in `.zenodo.json` and the date in the `CHANGELOG.md` heading to the Zenodo publication date; commit on `main` with message `chore: release 1.1.0, Zenodo publication date`; tag `v1.1.0` on that commit and push the tag.
5. `.zenodo.json` and this guide stay out of the bundle.

---

## Step 7 — Post-publication: update the working repository

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

## Checklist

### v1.0 (published 2026-06-02)

- [x] Step 1: Draft created, DOI `10.5281/zenodo.20507329` reserved
- [x] Step 2: DOI filled in all files
- [x] Step 3: bundle created
- [x] Step 4: files uploaded
- [x] Step 5: metadata form filled, communities applied
- [x] Step 6: preview checked, published
- [x] Step 7: working repo committed, badge added, `v1.0` tag pushed

### v1.1.0

- [ ] Release branch merged into `main`, CI green
- [ ] `imm-core-v1.1.0.zip` built from `main`
- [ ] New version created on Zenodo, files uploaded, form filled from `.zenodo.json`
- [ ] Preview checked, published
- [ ] Dates set in `CITATION.cff`, `.zenodo.json`, `CHANGELOG.md`; commit on `main`
- [ ] `v1.1.0` tag pushed
