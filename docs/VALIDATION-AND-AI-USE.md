# Validation and AI research use

This guide states reproducible checks and scientific boundaries. It is not an independent scholarly review or a new corpus reading.

## Local verification

From the repository root, run:

```sh
python -m etec validate
python -m unittest discover -s tests -v
python scripts/release_check.py
python scripts/audit_source_concordance.py --check
```

Record the exact repository commit, Python version, command output, and any failure. Do not infer that these checks passed merely from this document; run them on the checked-out version. Software validation is not epigraphic acceptance.

## Corpus-specific evidence boundaries

Digital entries and components are not independently certified objects. Keep Eteocypriot parts separate from Greek bilingual parallels; do not admit uncertain components or malformed IG XV 1, 150. The 296-label frequency is a conservative selected subset, not a whole-language frequency.

## AI research contract

Read [the individual AI skill](../ai-skill/SKILL.md), [rights-only readiness](RIGHTS-ONLY-READINESS.md), and [residual blocker ledger](../research/residual-blocker-ledger.json). Check `ai-skill/generated/source-state.json` for the commit represented by any generated AI bundle. Canonical records take precedence over generated summaries. Preserve source attribution, disagreements, uncertainty, negative evidence, exclusions, and record-specific rights. Cross-corpus comparisons require explicit comparability and witness-independence checks; shared fleet membership is not linguistic evidence.

## Human-review boundary

Treat source collation, physical object identification, language classification, and independent specialist adjudication as separate gates. Never mark an unreviewed transcription as expert-accepted or manufacture an attestation. Maintain a traceable link from any proposed correction to its source and reviewer.
