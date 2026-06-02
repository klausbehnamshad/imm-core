# IMM-Core: Interview Metadata Model — Core Profile

**Version:** 1.0 | **License:** [CC-BY-4.0](LICENSE) | **DOI:** 10.5281/zenodo.20507329

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20507329.svg)](https://doi.org/10.5281/zenodo.20507329)

A generic, openly published minimal metadata model for interview-based qualitative research. Discipline-agnostic (oral history, sociology, anthropology, education, migration studies, health research). Designed for secondary analysis, archival deposit, and cross-repository discoverability.

## What this is

IMM-Core specifies the *descriptive metadata layer* — thirteen fields in four blocks that describe an interview as a research object, prior to and independently of analysis. It uses a two-layer architecture: this Core Profile plus discipline-specific or institution-specific **Implementation Profiles** that extend it.

## Who it's for

Researchers, archivists, repository managers, and data stewards working with interview-based qualitative data who need a lightweight, validatable metadata standard that crosswalks to Dublin Core, Schema.org, and REFI-QDA/QDPX.

## Repository structure

```
tap/core.csv                          # DCTAP profile — single source of truth
schema/core.schema.json               # JSON Schema mirror (derived from DCTAP)
examples/core-generic.json            # Minimal valid Core record (migration studies)
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
```

## How to cite

Behnam Shad, Klaus (2026). *IMM-Core: Interview Metadata Model — Core Profile* (v1.0). Zenodo. https://doi.org/10.5281/zenodo.20507329

## Quick start

Validate a record against the Core schema:

```bash
npx ajv-cli validate -s schema/core.schema.json -d examples/core-generic.json
```

## Implementation Profiles

LuxOH-CMDI (oral history, C²DH Luxembourg) is the first registered profile. See `profiles/luxoh-cmdi.md` and the canonical institutional implementation at [GitLab — LuxOH-CMDI](https://gitlab.uni.lu/c2dh/lhi/luxoh-cmdi).

## License

[Creative Commons Attribution 4.0 International (CC-BY-4.0)](LICENSE)
