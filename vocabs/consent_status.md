# Recommended Vocabulary: `consent_status`

**Status:** Informative (not normative at Core level).  
**Field:** `consent_status` — Block A, mandatory, free string in IMM-Core.  
**Version:** IMM-Core 1.0

---

## Background

IMM-Core does not enforce a `consent_status` enum because consent regimes differ across disciplines. Archival oral history, health research, migration sociology, and educational research each have distinct frameworks for what categories are relevant and how they are named. Importing one discipline's vocabulary under the banner of a "generic" core would falsely universalise it.

This file provides a cross-domain reference vocabulary. Implementation Profiles SHOULD specify a subset, an extension, or an alternative vocabulary appropriate to their disciplinary and legal context. A profile that does not specify an enum SHOULD reference this file.

---

## Cross-Domain Reference Vocabulary

| Term | Definition | Typical context |
|---|---|---|
| `research-only` | Interview may be used for academic research but not for teaching or public dissemination | Oral history, archival research |
| `teaching` | Interview may be used for academic research and anonymised teaching contexts | Oral history, education research |
| `public` | Interview may be used without restrictions on dissemination | Oral history (fully consented public deposit) |
| `embargoed` | Interview is under a time-limited embargo; access and use governed by embargo terms | Oral history, political history, sensitive biography |
| `broad-research` | Consent covers use across multiple research projects; not limited to the originating project | Health research, migration studies, social science panel data |
| `specific-project-only` | Consent is limited to the project in which the interview was originally conducted | Health research, clinical studies, single-project qualitative research |
| `withdrawn` | Participant has withdrawn consent; record retained for administrative purposes only — no substantive content accessible | Any discipline |

---

## Adoption by registered profiles

| Profile | Terms in use |
|---|---|
| IMM-Profile-LuxOH | `research-only` \| `teaching` \| `public` \| `embargoed` \| `withdrawn` |
| IMM-Profile-Migration | `broad-research` \| `specific-project-only` \| `withdrawn` |

---

## Invariant rule

`withdrawn` MUST always be available as a valid value, even in profiles that specify a restricted enum. A withdrawn record MUST set `accessRights: "closed"`. Since IMM-Core 1.0.1 the Core schema enforces this rule.

Values are case-sensitive, lowercase, exact strings. The Core rule fires only on the exact value `withdrawn`; `Withdrawn`, `withdrawn ` (trailing space) or a translated term do not trigger it and the Core cannot detect them. Implementation Profiles and ingest software MUST restrict `consent_status` input to the profile vocabulary plus `withdrawn`; unknown values are a clarification case, not a record.

A withdrawn record SHOULD retain only the seven required fields (`record_id`, `interview_date`, `interviewer`, `consent_status`, `accessRights`, `title`, `language`) and `governance_ref`; `title` SHOULD be reduced to an administrative label. Descriptive fields (`interviewee_display`, `spatial`, `keywords`, `abstract`, `timecoded_segments`, `related_materials`) SHOULD be removed. Deleting derived files and propagating the withdrawal to copies and exports are operational duties outside the metadata record; the Core does not enforce them.

---

## Note on GDPR alignment

None of these terms maps 1:1 to a GDPR legal basis category. They describe what a participant consented to at the point of data collection, which is a layer above GDPR legal basis (typically Art. 6(1)(a) consent or Art. 9(2)(a) for sensitive data). Profiles targeting health research contexts should consider aligning with their national research ethics framework in addition to this vocabulary.
