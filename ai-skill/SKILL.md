---
name: eteocypriot-research
description: Evidence-first AI research skill for the Eteocypriot corpus.
version: 0.3.1
---

# Eteocypriot Research Skill

This skill is an interface to the corpus in this repository. The corpus remains the canonical source of truth. Never maintain an independent scholarly dataset inside the skill.

## Governing rules
1. Separate physical/epigraphic observation, source transcription, normalization, computational derivation, scholarly interpretation, and AI-derived analysis.
2. Prefer canonical machine-readable corpus records over prose summaries for record-level questions.
3. Preserve identifiers, provenance, uncertainty, disagreements, corrections, negative results, and superseded analyses.
4. Never invent missing signs, readings, restorations, provenience, bibliography, source independence, or rights.
5. Label calculations performed by the AI and state enough method for reproduction.
6. Respect record/source-specific licensing and attribution. Repository-level licensing must not erase upstream restrictions.
7. For cross-corpus claims, establish comparability and source independence before interpreting similarity.
8. Report blocked or missing evidence rather than filling gaps.

## Corpus-specific caution
Poorly understood language written largely in Cypriot script: script decipherment does not equal language decipherment; keep readings separate from lexical or grammatical interpretation.

## Default research response
Give the direct answer, followed as relevant by Evidence; Evidentiary status; Uncertainty/limitations; Reproducibility; Rights/attribution.

## Synchronization
Read `ai-skill/generated/source-state.json` before substantive work. It records the corpus commit from which the AI-facing package was synchronized. Generated files are rebuildable views; canonical corpus files govern if a discrepancy is found.

## Academic-scrutiny gates
- A deciphered script does not make the Eteocypriot language deciphered
- Greek parallel components are not Eteocypriot evidence
- Copies shared with the Cypriot Greek project are the same source witness, not independent replication
- Whole-corpus frequency, translation and cross-script phonetic inference remain blocked
- Uncertain and damaged components remain excluded under the canonical policy


## Offline corpus browser
Run `python scripts/build_corpus_browser.py` to generate `workbench/corpus-browser.html`. It searches only files explicitly admitted by `research/browser-sources.json`. Browser admission requires rights/provenance review; never recursively ingest restricted or raw upstream material. Display does not establish decipherment, source independence, or expert validation.


## Linear A method-parity gate
Eteocypriot now has explicit source lineage, language/object disagreement controls, component rights, browser/API/export/validation and review boundaries around its licensed IG XV 1 layer. Digital entries are not certified physical objects; historical and modern language classifications remain source-specific. See `docs/RIGHTS-ONLY-READINESS.md` and `research/residual-blocker-ledger.json`.

## Validation and AI-use guide
Consult `docs/VALIDATION-AND-AI-USE.md` before asserting reproducibility, corpus completeness, expert acceptance or cross-corpus comparability. Record the source commit and actual validation outputs. Keep scientific review gates separate from passing software checks.
