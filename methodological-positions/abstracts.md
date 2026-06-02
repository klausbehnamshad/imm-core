# Methodological Position: The Descriptive Abstract

**Status:** Informative position paper. Not normative, but the `abstract` field's scope constraint in `tap/core.csv` and `schema/core.schema.json` is grounded in the argument here. Referenced from `docs/README.md` §7.

---

## The claim

The IMM-Core `abstract` field is **descriptive, not analytic**. It describes the interview as a research object — who speaks, in what context, about what subject-matter in broad terms — without embedding the cataloguer's interpretive categories.

This is a methodological position, not a style preference.

---

## Why the distinction matters

Qualitative research traditions differ on what analytical moves are legitimate, at what level of abstraction, and with whose vocabulary. A biographical-narrative interviewer and a constructivist grounded theorist may produce abstracts for the same interview that are incommensurable — not because one is wrong, but because they are answering different questions at different analytic levels.

If the `abstract` field carries analytic content, it becomes tradition-specific. A catalogue of 500 interviews whose abstracts are written using Schütze's narrative categories is not straightforwardly accessible to a researcher working in Mayring's framework, and vice versa. A purely descriptive abstract — subject-matter, setting, approximate duration, narrative type — is legible across traditions because it describes the interview as an object rather than as an analytic result.

The Core's `abstract` is the lowest common denominator: the minimal description that any interviewer in any tradition can supply, and that any researcher in any tradition can interpret.

---

## What belongs in a Core abstract

- Who the interviewee is (in anonymised or pseudonymised terms: role, generation, location — if relevant and not privacy-compromising)
- What the interview is broadly about (subject-matter, not interpretation)
- Where and when it took place (if not fully captured in `spatial` and `interview_date`)
- Approximately what form the narrative takes (single session, life history, thematic, focus group) — if relevant

**Target length:** 2–3 sentences.

---

## What does NOT belong in a Core abstract

- Analytic categories, codes, or themes
- Interpretation of the narrator's account
- Theoretical framing or positioning
- Comparisons to other interviews in the corpus
- Evaluative judgements about the quality or richness of the material

These belong in analytic metadata — memos, case summaries, coded segments — which are outside Core scope. See `crosswalks/qdpx.md` for where analytic content is properly housed.

---

## The constructivist-grounded-theory note

Charmaz's constructivist grounded theory insists on reflexivity about the researcher's role in knowledge construction. One implication: in CGT, even a "descriptive" summary is a theoretical act, since the choice of what counts as subject-matter rather than interpretation is itself interpretive. The Core acknowledges this without resolving it at the schema level. The descriptive-vs-analytic split in the `abstract` field is the Core's move in the direction of Charmaz's reflexive agenda — it requires the cataloguer to reflect on what is description vs. interpretation — without committing to the full CGT programme. That tension is left for the cataloguer to navigate, which is appropriate: schema design cannot substitute for methodological reflection.

---

## Per-tradition guidance

| Tradition | What to put in the Core abstract | What belongs elsewhere |
|---|---|---|
| Biographical narrative (Schütze) | Narrator's life-phase and context, broad thematic arc of the narrative, interview setting | Structural analysis: narrative segments, argumentation schemes, evaluated sections |
| Qualitative content analysis (Mayring) | Subject-matter covered, approximate scope and range of topics | Category system, deductive and inductive codes, frequency notes |
| Constructivist grounded theory (Charmaz) | Context, broad subject, narrative form; note any unusual interview dynamics if methodologically significant | Theoretical memos, initial codes, focused codes, theoretical categories |
| Documentary method (Bohnsack) | Setting, group composition if applicable, broad topic | Reflective interpretation, orientation frames, sinngenetische Typenbildung |
| IPA | Participant profile (anonymised), subject of inquiry, interview format | Experiential themes, interpretive commentary, idiographic analysis |
| Discourse analysis | Text/speech type, topic, interactional context (dyadic, institutional, etc.) | Discourse structures, rhetorical analysis, positioning theory moves |

Each row ends implicitly with: the tradition needs more than Core provides at the analytic level, and that is by design. Core does not try to be a full research data record; it tries to be the minimal substrate on which any tradition's fuller records can be built.
