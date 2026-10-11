# AI evidence and publication integrity

The individual AI skill and its bundle now require the native dependency projection and this guide. Native bundle validation checks that projection and its local identifier/source-URL evidence. `scripts/check_cross_corpus_dependencies.py --records repository::record-id ...` reports known dependencies; `--claim independent_witness_count`, `physical_object_count` or `phonetic_transfer` fails closed. Empty or unregistered dependencies never establish independence.

Known relationships are source-asserted catalogue references or shared digital entries, not project-certified physical identity. Keep native units, candidate status, source roles and uncertainty. The master registry is `Linear-A/corpus-factory/cross-corpus-dependencies.json`; more dependencies may be found, and the absence of a registered link is not proof of uniqueness.

Automatic bundle synchronization builds and validates the corpus-native format at a named source commit. `ai-skill/scripts/publish_sync.py` checks source binding, rejects unrelated changes, verifies the remote source parent and publishes by an atomic fast-forward push. A source change before the guard skips publication; a race after the guard rejects the push. Rebuild on current main rather than rebasing or forcing the validated bundle. Compiled research-starter text, where present, is included in the allowed generated outputs. Local Git race fixtures and hostile dependency tests execute in CI.

These controls improve source delivery and package integrity. They do not certify ancient readings, physical identities, witness independence, or the behavior of every AI platform. All underlying licensing, canonical claim gates and human acceptance requirements remain in force.
