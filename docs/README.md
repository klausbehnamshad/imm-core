# IMM-Core: Interview Metadata Model — Core Profile

**Version:** 1.0  
**License:** CC-BY-4.0  
**DOI:** 10.5281/zenodo.20507329  
**Citation:** Behnam Shad, Klaus (2026). *IMM-Core: Interview Metadata Model — Core Profile* (v1.0). Zenodo. https://doi.org/10.5281/zenodo.20507329

---

## Table of Contents

1. Introduction: metadata as epistemic infrastructure
2. Minimal-as-methodology
3. FAIR and GDPR as operational frames
4. Relationship to existing standards
   - 4.1 Dublin Core
   - 4.2 CMDI
   - 4.3 Schema.org/Dataset
   - 4.4 REFI-QDA / QDPX
5. Two-layer architecture
6. The four functional blocks
7. Methodological awareness
8. Workflow integration
9. Common errors
10. Governance and versioning
11. Roadmap (Phase 2) — principled extensions

---

## 1. Introduction: Metadata as Epistemic Infrastructure for Interview-Based Research

An interview becomes a citable research object the moment it acquires a stable identifier, a rights-governed access status, and a minimal description that allows another researcher to find it, evaluate its relevance, and decide whether to request access. Before that point, it is a recording — valuable, perhaps irreplaceable, but not yet a legible element of the scholarly record.

This is not merely a technical observation. Metadata is the scaffold that transforms a raw audiovisual file into an archival entity: it grounds the interview in a specific time, place, and social context; it documents the conditions under which the material was produced and the terms under which it may be used; and it creates the stable reference that makes citation, replication, and secondary analysis possible. Without metadata, oral and qualitative sources cannot participate in the cumulative, peer-reviewed knowledge-building that defines scholarship.

IMM-Core is a minimal metadata model for interview-based qualitative research. It is designed to be generic across disciplines — oral history, sociology, anthropology, education, migration studies, health research, political science — and agnostic with respect to qualitative data analysis (QDA) tradition. It does this by occupying a precise niche: the *descriptive metadata layer*, the level at which the interview is described as a research object, prior to and independently of whatever analytic work is done on it.

The model has two layers. The **Core Profile** (this document) specifies the generic, discipline-agnostic minimum. **Implementation Profiles** specialise the Core for particular disciplines or institutions by adding fields, imposing controlled vocabularies, and tightening constraints. LuxOH-CMDI — the Luxembourg oral history institutional model from which IMM-Core was generalised — is one such Implementation Profile (see `profiles/luxoh-cmdi.md`).

---

## 2. Minimal-as-Methodology

Choosing a minimal model is a methodological position, not a stage on the way to something more complete.

Four imperatives converge on minimality:

**Specificity.** The model must include enough information to support discovery, rights management, and basic scholarly citation. Every field in the Core exists because it is load-bearing for at least one of these functions. Fields that are useful but not load-bearing are optional; fields that belong to a specific discipline are in profiles.

**Cognitive simplicity.** A model that requires fifteen mandatory fields will not be consistently populated by interdisciplinary research teams, student researchers, or archivists under time pressure. Metadata that exists only in the schema and never in the records is worse than no schema, because it creates a false sense of coverage. The Core requires seven fields. This is not an accident.

**Ethical clarity.** GDPR's principle of data minimisation applies to metadata about research participants as much as to the primary data itself. A metadata model that collects granular personal information about interviewees in the name of discoverability creates a privacy risk that no research benefit can straightforwardly justify. The Core's minimal speaker hook (`interviewee_display` — a pseudonym or display name) deliberately sits below the threshold of personal data while providing enough descriptive anchor for the record.

**Interoperability.** Fewer, better-defined fields crosswalk more cleanly to Dublin Core, Schema.org, and DataCite than many fields with ambiguous external mappings. Every Core field has a plausible external mapping; the crosswalk files in `crosswalks/` document where those mappings hold and where they break down.

Minimality is the *destination*, not a temporary compromise. The Phase 2 roadmap (§11) exists to keep future extensions principled when they happen, not to apologise for v1.0.

---

## 3. FAIR and GDPR as Operational Frames

The FAIR principles (Findable, Accessible, Interoperable, Reusable — Wilkinson et al., 2016) and the EU General Data Protection Regulation are sometimes portrayed as in tension: FAIR pushes toward openness and discoverability; GDPR constrains what can be disclosed about research participants. In practice, for interview-based qualitative research, they are mutually reinforcing.

