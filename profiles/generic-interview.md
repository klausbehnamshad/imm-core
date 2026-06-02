# IMM-Profile-Migration

| | |
|---|---|
| **Slug** | `Migration` |
| **Full name** | Migration-Studies Interview Profile |
| **Discipline** | Migration studies, sociology |
| **Institution** | Reference example — not institution-specific |
| **IMM-Core target** | `^1.0` |
| **Profile version** | `1.0` |
| **Maintainer** | IMM-Core editorial board |

---

## Purpose

This profile is a **worked example**, not an active institutional implementation. Its purpose is to demonstrate that IMM-Core is discipline-agnostic by showing what a non-oral-history adoption looks like. Migration-studies sociology differs from archival oral history in three ways relevant to metadata:

1. **Consent structure.** Consent is typically project-specific or broad-research rather than archival; participants often have a right to withdraw consent without implications for archival deposit.
2. **Study-level aggregation.** Interviews in migration studies often belong to a defined study with its own identifier, ethics approval, and sampling frame. The individual interview record needs to link up.
3. **Recruitment method as methodological context.** Sampling strategy (purposive, snowball, random-quota) is methodologically significant for scope-of-inference and belongs in the record.

---

## DCTAP delta

Fields not listed here inherit Core semantics unchanged.

| propertyID | block | change | value / constraint |
|---|---|---|---|
| `consent_status` | A | enum imposed | `broad-research \| specific-project-only \| withdrawn` |
| `study_id` | A | added, optional | string — identifier linking the record to a parent study or ethics-approval unit |
| `recruitment_method` | A | added, optional | string — recommended vocabulary below |
| `record_id` | A | pattern recommended (not required) | `^[A-Z]{2}-[MF?]-[0-9]{4}-[0-9]{2}$` (country-gender-birthyear-sequence); enforcement is project-level |

---

## JSON Schema delta (fragment)

```json
{
  "properties": {
    "consent_status": {
      "enum": ["broad-research", "specific-project-only", "withdrawn"]
    },
    "study_id": {
      "type": "string",
      "description": "Block A. Identifier for the parent study or ethics-approval unit (optional)."
    },
    "recruitment_method": {
      "type": "string",
      "description": "Block A. Sampling/recruitment method (optional). See profile vocabulary."
    }
  }
}
```

---

## Controlled vocabularies

**`consent_status`** (Migration profile):

| Term | Meaning |
|---|---|
| `broad-research` | Consent covers use across multiple academic research projects |
| `specific-project-only` | Consent limited to the originating project; secondary use requires re-consent |
| `withdrawn` | Participant withdrew consent; record `accessRights` MUST be `closed` |

**`recruitment_method`** (recommended, non-exhaustive):

`snowball` | `purposive` | `random-quota` | `institutional-referral` | `online-panel` | `community-organisation` | `registry-based`

---

## Notes

**`study_id` is not in Core** because many interview-based research traditions (biographical-narrative, IPA, single-case studies) work at the individual-interview level with no parent study structure. The field is optional even within this profile; it becomes de facto required when institutional ethics approval operates at the study level.

**`recruitment_method` sits at the edge of Core's mandate.** In migration sociology, sampling strategy affects scope-of-inference and is methodologically significant enough to warrant a record-level field. In oral history, it typically does not. Its placement here as an optional profile field is the correct home; putting it in Core would import a social-science methodological assumption into a generic spec.

**`consent_status: withdrawn`** in this profile triggers a hard constraint: `accessRights` must be `closed`. Projects implementing this profile SHOULD enforce this in their validation pipeline.
