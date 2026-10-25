# AI skill: use and validation

Canonical skill: [ai-skill/SKILL.md](../ai-skill/SKILL.md).
This is a repository-bound, vendor-neutral research instruction set. Give an AI
both the instructions and the matching corpus files (or repository-file access).
A URL alone does not install the skill. In a browser-only session, open the skill,
then the cited native evidence and rights files; state which execution checks
were not performed. Do not upload restricted source files to a third-party AI
unless the intended use and platform access satisfy the source terms.

## Repeatable check

From a complete repository checkout, use Python 3.10+ (standard library only):

```sh
python scripts/validate_ai_skill.py
```

The check verifies metadata and repository identity, every indexed artifact hash,
the native bundle contract, exact source retrieval and absence handling. It does
not modify the checkout, fetch sources, inspect unavailable images, certify
readings or evaluate accuracy on a particular AI product. The GitHub workflow
`AI skill functional checks` rebuilds fingerprints first, then runs the check and
uploads its JSON receipt; the receipt is scoped to that workflow's source commit.
A native source-only checkout may require `python ai-skill/scripts/build_bundle.py`
if its generated bundle has not yet been published. A rebuild is not a substitute
for reviewing source changes; it records new bytes rather than adjudicating them.

## Example research session

1. Ask the AI: “Use the individual skill. List the available native evidence
   collections and their units. Do not pool them as unique inscriptions.”
2. Ask: “Retrieve the exact record below. Show its source citation, path,
   SHA-256 and pointer; retain uncertainty and source-specific rights.”
3. Ask: “What does this evidence leave unknown? Do not manufacture a translation,
   restored signs, independent witness or accepted reading.”

Run the same retrieval directly:

```sh
python scripts/evidence_query.py --coverage
python scripts/evidence_query.py --list "digital-entries"
python scripts/research_delivery.py --dossier "ETEC-IGXV1-1" --collection "digital-entries"
```

A missing ID returns a nonzero exit status and an explicit rejection, with no
fabricated evidence. This is absence from selected views only. Review drafts are
not completed expert reviews. The functional check retrieves one real record
from every nonempty declared collection and compares it with its exact source.

## Validation boundary — 20 October 2026

Deterministic checks and separate bounded AI usage exercises cover retrieval,
source/uncertainty retention and unsupported-reading handling. They are not a
blinded model benchmark, cross-platform accuracy measurement, source autopsy,
independent scholarly validation or new permission. Existing source, rights,
calibration and expert-review gates remain authoritative.

Master corpus skill: [Linear-A/combined-ai-skill/SKILL.md](https://github.com/hawkinsnick/Linear-A/blob/main/combined-ai-skill/SKILL.md).
Full per-repository audit: [AI-SKILL-VALIDATION-2026-10-20.md](https://github.com/hawkinsnick/Linear-A/blob/main/corpus-factory/AI-SKILL-VALIDATION-2026-10-20.md).

## Adversarial-review follow-up — 25 October 2026

The master [replayable review](https://github.com/hawkinsnick/Master-Corpus-AI-Skill/blob/main/references/hostile-review-2026-10-25.md)
checked **34 declared view rows across 4 collections**, including 0
linked records, at native input `53299e6707e35ad1fcfd1690a7c89ae8d2468196`. These are
retrieval views, including registers and repeated assertions; they are not a
physical population or independently accepted readings. This member contributes
one three-operation compact-evidence case to the 54-task development exercise;
the exercise is not an academic holdout, cross-platform validation or expert review.

The independent source-citation verifier now rejects negative indices, leading-zero
array aliases, malformed escapes, relative/non-string pointers and traversal
through scalar values. Valid escaped object keys, false and null are preserved.
The former verifier accepted Python-style array aliases; the native query adapter
already rejected them. This repairs verification strictness without altering readings.

Run `python -m unittest discover -s scripts -p test_ai_skill_validation.py` and
`python scripts/validate_ai_skill.py` after rebuilding the native bundle.
The master retains raw development outputs, exact source checkpoints and
separate scholarly closure criteria. Source-access and specialist gates remain open.