**Findable.** `record_id` provides the stable unique identifier that FAIR F1 requires. `title`, `keywords`, and `abstract` support the rich metadata that F2 and F3 require. `language` and `spatial` enable filtering and scoped discovery.

**Accessible.** `accessRights` (`open | restricted | closed`) directly implements the A1 and A2 conditions: data is accessible under well-defined conditions, even when those conditions include access controls. A `restricted` record is accessible — under specified terms — which is FAIR-compliant. A record with no `accessRights` declaration is not.

**Interoperable.** The crosswalk files document how Core fields map to Dublin Core, Schema.org, and QDPX. The JSON Schema enables machine-readable validation. The DCTAP profile provides a metadata-standard-agnostic specification of field semantics.

**Reusable.** `consent_status` documents the participant-consent basis for reuse — a precondition for legally defensible secondary analysis. GDPR Art. 5(1)(c) requires that personal data be "adequate, relevant, and limited to what is necessary." The Core's minimality is a direct implementation of this principle.

Minimal metadata is not in tension with reusability. It is a precondition for *legally defensible* reusability. A research data record that collects unnecessary personal detail about participants may technically satisfy FAIR findability while creating GDPR liability. The Core is designed so that no field creates a data-minimisation problem when properly populated.

---

## 4. Relationship to Existing Standards

IMM-Core occupies a specific niche in the metadata landscape. It is not a replacement for any of the following standards; it is a specialised layer that complements them.

### 4.1 Dublin Core

Dublin Core Metadata Terms (DCTERMS) provides the semantic baseline from which IMM-Core's descriptive fields are drawn. `title`, `language`, `abstract` (as `description`), `identifier`, `date`, and `contributor` all have direct DC equivalents. The full field-by-field crosswalk is in `crosswalks/dublin-core.md`.

**Boundary.** Dublin Core is too thin for interview-specific rights and consent. It has no property for consent status, no controlled vocabulary for access rights at the GDPR level, and no way to represent structural interview data. IMM-Core uses DC as a semantic baseline and adds the discipline-specific layer on top.

### 4.2 CMDI

The Component Metadata Infrastructure (CMDI), developed within the CLARIN research infrastructure, provides a modular component framework for language-resource metadata. LuxOH-CMDI was originally developed as a CMDI-compatible profile, and the modular logic of CMDI — components can be combined, constrained, and specialised — directly informs IMM-Core's two-layer architecture. An institution with CLARIN infrastructure can express an IMM-Core Implementation Profile as a CMDI component; an institution without that infrastructure can implement the same profile as a JSON Schema and a DCTAP file.

**Boundary.** CMDI as a whole requires a CLARIN Centre or equivalent institutional host for component registration, schema deployment, and VLO harvesting. IMM-Core borrows the modular logic without requiring the full CMDI stack.

### 4.3 Schema.org/Dataset

The Schema.org `Dataset` type, embedded as JSON-LD in repository landing pages, provides web-level findability via Google Dataset Search and related structured-data harvesters. The mapping is in `crosswalks/schema-org-dataset.md`.

**Boundary.** Schema.org/Dataset is not a research-grade rights vocabulary. It carries no consent property and no controlled access-rights vocabulary that maps to GDPR categories. The JSON-LD serialisation is a discoverability exposure layer only.

### 4.4 REFI-QDA / QDPX

The REFI-QDA Project Exchange Format (QDPX) provides a portable XML format for qualitative analysis projects: codes, memos, annotations, source documents, and the links between them. It is supported by ATLAS.ti, NVivo, MAXQDA, Dedoose, and other major QDA packages.

IMM-Core and QDPX are designed to coexist at adjacent layers:

| Domain | IMM-Core | QDPX |
|---|---|---|
| Interview identity, date, rights, consent | ✓ | ✗ |
| Descriptive abstract | ✓ | ✗ |
| Timecoded structural segmentation | ✓ (descriptive) | ✓ (analytic) |
| Keywords / subject terms | ✓ (pre-analytic) | ✓ (codes) |
| Language | ✓ (source-level) | ✓ (code-level) |
| Transcript text | ✗ (Phase 2) | ✓ |
| Codes, code trees | ✗ | ✓ |
| Memos, annotations | ✗ | ✓ |
| Source–code links | ✗ | ✓ |
| Analytic provenance | ✗ | ✓ |

The recommended handoff convention — matching QDPX `<Source>` identifiers to IMM-Core `record_id` values, and linking QDPX exports via `related_materials` — is documented in `crosswalks/qdpx.md`.

