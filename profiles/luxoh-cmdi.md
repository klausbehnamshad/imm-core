# IMM-Profile-LuxOH

| | |
|---|---|
| **Slug** | `LuxOH` |
| **Full name** | Luxembourg Oral History — CMDI Profile |
| **Discipline** | Oral history |
| **Institution** | C²DH, University of Luxembourg |
| **IMM-Core target** | `^1.0` |
| **Profile version** | `1.0` |
| **Maintainer** | Luxembourg Centre for Contemporary and Digital History (C²DH) |
| **Canonical implementation** | [LuxOH-CMDI on GitLab](https://gitlab.uni.lu/c2dh/lhi/luxoh-cmdi) |

---

## DCTAP delta

Fields not listed here inherit Core semantics unchanged.

| propertyID | block | change | value / constraint |
|---|---|---|---|
| `record_id` | A | pattern tightened | `^[0-9]{4}-[0-9]{2}-[0-9]{2}_LHI_[0-9]{4}$` |
| `consent_status` | A | enum imposed | `research-only \| teaching \| public \| embargoed` |
| `spatial` | B | vocabulary imposed | Luxembourg place-name list (managed in canonical GitLab implementation; see `[canonical repo]/vocabs/spatial-lu.md`) |
| `file_format` | D | added, optional | string — master file format, e.g. `WAV 24/48` or `MP4 H.264` |
| `master` | D | added, optional | boolean — `true` if this record refers to the master copy |
| `access_copy` | D | added, optional | string — filename or path of the access copy |
| `checksum` | D | added, optional | string — checksum of master file, e.g. `sha256:…` |

---

## JSON Schema delta (fragment)

Apply these overrides to `schema/core.schema.json` properties when validating LuxOH records:

```json
{
  "properties": {
    "record_id": {
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}_LHI_[0-9]{4}$"
    },
    "consent_status": {
      "enum": ["research-only", "teaching", "public", "embargoed"]
    },
    "file_format": {
      "type": "string",
      "description": "Block D. Master file format, e.g. 'WAV 24/48' or 'MP4 H.264'."
    },
    "master": {
      "type": "boolean",
      "description": "Block D. True if this record refers to the master copy."
    },
    "access_copy": {
      "type": "string",
      "description": "Block D. Filename or path of the access copy."
    },
    "checksum": {
      "type": "string",
      "description": "Block D. Checksum of the master file, e.g. 'sha256:…'."
    }
  }
}
```

---

## Controlled vocabularies

**`consent_status`** (LuxOH enum):

| Term | Meaning |
|---|---|
| `research-only` | Use in academic research only; no teaching or public dissemination |
| `teaching` | Academic research and anonymised teaching contexts |
| `public` | No dissemination restrictions |
| `embargoed` | Time-limited embargo; specific terms in institutional deposit agreement |

**`spatial`** (Luxembourg places): managed in the canonical GitLab implementation. The list covers Luxembourg municipalities and cross-border regions relevant to LHI collections.

---

## What Core already provides

This profile does not restate Core fields. All seven Core-required fields (`record_id`, `interview_date`, `interviewer`, `consent_status`, `accessRights`, `title`, `language`) remain required and semantically unchanged. The profile adds Block D preservation fields and tightens `record_id` pattern and `consent_status` enum only.

---

## Relationship to LuxOH-CMDI v1.1

LuxOH-CMDI v1.1 (hosted on GitLab) is the canonical **institutional implementation** of this profile. The GitLab repository contains: CI/CD validation pipelines, training materials and instructor checklists, CatDV/Dataverse integration scripts, and Luxembourg-specific data-management procedures. This profile file documents the *metadata specification*; the GitLab repository documents the *operational workflow*. When this profile and the GitLab repo diverge, the GitLab repo is authoritative for operational questions; this profile is authoritative for field semantics.

The key generalisation from LuxOH v1.1 to IMM-Core is that Block D fields and the `record_id` LHI pattern, which were baked into the v1.1 schema, are now profile-level constraints. A Core record is valid without them; a LuxOH record must conform to both Core and this delta.
