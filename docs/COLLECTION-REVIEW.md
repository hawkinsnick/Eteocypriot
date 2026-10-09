# Prepare a source-bound expert review

Open the [work ledger](../research/collection-work-ledger.json) and [review packet](../review/collection-packet.json). Choose the record keys relevant to the question. The ledger links each entry to its native evidence file and exact location, with revision hashes. It also indexes declared source leads and outstanding native tasks.

Ask your AI: “Prepare an expert review request for these record keys. State which sources you accessed, retain exact edition/page/line/figure locators and alternatives, and identify the unanswered questions. Give the evidence fingerprint and record hashes. Do not invent a reviewer or settle missing readings.”

The expert can record supported, disputed, inconclusive or not-applicable decisions separately for object identity, reading/layout, uncertainty, classification, independence and rights. Use the [decision template](../review/collection-decision-template.json); retain the evidence they inspected and their rationale. A structural check does not establish expertise, scientific correctness or admission. Existing native procedures continue to govern corrections and admission.

Counts retain their native units. Reading versions, catalogue labels, source entries, faces and photographs are not interchangeable object counts. The indexed sources describe declared snapshots, not necessarily everything surviving in the language. Restricted Linear A/B record derivatives remain local; use their native authenticated audit and reproduction instructions for detailed reviews.

For maintainers: run `python scripts/build_collection_handoff.py --write` after changing a declared input, then replay without `--write`. Declare new source and task files in `research/collection-readiness-inputs.json`. No source scan or transcription is duplicated by this handoff. Upstream licenses remain attached to the linked evidence; the project license does not override them.
