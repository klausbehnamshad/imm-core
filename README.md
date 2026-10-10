# IMM-Core: Interview Metadata Model — Core Profile

**Version:** 1.1.0 | **License:** [CC-BY-4.0](LICENSE) | **DOI:** 10.5281/zenodo.20507328 (all versions)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20507328.svg)](https://doi.org/10.5281/zenodo.20507328)

A generic, openly published minimal metadata model for interview-based qualitative research. Discipline-agnostic (oral history, sociology, anthropology, education, migration studies, health research). Designed for secondary analysis, archival deposit, and cross-repository discoverability.

## What this is

IMM-Core specifies the *descriptive metadata layer* — fifteen fields in three functional blocks (A Administrative, B Descriptive, C Structural) that describe an interview as a research object, prior to and independently of analysis. It uses a two-layer architecture: this Core Profile plus discipline-specific or institution-specific **Implementation Profiles** that extend it. A fourth block, D Preservation, is reserved for profiles.

## Who it's for

Researchers, archivists, repository managers, and data stewards working with interview-based qualitative data who need a lightweight, validatable metadata standard that crosswalks to Dublin Core, Schema.org, and REFI-QDA/QDPX.

## Repository structure

```
tap/core.csv                          # DCTAP profile — single source of truth
schema/core.schema.json               # JSON Schema mirror (derived from DCTAP)
examples/core-minimal.json            # Minimal valid Core record (required fields only)
examples/core-generic.json            # Complete Core record (migration studies)
examples/core-oral-history.json       # Valid Core record (oral history, invented collection)
vocabs/consent_status.md              # Recommended vocabulary for consent_status
profiles/README.md                    # Conformance rules; profile registration
profiles/generic-interview.md         # IMM-Profile-Migration (worked example)
crosswalks/dublin-core.md             # Field-by-field DC mapping
crosswalks/qdpx.md                    # REFI-QDA/QDPX complementarity and boundary table
crosswalks/schema-org-dataset.md      # Web-level findability mapping
crosswalks/dataverse.md               # Dataverse citation-block projection
methodological-positions/abstracts.md # Descriptive-vs-analytic abstract position paper
docs/README.md                        # Full conceptual documentation (§1–§11)
docs/implementing.md                  # Export rules, collection configuration, tool calls
tools/validate.py                     # Record checker: schema plus rules R1–R8
tools/imm2dataverse.py                # Offline converter to Dataverse JSON plus empty ZIP
tools/examples/collection-OHX.toml    # Synthetic example collection configuration
tools/data/dataverse-languages.tsv    # Pinned Dataverse language table (ISO 639-3 → English name)
scripts/check_consistency.py          # Checks TAP ↔ schema agreement and validates examples
tests/invalid/                        # Records that must fail schema validation
tests/invalid-rules/                  # Schema-valid records that fail rules R1–R8 only
tests/tools/                          # Unit tests and synthetic tool fixtures
```

## How to cite

Behnam Shad, Klaus (2026). *IMM-Core: Interview Metadata Model — Core Profile* (Version 1.1.0) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.23190815

## Quick start

Validate a record against the Core schema:

```bash
npx -p ajv-cli@5 -p ajv-formats@3 ajv validate -c ajv-formats \
  -s schema/core.schema.json -d examples/core-generic.json
```

`ajv-formats` is needed because the schema uses `"format": "date"`; without it, ajv-cli rejects the schema.

Check that `tap/core.csv` and the schema agree and that all examples validate (Python, `pip install jsonschema`):

```bash
python scripts/check_consistency.py
```

## Implementation Profiles

IMM-Profile-Migration (migration-studies sociology) is a worked reference example showing a non-oral-history adoption. Oral history collections at C²DH use the Core directly with collection-specific tool configuration. See `profiles/README.md` for the conformance rules and the list of registered profiles.

## Credits

Developed by Klaus Behnam Shad, who designed the method, made all methodological decisions and is responsible for the content.

AI tools assisted with parts of the work:

- **Claude (Anthropic):** planning, design review and documentation
- **Codex (OpenAI):** implementation of code components
- **Muse (Meta):** prototype build from the approved plan

The author reviewed every AI-assisted contribution before it was adopted.

## License

[Creative Commons Attribution 4.0 International (CC-BY-4.0)](LICENSE)
