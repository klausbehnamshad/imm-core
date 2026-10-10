# Changelog — IMM-Core

All notable changes to IMM-Core are documented here.  
Format: [Semantic Versioning](https://semver.org/). Breaking changes are marked **[BREAKING]**. One local deviation from strict SemVer: a rule tightened on an existing field is released as MINOR and listed explicitly with its test fixtures (see Versioning policy below).

---

## [Unreleased]

Intended release: 1.2.0 (MINOR): one new optional field (`languages`); no field removed, no new required field, `language` stays a single string. Entries before 1.2.0 use the profile names of their time; the institutional profile lapses with 1.2.0 and its earlier descriptions are historical statements. No new DOI or publication is claimed here; the citations below name the last published version (1.1.0) as such.

### Added

- `languages` (Block B, optional): array of ISO 639-3 codes listing every spoken language of the interview; `minItems: 1`, `uniqueItems: true`, MUST contain the value of `language` (checked by `tools/validate.py`, rule R2). Spoken languages only: no subtitle or translation languages, no language per segment.
- Schema fixtures: `tests/invalid/languages-not-a-code.json`, `tests/invalid/languages-empty.json`, `tests/invalid/languages-duplicate.json`, `tests/invalid/languages-wrong-type.json`, `tests/invalid/timecode-minute-61.json`, `tests/invalid/timecode-second-60.json`.

### Changed

- `record_id`: collection wording (`{COLLECTION_CODE}`, collection-specific patterns); assigned once by the system that holds the collection, carried unchanged by exports. Existing identifiers stay valid; no global date pattern.
- `interviewer` and `interviewee_display`: several persons separated by `; `. `interviewee_display` is never filled automatically from a real name. A comma alone proves no person list (rule R5 warns only).
- `timecoded_segments`: chapter marks; subtitles go as WebVTT per language via `related_materials`; frames are truncated to seconds by the producing system. Timecode minutes and seconds range 00–59 in TAP note and schema.
- `consent_status`: collections keep their permitted values in tool configuration (`docs/implementing.md`); the Core stays a free string and `withdrawn` still implies `accessRights: closed`.
- Documentation: Block B lists `languages`; §9 names the `languages` error; §11 describes multilingual handling since 1.2.0; `vocabs/consent_status.md` lists `languages` among the fields a withdrawn record SHOULD drop. Field count is now fifteen in `README.md`, `docs/README.md` (§5, §6) and `.zenodo.json`.
- `examples/core-luxoh.json` is now `examples/core-oral-history.json` with invented collection code (`record_id` `2024-05-18_OHX_0042`, `governance_ref` `urn:example:governance:ohx-0042`) and a valid `languages` pair.
- Crosswalks: Dublin Core, Schema.org and QDPX carry the `languages` mapping and the `1.2.0 (unreleased)` head; the Schema.org example uses the new example identifier.
- `.zenodo.json`: notes say "versioned snapshot"; the predecessor `related_identifiers` entry is removed. `CITATION.cff` abstract no longer names the lapsed profile. Version, dates and DOIs stay at the published 1.1.0 until the separate release.

### Removed

- `profiles/luxoh-cmdi.md`: the institutional profile lapses; collections use the Core with tool configuration. The historical entries below keep their names.

### Implementers

- Consumers with `additionalProperties: false` and the old schema reject records carrying `languages`; they need their own upgrade path.
- Tighter timecode (00–59) and blank-text checks can hold back faulty records that earlier validators accepted.
- Raw schema validation does not enforce the cross-field `languages` rule; run `tools/validate.py`.

### Documentation

- Citation metadata after the Zenodo publication of 1.1.0: `CITATION.cff` and the citation lines in `README.md` and `docs/README.md` cite version 1.1.0 (10.5281/zenodo.23190815); the concept DOI for all versions is 10.5281/zenodo.20507328. 10.5281/zenodo.20507329 is the DOI of version 1.0 and stays with it.
- `docs/README.md`: unreleased marker removed; the versioning table lists the MINOR row for tightened rules; the schema `$id` is described as a stable identifier.
- Section 1.1.0 below: the summary now names all four classes of records that were valid under v1.0 and are not under 1.1.0. Two test fixtures added for the classes that had none (`tests/invalid/keywords-empty-item.json`, `tests/invalid/date-wrong-shape.json`); no schema rule changes.
- `docs/README.md` and `vocabs/consent_status.md`: statements on pseudonymisation, FAIR accessibility, data minimisation, anonymisation criteria and legal basis reworded as descriptions with sources; the Core makes no legal assessment.
- `tap/core.csv` and `schema/core.schema.json`: `consent_status` description no longer calls the value a GDPR-based category (description only, no rule change).
- Crosswalks: `governance_ref` is an internal reference and is omitted from Dublin Core and Schema.org exports; the Schema.org example uses a synthetic interviewer and an example.org address.
- `ZENODO-PUBLISHING-GUIDE.md`: DOI roles, 30-day file correction window, version field, 1.1.0 checklist.
- Naming: `CITATION.cff`, `.zenodo.json`, `docs/README.md` and `profiles/luxoh-cmdi.md` refer to the institutional predecessor model instead of its former name; file names and URLs are unchanged.

## [1.1.0] — 2026-10-06

Zenodo: https://doi.org/10.5281/zenodo.23190815 (this version); all versions: https://doi.org/10.5281/zenodo.20507328.

Consistency and correctness fixes. One optional field is added (`governance_ref`). No field is removed or renamed. The schema now enforces that required strings and `keywords` entries are non-empty, that `interview_date` has the form YYYY-MM-DD also in validators without format checking, and that `withdrawn` implies `accessRights: closed`. Records that relied on an empty required string, an empty `keywords` entry, `withdrawn` without `closed`, or (in validators without format checking) another date form validated against the published v1.0 schema and no longer do. `tests/invalid/empty-title.json` and `tests/invalid/withdrawn-not-closed.json` document the empty-string and withdrawal cases; the fixtures for the empty-keyword and date-form cases (`tests/invalid/keywords-empty-item.json`, `tests/invalid/date-wrong-shape.json`) were added after the release (see Unreleased).

### Added

- `governance_ref` (Block A, optional): stable reference to the governance record documenting the decisions applying to an interview; internal reference, must not be exported as a public link.
- `vocabs/consent_status.md`: case-sensitivity of `consent_status` values and withdrawn-record guidance (retain only required fields plus `governance_ref`; descriptive fields should be removed).
- `docs/README.md`: corrected pseudonymisation wording, FAIR A1/A1.2/A2 access wording and data-minimisation wording; new `Disclosure risk of descriptive fields` paragraph with three profile check questions; synthetic LuxOH example record.

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

### Implementers

Vendored copies of `tap/core.csv` and `schema/core.schema.json` should be refreshed. `governance_ref` is an internal reference and belongs on an export denylist by default.

### Release checklist (maintainer)

Set date-released in CITATION.cff and publication_date in .zenodo.json to the Zenodo publication date.
Replace "Unreleased" in this heading with that date.
Tag the version on the commit that sets the publication date; earlier versions keep their DOIs, Zenodo mints a new version DOI.

---

## [1.0] — 2026-06-02

Initial release of IMM-Core (Interview Metadata Model — Core Profile), generalised from the institutional predecessor model, version 1.1.

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

## Relationship to IMM-Profile-LuxOH

IMM-Core v1.0 is generalised from the institutional predecessor model, version 1.1, hosted on GitLab at C²DH. The breaking changes above are the moves that make the Core discipline-agnostic; they are design decisions, not corrections. The Luxembourg model continues as IMM-Profile-LuxOH, adding back the institution-specific constraints via the profile delta.

## Versioning policy

| Change type | Version impact |
|---|---|
| New required field; field removal; tightened `accessRights` enum | MAJOR |
| New optional field; loosened optional-field constraint | MINOR |
| Rule tightened on an existing field so that previously schema-valid records fail | MINOR, listed explicitly with the affected test fixtures |
| Documentation or description correction without semantic change | PATCH |
