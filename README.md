# IMM-Core: Interview Metadata Model — Core Profile

**Version:** 1.1 | **License:** [CC-BY-4.0](LICENSE) | **DOI:** 10.5281/zenodo.20507329

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20507329.svg)](https://doi.org/10.5281/zenodo.20507329)

A generic, openly published minimal metadata model for interview-based qualitative research. Discipline-agnostic (oral history, sociology, anthropology, education, migration studies, health research). Designed for secondary analysis, archival deposit, and cross-repository discoverability.

## What this is

IMM-Core specifies the *descriptive metadata layer* — thirteen fields in three functional blocks (A Administrative, B Descriptive, C Structural) that describe an interview as a research object, prior to and independently of analysis. It uses a two-layer architecture: this Core Profile plus discipline-specific or institution-specific **Implementation Profiles** that extend it. A fourth block, D Preservation, is reserved for profiles.

## Who it's for

Researchers, archivists, repository managers, and data stewards working with interview-based qualitative data who need a lightweight, validatable metadata standard that crosswalks to Dublin Core, Schema.org, and REFI-QDA/QDPX.

## Repository structure

```
tap/core.csv                          # DCTAP profile — single source of truth
schema/core.schema.json               # JSON Schema mirror (derived from DCTAP)
examples/core-minimal.json            # Minimal valid Core record (required fields only)
examples/core-generic.json            # Complete Core record (migration studies)
examples/core-luxoh.json              # Valid Core record (LuxOH oral history profile)
vocabs/consent_status.md              # Recommended vocabulary for consent_status
profiles/README.md                    # Conformance rules; profile registration
profiles/luxoh-cmdi.md                # IMM-Profile-LuxOH (C²DH, University of Luxembourg)
profiles/generic-interview.md         # IMM-Profile-Migration (worked example)
crosswalks/dublin-core.md             # Field-by-field DC mapping
crosswalks/qdpx.md                    # REFI-QDA/QDPX complementarity and boundary table
crosswalks/schema-org-dataset.md      # Web-level findability mapping
methodological-positions/abstracts.md # Descriptive-vs-analytic abstract position paper
docs/README.md                        # Full conceptual documentation (§1–§11)
scripts/check_consistency.py          # Checks TAP ↔ schema agreement and validates examples
tests/invalid/                        # Records that must fail validation
```

## How to cite

Behnam Shad, Klaus (2026). *IMM-Core: Interview Metadata Model — Core Profile* (v1.0). Zenodo. https://doi.org/10.5281/zenodo.20507329

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

IMM-Profile-LuxOH (oral history, C²DH Luxembourg) is the first registered profile; IMM-Profile-Migration is a worked reference example. See `profiles/README.md` for the conformance rules and the list of registered profiles.

## Credits

Developed by Klaus Behnam Shad, who designed the method, made all methodological decisions and is responsible for the content.

AI tools assisted with parts of the work:

- **Claude (Anthropic):** planning, design review and documentation
- **Codex (OpenAI):** implementation of code components
- **Muse (Meta):** prototype build from the approved plan

The author reviewed every AI-assisted contribution before it was adopted.

## License

[Creative Commons Attribution 4.0 International (CC-BY-4.0)](LICENSE)
