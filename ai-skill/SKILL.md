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

## Evidence-count interpretation
Do not equate digital entries, editorial components, archaeological objects, or independent witnesses. For coverage comparisons, disclose the counted unit, edition/version, language-admission rules, bilingual segmentation and shared source dependencies. The README's evidence-count interpretation governs summaries; successful computational validation does not establish expert verification or completeness.

## Enforced assertion, dependency and bundle integrity

Read `docs/AI-INTEGRITY.md` and the required `research/cross-corpus-dependencies.json` before source counts or cross-corpus analysis. Use qualified assertion views when provided; original source literals must travel with their reconciliation, uncertainty and identity context. The dependency register does not certify physical identity or linguistic affinity. Shared catalogue references and duplicated digital sources are not independent witnesses. Missing links mean unknown, not independent. `scripts/check_cross_corpus_dependencies.py` screens declared record selections and rejects pooled physical/witness counts and phonetic transfer. Native AI bundle validation checks the dependency projection and local evidence hashes. Bundle publication validates the exact source parent and never rebases or force-pushes the validated artifact. Software and packaging checks do not establish expert or model-behavior acceptance.

## Corpus-native evidence and alternatives

Read `docs/EVIDENCE-AND-ALTERNATIVES.md`, `research/evidence-query-profile.json` and `analysis/evidence-query-coverage.json` for evidence or competing-reading questions. Use `scripts/evidence_query.py` with exact native IDs and an explicit collection when ambiguous. Preserve `native_record`, every uncertainty/editorial mark, source attribution, locator, inspection status and rights. Cite artifact path, JSON pointer and SHA-256; hashes certify bytes only. Treat explicitly linked records as declared ID associations, not physical certification or independent witnesses. Context resources have corpus-level scope and are not automatically about the queried record. Distinguish a named source reading from a legacy queue label, uninspected bibliographic lead, count convention or hypothesis. Do not infer a count of collated alternative pairs or independent witnesses from searchable rows; those metrics remain unknown. Report the native units and scope of each view separately, and defer to the corpus-specific limits. No new readings, expert acceptance or decipherment follows from this interface.
