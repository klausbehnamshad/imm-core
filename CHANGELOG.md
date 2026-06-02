# Changelog — IMM-Core

All notable changes to IMM-Core are documented here.  
Format: [Semantic Versioning](https://semver.org/). Breaking changes are marked **[BREAKING]**.

---

## [1.0] — 2026-01-01

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