**Boundary.** Neither system is a substitute for the other. QDPX does not solve the problem of citable, rights-governed, cross-repository-discoverable interview records. IMM-Core does not solve the problem of portable analytic structure. The strategic claim here is that these systems are designed to coexist at adjacent layers, not to compete for the same territory.

---

## 5. Two-Layer Architecture

IMM-Core uses a two-layer architecture: a **Core Profile** and **Implementation Profiles**.

**Core Profile** (this specification): generic, discipline-agnostic, methodologically neutral. Thirteen fields across four functional blocks. Seven required. No discipline-specific vocabularies enforced except `accessRights` (which is genuinely cross-domain stable). `tap/core.csv` is the single source of truth; `schema/core.schema.json` is the derived machine-readable mirror.

**Implementation Profiles**: discipline-specific or institution-specific specialisations. Each profile is expressed as a DCTAP delta (only fields that differ from or are added to Core) and a JSON Schema fragment. Profiles may add fields, tighten constraints, and impose controlled vocabularies. Profiles may not remove Core-required fields, loosen the `accessRights` enum, or override Core field semantics.

The architecture is governed by a single invariant: **profiles extend, never weaken**. DCTAP-as-SSoT holds at both layers. The Core DCTAP and the profile's DCTAP delta together constitute the complete specification for any profile. CI pipelines validate records against the relevant schema at commit time.

Registered profiles and registration instructions are in `profiles/README.md`. The naming convention is `IMM-Profile-{Slug}`.

---

## 6. The Four Functional Blocks

Any interview metadata record must cover four domains regardless of discipline or serialisation format. IMM-Core organises its thirteen fields into four blocks:

**Block A — Administrative.** Identity, provenance, and rights. Required: `record_id`, `interview_date`, `interviewer`, `consent_status`, `accessRights`. These five fields make the interview citable and rights-governable; no interview record is complete without them.

- `record_id`: stable identifier. Recommended format `YYYY-MM-DD_{INSTITUTION_CODE}_{NNNN}`. Pattern not enforced at Core; profiles impose institution-specific patterns. *Not in Core by design:* no UUID mandate, no namespace registry — implementation policy belongs in profiles.
- `interview_date`: ISO 8601 date (YYYY-MM-DD). *Not in Core:* date ranges, approximate dates — deferred to Phase 2.
- `interviewer`: name string; ORCID in parentheses recommended. *Not in Core:* multi-interviewer objects, institutional affiliation — deferred to Phase 2.
- `consent_status`: free string at Core; see `vocabs/consent_status.md` for recommended vocabulary. *No enum at Core:* discipline-specific consent regimes belong in profiles (see E.1 discussion in project outline).
- `accessRights`: `open | restricted | closed`. *This enum is enforced at Core level* because it is genuinely cross-domain stable — OpenAIRE, Zenodo, and DataCite all use it — and is the minimum for machine-readable access governance.

**Block B — Descriptive.** Content and context. Required: `title`, `language`. Optional: `interviewee_display`, `spatial`, `keywords`, `abstract`.

- `title`: interview title or descriptive label.
- `language`: ISO 639-3 three-letter code. Single language at Core; multilingual deferred to Phase 2.
- `interviewee_display`: pseudonym or display name. The Core's minimal speaker hook. *Not in Core by design:* demographics, life-history data — full speaker component deferred to Phase 2. Privacy-principled: the Core does not collect personal data about participants beyond the minimum for description.
- `spatial`: place of interview, free string. *Not in Core:* controlled place-name lists — geography-specific, profile-level.
- `keywords`: free string array. *Not in Core:* a specific controlled vocabulary — profile-level.
- `abstract`: 2–3 sentence descriptive summary. See `methodological-positions/abstracts.md` for scope constraints. *Not in Core:* analytic content, codes, themes — above Core by design.

**Block C — Structural.** Internal organisation. Both fields optional.

- `timecoded_segments`: array of `{start, end, label}` objects in HH:MM:SS. Descriptive segmentation for navigation. *Not in Core:* analytic coding, transcription — QDPX territory.
- `related_materials`: array of URL/DOI strings for transcripts, companion documents, derived files.

**Block D — Preservation.** File-format, master-copy, checksum, and access-copy fields. *Absent from Core v1.0 by design.* Block D is a profile-level concern: LuxOH-CMDI adds it via IMM-Profile-LuxOH. The Core's mandate stops at the descriptive-metadata layer; preservation metadata is infrastructure-specific and belongs in profiles.

---

## 7. Methodological Awareness

IMM-Core does not privilege any QDA tradition. It makes this claim because it sits below the analytic layer: it describes what an interview is, not what it means. That is an assertion that requires demonstration. For each major tradition, the question is: which Core fields carry that tradition's descriptive needs, and what does the tradition do above Core that Core cannot and should not carry?

