# Zenodo Publishing Guide — IMM-Core v1.0

**DOI:** https://doi.org/10.5281/zenodo.20507329

**Status:** Steps 1 and 2 are complete — the DOI has been reserved and all files updated. Continue from Step 3.

---

## ✅ Step 1 — Create draft deposit and reserve DOI *(done)*

Draft created at https://zenodo.org. DOI reserved: `10.5281/zenodo.20507329`.

## ✅ Step 2 — Update files with real DOI *(done)*

All `XXXXXXX` instances replaced with `20507329` across:
`README.md`, `docs/README.md`, `schema/core.schema.json`, `CITATION.cff`.

---

## Step 3 — Prepare the upload bundle

From the `colloquium-align/` directory, run:

```bash
zip -r imm-core-v1.0.zip \
  README.md LICENSE CITATION.cff CHANGELOG.md \
  tap/core.csv schema/core.schema.json \
  vocabs/ profiles/ crosswalks/ \
  examples/core-generic.json examples/core-luxoh.json \
  methodological-positions/ docs/
```

**Excluded** (do not upload): `tap/minimal-metadata.csv`, `schema/minimal-metadata.schema.json`, `examples/klaus-record.json`, `.zenodo.json`, `ZENODO-PUBLISHING-GUIDE.md`.

---

## Step 4 — Upload files to the Zenodo draft

1. Open your draft at https://zenodo.org/uploads.
2. Upload `imm-core-v1.0.zip`.
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
| **Version** | 1.0 |
| **Publication date** | today |
| **Keywords** | interview metadata; qualitative research; oral history; metadata model; FAIR data; GDPR; DCTAP; JSON Schema; Dublin Core; REFI-QDA; QDPX; schema.org; minimal metadata; research data management |
| **Related identifier** | `https://gitlab.uni.lu/c2dh/lhi/luxoh-cmdi` · relation: *is supplemented by* · type: Dataset |
| **Notes** | DCTAP-as-SSoT: tap/core.csv is authoritative; schema/core.schema.json is a derived artefact. Working repository: https://github.com/kbehnamshad/imm-core |

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

- [x] Step 1: Draft created, DOI `10.5281/zenodo.20507329` reserved
- [x] Step 2: DOI filled in all files
- [ ] Step 3: `imm-core-v1.0.zip` created
- [ ] Step 4: Files uploaded to draft
- [ ] Step 5: Metadata form filled, communities applied
- [ ] Step 6: Preview checked, published
- [ ] Step 7: Working repo committed, badge added, `v1.0` tag pushed
