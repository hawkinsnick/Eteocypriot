# Evidence and alternative-reading queries

This corpus exposes its existing native evidence through a checksum-pinned profile. The query layer preserves complete selected records and their source locators, uncertainties, editorial assertions and rights fields. It adds no new source acquisition, canonical reading, restoration, adjudication, source independence or expert acceptance.

## Use

Run from the repository root:

```sh
python scripts/evidence_query.py --coverage
python scripts/evidence_query.py --list 'digital-entries'
python scripts/evidence_query.py --record 'ETEC-IGXV1-1' --collection 'digital-entries'
python scripts/evidence_query.py --check
python scripts/test_native_evidence_query.py
```

Use exact native IDs. If an ID occurs in more than one view, specify `--collection`. Absence from these selected views does not establish absence from the full corpus, scholarship or historical record.

## Declared native views

| View | Records | Native unit | Scope |
|---|---:|---|---|
| digital-entries | 25 | digital edition entry | Entry membership, source language classification and component partitions remain literal. |
| disagreement-register | 4 | research disagreement/control item | Broad scopes are not automatically assigned to individual records. |

Counts overlap and must not be added as unique inscriptions, objects or independent witnesses. The coverage report deliberately leaves alternative-pair and independent-witness counts unknown; a comparison register can include reported, dependent or unaligned assertions.

## Trace a claim

Each dossier returns `native_record` unchanged, the repository path, exact JSON pointer and file SHA-256. It also returns any records linked by specifically declared equal native keys. Such links are editorial associations, not certified physical equivalence or source independence. Read source authorship, locators, inspection state, uncertainty and rights in the native record and its context.

The profile lists additional source, rights and disagreement registers. These are corpus-level context pointers: inclusion does not mean every register asserts facts about the queried record. Retrieve an exact existing claim with:

```sh
python scripts/evidence_query.py --artifact 'data/records.json' --pointer ''
```

Pointers use RFC 6901 escaping (`~1` for slash, `~0` for tilde). JSONL artifacts are viewed as arrays of nonempty source lines; CSV fields remain source strings. Context envelopes omit array-valued siblings; use `--artifact` to retrieve those siblings and their full qualifications. Nothing is fetched from the network or from private gold/calibration files.

## Corpus-specific limits

- Shared IG material is not independent across the two projects. Greek, Eteocypriot and uncertain components must not be conflated. Source editorial marks, translation responsibility and source URLs remain unaltered.

## Further scholarly work

For each proposed alternative, identify the author or edition, precise page/plate/position, literal reading, consultation state, source lineage and reuse terms. Distinguish observed damage, supplied text, segmentation, transliteration conventions, source-reported analysis and project hypotheses. Align the same locus before comparing readings. Keep unresolved attribution and alignment explicit. Existing register entries must not be promoted to completed collation merely because they are searchable.

The profile and report are `research/evidence-query-profile.json` and `analysis/evidence-query-coverage.json`. Source pins fail closed: changes to a registered source require inspecting the change, updating its profile pin, regenerating coverage and rerunning tests. Hashes establish byte identity, not historical truth. Source-specific rights prevail over project licenses; this interface grants no new extraction or redistribution permission.

## Bounded attribution review (2026-10-15)

Read `docs/ATTRIBUTION-REVIEW.md` and `research/attribution-review.json` before describing a dispute or source comparison. Run `python scripts/attribution_review.py --case ID` with the referenced evidence available. Preserve complete native evidence and distinguish reading, interpretation, classification, count, identity and representation questions. This checkpoint reviews pinned repository packets; it does not repeat their primary consultation or grant independent review. Inherit the exact author/publication, locator, consultation limits and dependence from each pointer; missing fields remain unknown. Use the case-specific remaining work. Do not count register entries or apparatus notes as fully attributed pairs, physical objects or independent witnesses.

All four controls; Masson’s Eteocypriot coin-type attribution and IG’s syllabic-only title are not equivalent opposite language claims. Parts and specimens remain distinct.
