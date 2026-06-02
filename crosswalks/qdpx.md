# Crosswalk: IMM-Core ↔ REFI-QDA / QDPX

**IMM-Core version:** 1.0  
**Standard:** REFI-QDA Project Exchange Format (QDPX) — https://www.qdasoftware.org/

---

## Complementarity statement

IMM-Core and QDPX are **complementary, not competing**. They operate at different layers of the research stack:

- **IMM-Core** covers the *descriptive metadata layer*: the interview as a citable, rights-governed research object — its administrative context, consent, access rights, and structural segmentation.
- **QDPX** covers the *analytic data layer*: codes, memos, annotations, links between sources and analytic categories, and the coded structure of qualitative data.

A complete qualitative research data package may use both: IMM-Core records describe the interview objects; QDPX encodes the analysis applied to them. Neither system is a substitute for the other.

---

## Scope boundary table

| Domain | IMM-Core scope | QDPX scope | Overlap / notes |
|---|---|---|---|
| Interview identity (ID, date, title) | ✓ | ✗ | QDPX references source files but does not carry interview-level bibliographic or administrative metadata |
| Interviewer | ✓ | ✗ | |
| Consent and access rights | ✓ | ✗ | Rights are descriptive metadata, not analytic data |
| Language | ✓ (ISO 639-3 at source level) | ✓ (language codes on sources and code items) | Both may carry language codes; IMM-Core is authoritative for the source object |
| Keywords | ✓ (descriptive, pre-analytic subject terms) | ✓ (codes as analytic categories) | Conceptually different: IMM-Core keywords describe the interview; QDPX codes interpret it. Do not conflate. |
| Abstract | ✓ (descriptive, non-analytic) | ✗ | |
| Timecoded segments | ✓ (structural segmentation — descriptive) | ✓ (coded segments — analytically motivated) | IMM-Core segments are structural/descriptive (e.g. thematic blocks for navigation); QDPX segments are analytic (coded passages). They may overlap spatially but are not equivalent. |
| Transcript text | ✗ (deferred to Phase 2 in Core) | ✓ (source documents, transcripts) | |
| Codes and code trees | ✗ | ✓ | |
| Memos | ✗ | ✓ | |
| Annotations | ✗ | ✓ | |
| Source–code links | ✗ | ✓ | |
| Provenance of analytic categories | ✗ | ✓ | |
| File paths / media references | ✓ `related_materials` (URL / DOI) | ✓ (local file paths in `<Source>`) | Different reference conventions — see handoff note below |

---

## Recommended handoff convention

When a project uses both IMM-Core and QDPX:

1. The QDPX `<Source>` element's `name` attribute (or `guid`) should correspond to the IMM-Core `record_id` of the interview.
2. The IMM-Core `related_materials` array should contain the URL or DOI of the QDPX export file or the archive package containing it.
3. Neither system is master: IMM-Core is authoritative for rights and consent; QDPX is authoritative for analytic structure.
4. Projects depositing both in a repository should link the two records via `related_materials` (IMM side) and a `<Source>` reference (QDPX side).

---

## Boundary

QDPX does not solve the problem IMM-Core addresses: citable, rights-governed, discoverable interview records that are interoperable across repositories and disciplines. IMM-Core does not solve the problem QDPX addresses: portable, QDA-software-agnostic representation of qualitative analysis with full code-tree and annotation structure.

Projects adopting one do not need the other. Projects wanting both discoverability/governance and analytic portability benefit from both. The strategic claim in IMM-Core §4.4 is that these systems are designed to coexist at adjacent layers, not to compete for the same territory.
