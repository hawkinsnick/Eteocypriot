# Combining the two Cypriot source views

The broader Cypriot index and the Eteocypriot candidate view share 25 parsed source-entry IDs. Adding their 592 and 25 digital-entry rows produces 617 view rows, not 617 additional or independent inscriptions.

The master supplies a [controlled source-entry union](https://github.com/hawkinsnick/Master-Corpus-AI-Skill/blob/main/references/academic-remediation.md) and an executable `scripts/prepare_source_union.py`. Its frozen manifest pins both input revisions, files, hashes and counts. It assembles 592 source-entry groups from 617 view rows and preserves all 617 view-specific pointers. It does not choose between conflicting or differently structured assertions, certify a sign unit, classify languages, or count physical objects.

From a master checkout with both native repositories available:

```sh
python scripts/prepare_source_union.py --checkouts /path/to/corpora --output /tmp/cypriot-union.json
```

Use the declared `digital_edition_entry` unit. Requests for sign/word/object/witness units and unregistered corpus pairings are rejected. The native corpus remains the authority for source assertions, attribution, component uncertainty and rights. Same-edition overlap is not independent corroboration. Null physical identities and unknown language assignments remain unknown. Passing assembly/replay checks grants no expert acceptance or population-frequency claim.
