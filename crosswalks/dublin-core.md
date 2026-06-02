# Crosswalk: IMM-Core → Dublin Core Terms

**IMM-Core version:** 1.0  
**Standard:** Dublin Core Metadata Terms (DCTERMS) — https://www.dublincore.org/specifications/dublin-core/dcmi-terms/

---

## Field mapping

| IMM-Core field | DCTERMS property | Mapping quality | Notes |
|---|---|---|---|
| `record_id` | `dcterms:identifier` | Clean | |
| `interview_date` | `dcterms:date` | Clean | Use `dcterms:created` if the recording date is the creation date; `dcterms:date` is more general |
| `interviewer` | `dcterms:contributor` | Acceptable | `dcterms:creator` is sometimes used, but the interviewer is usually a contributor rather than the intellectual author of the work |
| `consent_status` | — | No clean mapping | DC has no consent property. Document alongside `accessRights` as a plain-text note in a `dcterms:rights` statement |
| `accessRights` | `dcterms:accessRights` | Clean | |
| `title` | `dcterms:title` | Clean | |
| `interviewee_display` | `dcterms:subject` or `dcterms:contributor` | Lossy | Neither is satisfactory. `subject` works if the interviewee is the subject of the interview; `contributor` works if framing them as participant. Both are lossy. |
| `language` | `dcterms:language` | Clean | ISO 639-3 three-letter codes are accepted by most DC implementations (RFC 5646 formally requires BCP 47, which overlaps) |
| `spatial` | `dcterms:spatial` (refinement of `dcterms:coverage`) | Clean | Use `dcterms:spatial` specifically rather than the broader `coverage` |
| `keywords` | `dcterms:subject` | Clean | Multiple `subject` elements; note that `interviewee_display` may also map here, creating a collision if not disambiguated |
| `abstract` | `dcterms:description` | Clean | `dcterms:abstract` (a refinement) is more precise if the DC profile supports it |
| `timecoded_segments` | — | No mapping | Segment structure has no DC equivalent. Retain in native format; do not flatten. |
| `related_materials` | `dcterms:relation` or `dcterms:hasPart` | Acceptable | Use `dcterms:hasPart` if the related material is a derivative (transcript, excerpt); `dcterms:relation` for lateral associations |

---

## Boundary

Dublin Core provides a useful semantic baseline for catalogue export and OAI-PMH harvest endpoints. IMM-Core is not a DC application profile. DC cannot carry:

- GDPR-grade consent semantics (`consent_status` has no DC equivalent without information loss)
- Interview-specific rights fields beyond basic access categories
- Structural data (`timecoded_segments`)

The DC mapping is an **exposure layer** for interoperability with library catalogues and generic repositories. It is not the authoritative IMM-Core representation. Where DC and IMM-Core diverge, IMM-Core is authoritative.
