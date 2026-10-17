# Research delivery and independent-review workflow

The native profile `research/evidence-query-profile.json` defines the selected
public evidence views. It is not a census of all inscriptions or all available
research. Each view preserves its native unit, category, scope, source pointers,
uncertainty and rights context. A file hash and JSON pointer locate a project
record; they do not supply missing primary-edition attribution. Read native
`scholarly_limits` and `review/collection-packet.json` before interpretation.

## Read and reproduce

Use Python 3.12 with the standard library:

```sh
python scripts/research_delivery.py --check
python scripts/test_research_delivery.py
python scripts/research_delivery.py --search '?' --limit 5
python scripts/evidence_query.py --coverage
```

Choose a collection and exact ID from coverage/inventory, then use
`--dossier ID --collection COLLECTION` to obtain an evidence-only answer with
exact artifact hashes and pointers. Only the supplied native record is asserted;
no translation, restoration, source independence or accepted reading is generated.
The evidence-response validator rejects altered records, citations or added claims.
This is a deterministic interface test, **not an empirical evaluation of an LLM**.
When an assistant adds its own analysis, label it separately, cite its evidence,
retain alternatives and explain uncertainty. Do not assert missing metadata.

Build a local research package:

```sh
python scripts/research_delivery.py --package /tmp/native-research.zip
```

It contains only explicitly registered/linked public files, instructions, source
and license context, native review routing, and replay code. No crawl of raw,
private or sealed directories occurs. Packaging grants **no redistribution rights**.
Do not publish or upload payloads merely because a local package was built.
Keep the originating GitHub commit and external ZIP SHA-256. Extract it, run
`--check`, and rebuild with the same command to obtain byte-identical output.
The internal manifest covers all members except itself; the external ZIP checksum
binds the complete package. Hashes require a trusted repository revision for
source authentication. Native terms continue to govern each component.

## Submit a bounded correction or review

Generate a draft using `--review-template ID --collection COLLECTION` and save
the JSON outside the repository. It pins one native target, profile and source
bytes. Ask a qualified reviewer a bounded question using the full native dossier
and its linked context. No outreach is sent by this workflow.

The reviewer supplies identity reference, affiliation, relevant expertise, date,
conflicts and source dependence; evidence actually consulted with citation,
page/line/figure locator, accessed version, access/rights and dependence;
reasoning, confidence, counterevidence and unresolved objections. Use SUPPORT,
REJECT, INCONCLUSIVE or MORE_SOURCE_REQUIRED. Set status to
SUBMITTED_FOR_MAINTAINER_CHECK. Preserve false acceptance/change flags.

Validate with `--validate-review /path/submission.json`. This checks structure
and exact source binding only. It neither authenticates identity nor verifies
expertise, access, independence or epigraphic truth. A human maintainer must
verify those matters and apply the corpus's native acceptance rules. Preserve
the response and dissent; do not automatically rewrite native readings. If the
source bytes/profile change, regenerate the request and explicitly reconcile
old feedback rather than silently applying it to new evidence.

## What completion means

`analysis/research-delivery.json` reports delivery-control coverage for the
selected views. It deliberately leaves scholarly completeness, expert acceptance
and model-behavior validation unclaimed. Missing editions/permissions, incomplete
source-to-record attribution, disputed readings and object identity, source
independence and outstanding calibration require their recorded native work.
An engineering pass must never be reported as all scholarly P0/P1 issues closed.
