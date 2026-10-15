# Attribution review

All four controls; Masson’s Eteocypriot coin-type attribution and IG’s syllabic-only title are not equivalent opposite language claims. Parts and specimens remain distinct.

Existing source consultation receipts and limits are inherited exactly from the referenced native packets. This pass inspects those packets, not the underlying publications afresh. No exhaustive literature search, new autopsy or independent review is claimed.

The complete selections below name the finite native collections reviewed. Other repository records and the broader literature are outside this checkpoint. Case counts are review tasks, not inscriptions, independent witnesses or fully attributed alternative pairs.

| Complete native selection | Rows |
|---|---:|
| `research/disagreement-register.json/items` | 4 |

Use the case query to read the finding together with the complete native evidence, including any named author/publication, source locator, inspection state, qualification and source dependence. Missing metadata stays missing; a source ID alone is not proof of direct consultation.

```sh
python scripts/attribution_review.py --check
python scripts/attribution_review.py --case 'ECY-DIS-001'
python scripts/evidence_query.py --list attribution-review
```

| Review ID | Type | Finding | Remaining work |
|---|---|---|---|
| ECY-DIS-001 | CLASSIFICATION | Whole-entry labels and question-mark language assertions are not adjudicated component readings. | Inspect component-specific source labels; Greek parallel text does not supply an Eteocypriot translation. |
| ECY-DIS-002 | CLASSIFICATION | Masson attributes the coin type to Eteocypriot; IG XV1,88 is titled syllabic. This is not a direct contradiction between explicit Eteocypriot and explicit Greek labels. | Retain Masson1957 pp.66–67 and exact IG XML; four reported specimens are not certified as the four modern parts. |
| ECY-DIS-003 | COVERAGE_GAP | A re-edition/autopsy lineage is named, but this control does not encode a complete historical/modern same-locus pair. | Inspect Perna and historical editions at exact pages/lines before reading comparison. |
| ECY-DIS-004 | COUNT_OR_IDENTITY | Digital entries are not certified physical objects. | Inventory/face joins and specimen identities remain source-specific. |

`research/attribution-review.json` pins every referenced native artifact by SHA-256 and records exact JSON pointers. `analysis/attribution-review-audit.json` is replayed by the checker. Queries reject changed input bytes before returning any case. The earlier native records remain unchanged.

Pair-attribution states describe documentary limitations, not scientific acceptance. A partial located comparison can be a real scholarly alternative without full typographic, physical-position or independent collation. `NOT_APPLICABLE` marks controls and interpretations for which a two-reading pair is not the appropriate unit. No unknown pair/witness total is replaced with zero.