**Biographical narrative (Schütze).** Setting and sequencing are central: the Nachfrageteil structure, the sequential reconstruction of life phases, the interplay between Erlebniserzählung and Argumentation all depend on accurate contextual description. Core fields: `spatial`, `interview_date`, `timecoded_segments` (rough segmentation), `abstract` (broad narrative arc). What this tradition needs that Core does not provide: segment-level narrative-type annotation (narrative segment / descriptive segment / argumentation / evaluation) — analytic, above Core.

**Qualitative content analysis (Mayring).** Corpus delimitation is the first methodological step. Core fields: `record_id`, `language`, `keywords` (pre-analytic subject-matter bounding). What this tradition needs that Core does not provide: the category system — whether deductive or inductive, categories and subcategories are analytic constructs that live in QDPX or researcher notes, not in descriptive metadata.

**Constructivist grounded theory (Charmaz).** The reflexivity of the cataloguer is itself a grounded-theory move. The decision to separate descriptive from analytic abstract — which the Core enforces — is the model's most Charmaz-resonant design choice. Core fields: the entire record, understood as the researcher's act of constituting the interview as an object. What this tradition needs that Core does not provide: theoretical memos, memo-to-data links, theoretical saturation markers — all above Core, all in QDPX.

**Documentary method (Bohnsack).** The most underserved tradition in Core v1.0. Recording context — group composition, atmosphere, degree of acquaintance, setting as a participant-produced situation — is methodologically significant in ways it is not in most other traditions. Core fields: `spatial`, `interview_date`, `abstract` (if the cataloguer notes group-interview format). What this tradition needs that Core does not provide: structured recording-context field, group-composition metadata, interactional-atmosphere descriptors. This is the known gap; flagged in the Phase 2 roadmap (§11).

**Interpretative phenomenological analysis (IPA).** IPA's idiographic commitment — the individual case as unit of analysis — is reflected in the Core's design choice not to require corpus-level aggregation fields. Core fields: `interviewee_display` (individual pseudonym), `abstract` (subject of inquiry as experienced by this individual). What this tradition needs that Core does not provide: experiential-theme annotations and interpretive commentary layers — above Core scope entirely.

**Discourse analysis.** Language is the object of inquiry, not merely its medium. Core fields: `language`, `abstract` (interactional context and speech-event type). What this tradition needs that Core does not provide: transcription conventions and transcript metadata (GAT 2, Jefferson notation) — these live with the transcript files, referenced via `related_materials`, not in descriptive metadata.

The pattern across traditions is consistent: Core covers the descriptive context of the interview as an object; each tradition's analytic apparatus operates above Core in QDA software, memos, and QDPX exports. The Core does not attempt to be any of those tools. That is not a limitation; it is the argument.

---

## 8. Workflow Integration

IMM-Core fields are populated incrementally across the research pipeline. The model is agnostic to which roles fill which block at which stage; the following sequence is typical.

**Researcher.** Fills Block A at the point of recording or immediately after: `record_id`, `interview_date`, `interviewer`, `consent_status`, `accessRights`. Fills Block B descriptive fields (`title`, `language`, `spatial`, `interviewee_display`) at or near the time of recording. Completes `keywords` and `abstract` during or after transcription/review. Adds `related_materials` URLs as derivative files become available.

**Project lead.** Validates Block A against project-level consent documentation. Confirms `accessRights` against institutional agreements. Reviews `abstract` for inadvertent re-identification risk.

**Repository manager.** Validates the complete record against the relevant schema (Core or profile). Assigns or confirms `record_id` if the institution manages identifiers centrally. Deposits to repository. Adds Block D preservation fields if the Implementation Profile (e.g. IMM-Profile-LuxOH) requires them.

No IMM-Core field requires a specific institutional system. The model operates with any workflow that can produce a JSON record and validate it against a JSON Schema.

---

## 9. Common Errors

**1. `abstract` contains analytic content.** The most common error. Categories, themes, interpretations, and comparisons to other interviews do not belong in the Core abstract. See `methodological-positions/abstracts.md`.

**2. `consent_status` and `accessRights` are conflated.** These are distinct fields: `consent_status` records what the participant agreed to; `accessRights` records the repository's current access policy. They should be set independently. A record may have `consent_status: research-only` and `accessRights: open`, or `consent_status: public` and `accessRights: restricted` (pending review).

