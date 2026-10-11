# IMM-Core

**A common descriptive layer for interview research.**

**Version:** 1.2.0 · **Published:** 2026-10-11 · **DOI:** [10.5281/zenodo.23295846](https://doi.org/10.5281/zenodo.23295846) · **License:** [CC BY 4.0](LICENSE)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20507328.svg)](https://doi.org/10.5281/zenodo.20507328)

An interview becomes useful for further research when someone can establish which source they are looking at, how it was produced, what it concerns, and under which conditions it may be consulted. That context needs to travel with the recording, transcript and subsequent analysis.

**IMM-Core puts this shared descriptive foundation into a small, explicit, testable record: fifteen fields, seven required.** It combines stable identity, provenance, access and consent information, description, spoken languages, chapter marks and links to related materials. Collection rules handle local vocabularies and existing identifiers; Implementation Profiles support more specialised descriptions.

A useful interview record should survive a new research question, a change of software and a move between repositories. This is the problem IMM-Core addresses.

## Why this matters for Digital Humanities

Interview research brings together historical sources, situated acts of narration and digital objects that are repeatedly transcribed, annotated, translated and re-used. A source may circulate through a collection database, a media workflow, a qualitative analysis package and a repository. Its identity and production context need to remain recognisable at every handover.

Established standards provide important parts of this work. [Dublin Core](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/) supplies descriptive terms. [CLARIN's CMDI components and profiles](https://forum.clarin.eu/t/is-there-a-list-of-recommend-components-and-profiles/443) include an OralHistoryInterview profile. [REFI-QDA/QDPX](https://www.qdasoftware.org/project) supports the exchange of sources, segments, codes and analytical work between QDA applications.

IMM-Core makes a practical choice within this landscape: specify a compact common interview record, publish its meanings and constraints, and document how it relates to other formats. A project can adopt that shared foundation while keeping its collection's identifiers, vocabulary and governance arrangements.

| Research need | IMM-Core design choice | Why it matters |
|---|---|---|
| Recognise the same source across systems | `record_id` is assigned once and carried unchanged through exports | Recording, transcript and analysis can remain connected as tools change. Existing collection IDs are retained. |
| Understand the production of a source | Interview date and interviewer are required; place can be added | The record carries context for source criticism and helps distinguish the interview event from later processing. |
| Make conditions of use explicit | Separate `consent_status`, `accessRights` and optional `governance_ref`; export licensing is configured separately | Consent, access, licence and institutional decisions remain distinguishable. A valid record does not itself authorise reuse. |
| Preserve room for further interpretation | A descriptive `abstract`, subject keywords and chapter labels; analytical coding stays in the analysis layer | Later researchers can approach the source with different questions without inheriting one coding scheme as its basic description. |
| Describe multilingual sources | Main `language` plus optional `languages` for all spoken languages | Multilingual interviews remain visible; spoken languages are kept separate from subtitle and translation languages. |
| Keep the shared model usable | Seven required fields; optional detail; stricter rules belong in profiles or collection configuration | Projects can share a baseline without imposing every local requirement on every other collection. |

## What a Core record contains

The Core has three functional blocks. **A** identifies the interview and records its access/consent context. **B** describes the source. **C** connects its structure and related materials. **Block D, preservation, is reserved for Implementation Profiles.**

| Block | Required | Optional |
|---|---|---|
| A · Administrative | `record_id`, `interview_date`, `interviewer`, `consent_status`, `accessRights` | `governance_ref` |
| B · Descriptive | `title`, `language` | `interviewee_display`, `languages`, `spatial`, `keywords`, `abstract` |
| C · Structural | — | `timecoded_segments`, `related_materials` |

A minimal synthetic record:

```json
{
  "record_id": "2024-05-18_OHX_0042",
  "interview_date": "2024-05-18",
  "interviewer": "Interviewer A",
  "consent_status": "research-only",
  "accessRights": "restricted",
  "title": "Interview on work and migration",
  "language": "deu"
}
```

The identifier shown is an example. A collection can keep an established identifier such as `WALZ-1000` and configure its own pattern. The Core requires a non-empty identifier; it introduces no universal renumbering rule.

For a multilingual interview, add spoken languages as a JSON array:

```json
"language": "deu",
"languages": ["deu", "ltz"]
```

The main language must be included in `languages`. Records use ISO 639-3 codes; target formats may need another representation, which is handled at the export boundary.

## Description, governance and analysis

**Description supports source criticism.** The `abstract` describes the interview as a research object; `timecoded_segments` describes chapter marks. Transcripts, subtitles and QDPX projects are separate materials linked through `related_materials`. WebVTT can carry subtitles per language. Research codes, memos and interpretive annotations stay in their analysis environment.

**Governance has an identifiable location.** `governance_ref` can point to the institutional record of the decisions that apply to an interview. It is an internal reference and must be excluded from public-link exports. The Core neither duplicates nor evaluates the referenced decision. Inspection of that decision depends on the institution's access arrangements.

**A public projection is a deliberate selection.** A collection may need detailed internal metadata while exposing fewer fields for discovery. The offline Dataverse converter excludes `governance_ref`, `consent_status`, `interviewee_display`, `timecoded_segments` and the `accessRights` field. Export of the identifier and interviewer is off by default and requires explicit configuration. Selection, licensing and review of the proposed public output remain collection decisions.

Validation checks the record. Institutional processes establish its permitted uses.

## Specification and validation

[`tap/core.csv`](tap/core.csv) is the authoritative DCTAP specification. [`schema/core.schema.json`](schema/core.schema.json) is its machine-readable mirror. [`tools/validate.py`](tools/validate.py) applies the schema and rules R1–R8, including the cross-field language rule, chapter chronology, collection-specific identifiers and blank-text checks. Warnings remain distinct from failures.

Profiles can add fields, require more detail and tighten constraints. They retain Core-required fields and Core meanings: **profiles extend, never weaken**. A worked migration-studies profile and the conformance rules are in [`profiles/README.md`](profiles/README.md).

With Python 3.11+ and `jsonschema` installed, validate the supplied examples:

```bash
python tools/validate.py examples/core-minimal.json
python tools/validate.py --collection tools/examples/collection-OHX.toml \
  examples/core-oral-history.json
```

Check agreement between specification, schema and fixtures:

```bash
python scripts/check_consistency.py
python tools/validate.py --self-test
```

Validator exit codes: `0` valid, possibly with warnings; `1` invalid; `2` input, configuration or execution could not be evaluated.

## Handoffs and the offline Dataverse tool

Four crosswalks document intended handoffs and their limits:

| Target | Role |
|---|---|
| [Dublin Core](crosswalks/dublin-core.md) | Descriptive discovery metadata |
| [Schema.org/Dataset](crosswalks/schema-org-dataset.md) | Web discovery layer |
| [REFI-QDA/QDPX](crosswalks/qdpx.md) | Linking descriptive records with analytical projects; documented boundaries |
| [Dataverse](crosswalks/dataverse.md) | Selected citation-block metadata |

Version 1.2.0 implements the Dataverse projection locally through [`tools/imm2dataverse.py`](tools/imm2dataverse.py). The other crosswalks are documentation; this package does not supply a general exporter for all four targets.

Check a supplied synthetic fixture without writing output:

```bash
python tools/imm2dataverse.py check \
  --collection tools/examples/collection-OHX.toml tests/tools/conv-build.json
```

`build` produces local citation JSON, a ZIP containing no interview files, and a private hash-bound build log. The tool has no network or repository-publishing path. It withholds records when consent/access selection, missing description, language mapping or names checks prevent a projection. A successful local build establishes neither approval for public release nor compatibility with a particular live instance. Commands, configuration and output rules are in [`docs/implementing.md`](docs/implementing.md).

## Adopting 1.2.0

The new `languages` field is optional. There are no new required fields, and `language` remains one string. Existing identifiers remain in place.

Consumers pinned to an older schema with `additionalProperties: false` will reject records that include `languages` until they are updated. Tighter chapter-time and blank-text checks can also expose previously accepted faulty records. Upgrade each consuming application separately, test its existing records and keep its operational version pinned until its own acceptance. The [changelog](CHANGELOG.md) records the compatibility details.

## Find your way around

- [`docs/README.md`](docs/README.md): conceptual documentation and model decisions.
- [`tap/core.csv`](tap/core.csv), [`schema/core.schema.json`](schema/core.schema.json): specification and schema.
- [`examples/`](examples/): minimal, generic and oral-history examples.
- [`vocabs/consent_status.md`](vocabs/consent_status.md): recommended consent vocabulary.
- [`methodological-positions/abstracts.md`](methodological-positions/abstracts.md): descriptive abstracts and interpretation.
- [`tools/`](tools/), [`tests/`](tests/), [`scripts/`](scripts/): offline tools, fixtures and consistency checks.

## Citation and credits

Cite this version:

Behnam Shad, Klaus (2026). *IMM-Core: Interview Metadata Model — Core Profile* (Version 1.2.0) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.23295846

The [concept DOI](https://doi.org/10.5281/zenodo.20507328) identifies the version family. Cite the version DOI when your work relies on a particular release.

Designed and built by **Klaus Behnam Shad**, Luxembourg Centre for Contemporary and Digital History (**C²DH**), University of Luxembourg. [ORCID](https://orcid.org/0000-0002-3601-9024) · [GitHub](https://github.com/klausbehnamshad/imm-core) · [Zenodo](https://doi.org/10.5281/zenodo.20507328)

He designed the model, built the specification, schema and tools, made all methodological decisions and is responsible for the content. AI tools assisted under his direction: Claude (Anthropic) with planning, design review and documentation; Codex (OpenAI) with implementation of code components; Muse with builds of approved work packages. He reviewed every AI-assisted contribution before adoption.

[CC BY 4.0](LICENSE). The bundled Dataverse language table retains its source attribution and [Apache-2.0 source licence](tools/data/LICENSE-dataverse.md).
