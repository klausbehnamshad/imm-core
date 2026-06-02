# Crosswalk: IMM-Core → Schema.org/Dataset

**IMM-Core version:** 1.0  
**Standard:** Schema.org `Dataset` type — https://schema.org/Dataset

---

## Purpose

A Schema.org/Dataset mapping enables web-level findability via Google Dataset Search and structured-data harvesters. An IMM-Core record can be exposed as a JSON-LD `Dataset` block embedded in a repository landing page. This mapping is an SEO/discoverability layer, not the authoritative record.

---

## Field mapping

| IMM-Core field | Schema.org property | Notes |
|---|---|---|
| `record_id` | `schema:identifier` | |
| `interview_date` | `schema:dateCreated` | |
| `interviewer` | `schema:creator` | Type `schema:Person`; add `schema:sameAs` with ORCID URI (e.g. `https://orcid.org/0000-0001-2345-6789`) if available |
| `title` | `schema:name` | |
| `abstract` | `schema:description` | |
| `language` | `schema:inLanguage` | ISO 639-3 three-letter codes are accepted by most harvesters; BCP 47 is formally required but 3-letter codes pass in practice |
| `spatial` | `schema:spatialCoverage` | Type `schema:Place` with `schema:name` set to the IMM `spatial` string value |
| `keywords` | `schema:keywords` | Comma-separated string or array; Schema.org accepts both |
| `accessRights` | `schema:conditionsOfAccess` | Schema.org has no closed vocabulary here; pass the IMM string directly |
| `consent_status` | — | No direct mapping. Document in a `schema:license` note or omit from Schema.org serialisation entirely. Do not attempt to map to `schema:license`. |
| `related_materials` | `schema:hasPart` or `schema:distribution` | Use `schema:distribution` if the URL points to a downloadable file; `schema:hasPart` for related datasets or documents |
| `timecoded_segments` | — | Not representable at Schema.org level; omit |
| `interviewee_display` | `schema:about` (as `schema:Person`) | Optional and sensitive. Use only if `interviewee_display` is a public pseudonym used in publications, not a private code name. When in doubt, omit. |

---

## Minimal JSON-LD example

```json
{
  "@context": "https://schema.org/",
  "@type": "Dataset",
  "identifier": "2024-05-18_LHI_0042",
  "name": "Interview with a former steelworker in Esch-Belval",
  "description": "The narrator reflects on migration experiences, working life in Luxembourg's steel industry, and the intergenerational transmission of memory.",
  "dateCreated": "2024-05-18",
  "creator": {
    "@type": "Person",
    "name": "Klaus Behnam Shad",
    "sameAs": "https://orcid.org/0000-0002-3601-9024"
  },
  "inLanguage": "deu",
  "spatialCoverage": {
    "@type": "Place",
    "name": "Esch-sur-Alzette"
  },
  "keywords": "labour history, migration, memory, steel industry",
  "conditionsOfAccess": "restricted",
  "distribution": {
    "@type": "DataDownload",
    "contentUrl": "https://gitlab.uni.lu/c2dh/lhi/luxoh-cmdi/-/raw/main/data/transcript-LHI-0042.docx",
    "encodingFormat": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  }
}
```

---

## Boundary

Schema.org/Dataset provides web-level SEO and basic harvester compatibility. It does not carry:

- GDPR-grade consent semantics (`consent_status` has no Schema.org equivalent)
- Structural interview data (`timecoded_segments`)
- Research-grade rights vocabulary

IMM-Core is not a Schema.org application profile. The JSON-LD block is an **exposure layer** for discoverability only. Where Schema.org and IMM-Core diverge, IMM-Core is authoritative.