**3. `language` is not ISO 639-3.** Using BCP 47 tags (`en`, `de`), two-letter ISO 639-1 codes, or natural-language names (`English`, `German`) instead of ISO 639-3 three-letter codes (`eng`, `deu`) breaks machine-readable filtering. The Core schema enforces a three-letter lowercase pattern.

**4. `record_id` is not stable.** Record identifiers must not be reassigned. If a record is revised, the `record_id` stays the same; changes are documented in `CHANGELOG.md`. Changing identifiers silently breaks external references and citations.

**5. `timecoded_segments` labels are analytic.** Labels like "Charmaz node 3" or "core category: belonging" belong in QDA software, not in the structural segmentation layer. Labels should describe what happens in the segment at a factual level: "Childhood and migration background", "Discussion of work conditions".

**6. `keywords` conflate subject terms with analytic codes.** Keywords describe the subject-matter of the interview for discovery purposes, not the analytic conclusions drawn from it. This is a specific case of the descriptive-vs-analytic distinction.

**7. Profile-specific fields used in Core records without declaring the profile.** A record including `file_format` or `study_id` — fields defined in profile deltas — without validation against the relevant profile schema will fail Core schema validation (`additionalProperties: false`). Profile-specific fields are only valid in records validated against the relevant profile schema.

---

## 10. Governance and Versioning

**Core versioning** uses Semantic Versioning (SemVer: `MAJOR.MINOR.PATCH`).

| Change type | Version impact |
|---|---|
| New required field; tightened `accessRights` enum; field removal | MAJOR |
| New optional field; loosened optional-field constraint | MINOR |
| Documentation or description correction without semantic change | PATCH |

**DCTAP-as-SSoT.** `tap/core.csv` is authoritative. `schema/core.schema.json` is derived. If they diverge, the DCTAP is correct. CI pipelines on working repositories should validate their consistency.

**Zenodo deposits are immutable snapshots.** Each Zenodo release is a tagged version. Breaking changes produce a new DOI on the new major version. `CHANGELOG.md` documents all changes between versions.

**Profile versioning.** Profiles are versioned independently from Core. Each profile declares the Core version it targets (e.g. `imm-core: "^1.0"`). A Core major-version bump does not automatically invalidate profiles, but profile maintainers must verify compatibility.

**Governance.** In v1.0, Klaus Behnam Shad (C²DH, University of Luxembourg) is the sole author and maintainer. Community governance (steering group, RFC process, public GitHub mirror) is scheduled for Phase 2 once the Core has been adopted by at least two independent Implementation Profiles outside the original institutional context.

---

## 11. Roadmap (Phase 2) — Principled Extensions

Phase 2 items address genuine layers of interview-metadata work that v1.0 deliberately defers. Each is deferred not because it is unimportant, but because the design choices it requires are not yet stable across disciplines.

**Block D — Preservation fields** (`file_format`, `master`, `access_copy`, `checksum`). Deferred because they are infrastructure-specific: what counts as a master copy and how checksums are generated depends on institutional systems (CatDV, Dataverse, DSpace). Already implemented in IMM-Profile-LuxOH as a profile-level extension.

**Speaker component** (demographics, life-history fields, role). Deferred because: (a) speaker metadata is the highest-privacy layer of interview records; (b) what demographic fields are relevant varies sharply by discipline; (c) the Core's `interviewee_display` provides the minimal hook needed without prescribing the full component.

**Multilingual interviews** (`language` as array; language-per-segment). Deferred because ISO 639-3 arrays and mixed-language segmentation require a more complex data structure than the current single-value field. Single-language interviews are the common case; the design for multi-language support should be validated against real multilingual corpora before being added.

**Transcript provenance** (ASR-generated vs. manual; human review status). Deferred because transcript-level metadata belongs closer to the transcript file itself than to the interview record, and the correct home (Core field vs. transcript sub-record vs. QDPX source metadata) requires design work. Note: IMM-Core v1.0 does not specify transcript provenance, but implementers working with ASR-generated or LLM-assisted transcripts should document the generation method in their institutional workflow metadata. Presenting AI-generated content as primary data without disclosure is an epistemic integrity issue regardless of schema version.

**Recording-context fields** (setting structure, group composition, interactional atmosphere). Deferred because this is the most tradition-specific layer — essential for documentary method (Bohnsack), much less relevant for IPA. A Phase 2 design should involve consultation with communities using Bohnsack's framework and related approaches.

**Community governance** (steering group, RFC process, public GitHub mirror). Deferred until the Core has been adopted by at least two independent Implementation Profiles. The Zenodo deposit is the first step toward community infrastructure.

Deferral is a stance, not a delay.
