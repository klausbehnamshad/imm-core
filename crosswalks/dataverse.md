# Crosswalk: IMM-Core → Dataverse (citation block)

**IMM-Core version:** 1.2.0 (unreleased)  
**Standard:** Dataverse citation metadata block — `scripts/api/data/metadatablocks/citation.tsv` in IQSS/dataverse, commit `cc6e62e3354492ad1f4127adc64eb22445319b95` (SHA-256 `21495ad4f4f917b1713d58fa5b81ca037df58cbf0d1d150cce856aa80d1ef82a`). The concrete instance can differ; check its version, licences, active blocks and granularity before any real deposit (a separate task, not this release).

---

## Scope

This crosswalk defines the projection that `tools/imm2dataverse.py` builds locally: one IMM-Core record becomes one `datasetVersion` object with the citation block. The tool only checks and writes files. A local file is neither a release permission nor a created Dataverse draft, and BUILD guarantees no acceptance by a real instance.

## Field projection

| Source | Dataverse field and shape |
|---|---|
| `title` | primitive `title`, `multiple:false` |
| `abstract` | compound `dsDescription`, `multiple:true`; child `dsDescriptionValue`, primitive, `multiple:false` |
| `keywords` | compound `keyword`, `multiple:true`; per child `keywordValue`, primitive, `multiple:false`; omitted entirely when the array is empty |
| `interview_date` | compound `dateOfCollection`, `multiple:true`; start and end each equal the date, primitives, `multiple:false` |
| `interviewer`, only when switched on | compound `contributor`, `multiple:true`; per person `contributorName` primitive and `contributorType` controlledVocabulary, children `multiple:false`; exact value `Data Collector`; split only on `; `; only a real ORCID bracket (`0000-0001-2345-6789` form) is removed, ordinary brackets such as `(1939)` are kept, and that loss of extra information is documented here |
| `language` plus optional `languages` | controlledVocabulary `language`, `multiple:true`; main language first, further codes in input order without duplication; exact English names from the pinned table `tools/data/dataverse-languages.tsv` |
| `spatial`, when present | primitive `productionPlace`, `multiple:true`; list with exactly one value |
| `record_id`, only when switched on | compound `otherId`, `multiple:true`; children `otherIdAgency` and `otherIdValue`, primitives, `multiple:false` |
| `related_materials` | primitive `relatedMaterial`, `multiple:true`; only normalised DOI references and HTTPS URLs on exactly parsed `allowed_hosts` with a valid numeric port; entries with query or fragment parts (including empty ones), invalid ports or user information are skipped and counted, never truncated; no user information in admitted entries |
| Configuration | one outer `author` compound holding every configured author as a `value` entry, plus `datasetContact` as a repeatable compound; `subject` as repeatable controlledVocabulary; `kindOfData` as repeatable primitive |
| Licence mode | directly under `datasetVersion`: `license` as object with `name`/`uri`, or `termsOfUse` as non-empty string; outside `metadataBlocks` |

## Never to Dataverse

Never passed through generically and always excluded: `governance_ref`, `consent_status`, `interviewee_display`, `timecoded_segments`, `accessRights` as a field, internal consent references, the approval block and the names list.

## Withholding and minimisation

Valid records are still withheld (SKIP with a fixed reason) for: `withdrawn`; `accessRights = closed`; `embargoed`; consent outside the approved selection; access outside `export_access`; missing or blank abstract; a names-list hit in the projected public free texts; a language code without table mapping.

The names check runs on the planned projection (title, abstract, keywords, place, admitted URLs and, when switched on, the interviewer). It is case-insensitive, honours whole words and never prints hit values. It supports the check for releasable content; further persons, quasi-identifiers and linkage risks need the institutional output review. No blanket ban on titles with date or place, no automatic shortening.

## Language mapping

The record carries ISO 639-3; the instance vocabulary carries English names with ISO 639-3 identifiers. The pinned table `tools/data/dataverse-languages.tsv` holds 7,915 rows with a three-letter code, derived from 7,916 controlled language values of the source including one code-free `Not applicable` row, which is not part of the mapping. Spot checks: `deu → German`, `ltz → Luxembourgish, Letzeburgesch`, `fra → French`, `eng → English`, `por → Portuguese`, `ita → Italian`, `nld → Dutch`. A live vocabulary override is specified in the instance task. Offline, no checked instance compatibility is claimed.

## Governance rules (sources)

- Licence is always explicit: exactly one non-empty mode (`license_name` plus `license_uri`, or `custom_terms_of_use`). Both at once, incomplete pairs and whitespace-only are errors. A default licence of the instance is never relied upon (Dataverse ships CC0 1.0 as the default; pinned installation guide and parser).
- Only what the approved collection configuration allows in `export_consent` is projected; never a draft for `withdrawn`, `closed` or `embargoed`. Missing `abstract` means no projection.
- `export_consent` is a subset of `consent_values` and holds neither `withdrawn` nor `embargoed`. `export_access` holds only `open` and/or `restricted`, never `closed`. An empty selection withholds everything.
- Published metadata stays public; a tombstone page with citation data remains after deaccession (Dataverse guide, DataCite). Titles, authors, descriptions and keywords of every migrated record must be allowed to stay public by collection decision.
- Public identifier and interviewer are configurable and off by default; the approved configuration documents role, date and decision reference. The names check helps; it replaces no output review on persons and linkage risks. A synthetic configuration must never trigger a real write.

---

## Boundary

Dataverse carries no consent property, no withdrawn semantics and no structural chapter marks. The JSON built here is an **exposure candidate** for repository deposit only. Where Dataverse and IMM-Core diverge, IMM-Core is authoritative for the record; the collection decision is authoritative for what may leave the collection.
