# Changelog — IMM-Core

All notable changes to IMM-Core are documented here.  
Format: [Semantic Versioning](https://semver.org/). Breaking changes are marked **[BREAKING]**.

---

## [1.0.1] — Unreleased

Consistency and correctness fixes. No field is added, removed or renamed; every record that met the v1.0 documentation still validates.

### Schema (`schema/core.schema.json`) and DCTAP (`tap/core.csv`)

- `consent_status: withdrawn` now requires `accessRights: closed` (`if`/`then`). The rule was a MUST in `vocabs/consent_status.md` but not machine-checked.
- `interview_date`: added `pattern` `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`, so the date shape is checked even by validators that treat `format` as an annotation only.
- `record_id`, `interviewer`, `consent_status`, `title` and each `keywords` item must be non-empty (`minLength: 1`). An empty string was valid before, which made "required" meaningless.
- `tap/core.csv` now carries the `language` and `interview_date` patterns and the timecode pattern (in notes). The schema enforced them, but the single source of truth did not list them.
- `interviewer` description aligned between TAP and schema: "Name(s) of the interviewer(s) as a single string".

### Profiles

- IMM-Profile-LuxOH 1.1: `withdrawn` added to the `consent_status` enum. Version 1.0 violated the invariant that `withdrawn` is always available.
- IMM-Profile-Migration 1.1: the recommended `record_id` pattern no longer encodes country, gender and birth year (quasi-identifiers); it follows the Core recommendation. Example `interviewee_display` changed accordingly.

### Documentation

- README quick start: the `ajv-cli` command failed on `"format": "date"`; it now loads `ajv-formats`.
- README: repaired the broken "Implementation Profiles" paragraph.
- "Thirteen fields in four blocks" corrected to three blocks (A–C) with Block D reserved for profiles (README, docs §5, §6, `.zenodo.json`).
- docs §6: removed a dangling reference to "E.1 discussion in project outline".
- docs §9.4: record revisions belong in the record's own history, not in the specification's `CHANGELOG.md`.
- Crosswalks: `language` exports SHOULD convert ISO 639-3 to the shortest BCP 47 tag (`deu` → `de`); the Schema.org `creator` vs. Dublin Core `contributor` difference for `interviewer` is now explained.
- Release date of v1.0 corrected to 2026-06-02 (Zenodo publication date) in this file and in `.zenodo.json`.

### Tooling

- `scripts/check_consistency.py`: checks TAP ↔ schema agreement, validates `examples/*.json` and rejects `tests/invalid/*.json`.
- CI workflow `.github/workflows/validate.yml` runs the check and the README quick start.
- `examples/core-minimal.json`: a record with only the seven required fields.

---

## [1.0] — 2026-06-02

Initial release of IMM-Core (Interview Metadata Model — Core Profile), generalised from LuxOH-CMDI v1.1.

### Core Profile — new in this release

- Thirteen fields across four functional blocks (A Administrative, B Descriptive, C Structural; Block D deferred to Phase 2 but available via profile extension)
- Seven required fields: `record_id`, `interview_date`, `interviewer`, `consent_status`, `accessRights`, `title`, `language`
- Six optional fields: `interviewee_display`, `spatial`, `keywords`, `abstract`, `timecoded_segments`, `related_materials`
- `consent_status`: **[BREAKING vs LuxOH v1.1]** Free string at Core (no enum); `vocabs/consent_status.md` provides recommended cross-domain vocabulary; LuxOH enum (`research-only | teaching | public | embargoed`) now lives in `profiles/luxoh-cmdi.md`
- `accessRights`: enum `open | restricted | closed` enforced at Core
- `record_id`: **[BREAKING vs LuxOH v1.1]** No pattern enforced at Core; LHI pattern now in `profiles/luxoh-cmdi.md`
- `language`: ISO 639-3 three-letter code; regex `^[a-z]{3}$` enforced in schema
- `timecoded_segments`: HH:MM:SS regex enforced on `start` and `end` sub-properties
- `related_materials`: URL/DOI string array, optional, Block C (pulled forward from LuxOH v2.0 roadmap into Core)
- Block D fields (`file_format`, `master`, `access_copy`, `checksum`): **removed from Core**; available via IMM-Profile-LuxOH delta

### Architecture

- Two-layer architecture: Core Profile + Implementation Profiles
- DCTAP (`tap/core.csv`) as single source of truth; JSON Schema (`schema/core.schema.json`) as derived artefact
- Profile conformance rules: extend, never weaken (see `profiles/README.md`)

### Registered profiles (v1.0)

- `IMM-Profile-LuxOH` (`profiles/luxoh-cmdi.md`) — oral history, C²DH, University of Luxembourg
- `IMM-Profile-Migration` (`profiles/generic-interview.md`) — migration-studies sociology reference example

### Documentation and support files

- Full conceptual documentation (`docs/README.md`), §1–§11
- Three crosswalks: Dublin Core (`crosswalks/dublin-core.md`), REFI-QDA/QDPX (`crosswalks/qdpx.md`), Schema.org/Dataset (`crosswalks/schema-org-dataset.md`)
- Methodological position paper on the descriptive abstract (`methodological-positions/abstracts.md`)
- Recommended consent vocabulary (`vocabs/consent_status.md`)
- Two example records (`examples/core-generic.json`, `examples/core-luxoh.json`)

---

## Relationship to LuxOH-CMDI

IMM-Core v1.0 is generalised from LuxOH-CMDI v1.1 (hosted on GitLab at C²DH). The breaking changes above are the moves that make the Core discipline-agnostic; they are design decisions, not corrections. LuxOH-CMDI continues as IMM-Profile-LuxOH, adding back the institution-specific constraints via the profile delta.

## Versioning policy

| Change type | Version impact |
|---|---|
| New required field; field removal; tightened `accessRights` enum | MAJOR |
| New optional field; loosened optional-field constraint | MINOR |
| Documentation or description correction without semantic change | PATCH |
