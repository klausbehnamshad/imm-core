# Implementation Profiles

An **Implementation Profile** (IP) is a discipline-specific or institution-specific specialisation of IMM-Core. Profiles extend the Core; they do not weaken it.

---

## Conformance Rules

**Rule 1 — Extend, never weaken.**  
A profile may: add fields; tighten constraints (narrower enums, stricter patterns, additional required fields); specify controlled vocabularies; add block D preservation fields. A profile may NOT: remove Core-required fields; loosen the `accessRights` enum (`open|restricted|closed` is invariant); override Core field semantics.

**Rule 2 — DCTAP-as-SSoT.**  
Each profile is specified as a DCTAP delta over `tap/core.csv`. Only fields that differ from or are added to Core need to appear in the delta. Fields not listed in the delta inherit Core semantics unchanged.

**Rule 3 — Schema extension.**  
Each profile SHOULD provide a JSON Schema fragment (or full file) that extends `schema/core.schema.json` by: overriding `consent_status` with a discipline-specific `enum`; adding profile-specific properties to `properties`; tightening `record_id` pattern; keeping `additionalProperties: false` over the full extended field set.

**Rule 4 — Versioning.**  
Profiles are versioned independently from Core using SemVer. Each profile version MUST declare the IMM-Core version it targets (e.g. `imm-core: "^1.0"`). A Core major-version bump requires a profile update declaration; profile maintainers are responsible for verifying compatibility.

**Rule 5 — Profile identifier and registration.**  
Each profile is identified by a short slug and named `IMM-Profile-{Slug}`. Registration means: adding a row to the table below and a profile file in this directory.

---

## Registered Profiles

| Slug | File | Discipline / institution | Core target | Profile version |
|---|---|---|---|---|
| `LuxOH` | `luxoh-cmdi.md` | Oral history — C²DH, University of Luxembourg | IMM-Core ^1.0 | 1.0 |
| `Migration` | `generic-interview.md` | Migration-studies sociology (reference example) | IMM-Core ^1.0 | 1.0 |

To register a new profile: open a pull request adding a row above and a corresponding profile file in this directory.

---

## Profile File Format

Each profile file contains the following sections in order:

1. **Header block** — slug, full name, discipline, institution (if applicable), IMM-Core target, profile version, maintainer.
2. **DCTAP delta** — fields that differ from or are added to Core, in the same column format as `tap/core.csv` plus a `change` column.
3. **JSON Schema delta** — fragment for overrides and additions only.
4. **Controlled vocabularies** — any discipline-specific vocab not already in `vocabs/`.
5. **Crosswalk delta** (optional) — any profile-specific crosswalk additions beyond the Core crosswalks.
6. **Notes** — rationale for each constraint tightening; what Core already provides (no redundant restating of Core fields).
