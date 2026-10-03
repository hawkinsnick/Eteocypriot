# Eteocypriot research corpus

**1.0.0 — source-attributed components and an offline research toolkit.**

A reproducible, licensed starting corpus for Eteocypriot inscriptions, with
explicit uncertainty and bilingual component boundaries. It is **not an
exhaustive corpus, independently reviewed critical edition, or decipherment**.

## AI research skill

This corpus project includes a vendor-neutral, evidence-first AI research skill in [`ai-skill/`](ai-skill/). The corpus remains the scholarly source of truth; the skill is an interface to it, not a second corpus and not an independent authority.

Researchers using ChatGPT, Claude, Gemini, or another capable model can provide the repository (or its AI-ready bundle) together with [`ai-skill/SKILL.md`](ai-skill/SKILL.md). The skill requires the model to preserve provenance, uncertainty, exclusions, source dependence, rights, and this project's scientific gates. Before substantive use, check [`ai-skill/generated/source-state.json`](ai-skill/generated/source-state.json) and the generated research-bundle index for the corpus commit represented by the AI package.

For questions spanning multiple corpus projects, use the **Combined Corpus Research AI** documented in the Linear A repository under [`combined-ai-skill/`](https://github.com/hawkinsnick/Linear-A/tree/ai-skill-v0.1/combined-ai-skill). It orchestrates the registered individual skills while keeping their evidence models and rights separate. Membership in the combined system does **not** imply linguistic relationship, sign equivalence, chronology, decipherment, or independent replication.

## Evidence coverage

| Measure | Snapshot |
|---|---:|
| Selected primary-source candidate entries | 26 |
| Parsed digital edition entries | 25 |
| Unchanged malformed source responses quarantined | 1 |
| Source-attributed Eteocypriot entries | 17 |
| Source-attributed Eteocypriot components | 18 |
| Uncertain components, excluded from analysis | 8 |
| Greek parallel components, excluded from Eteocypriot analysis | 3 |
| Total source components | 29 |
| Independently reviewed project records | 0 |

These are digital entry/component counts, not independent object or witness
counts. Whole-corpus coverage is unknown. Sources are the 26 candidates selected
from BBAW / TELOTA IG XV 1 and preserved via the Cypriot syllabic Greek v1.0.0
raw-source snapshot. Copies across repositories remain the same source witness.

The source explicitly makes IG XV 1, 110 uncertain; this corrects its earlier
preparation label. IG XV 1, 150 has malformed XML and remains unchanged in
quarantine. In bilingual entries 1, 2 and 7, Eteocypriot part I is separate from
Greek part II. Source fragments A and B in entry 16 remain separate components
of a single digital entry.

## Download and use

Download [1.0.0](https://github.com/hawkinsnick/Eteocypriot/releases/tag/v1.0.0)
and extract the ZIP. Read the JSON, CSV, source XML and documentation directly;
Python is needed only for the commands. Start with the
[admitted components](exports/eteocypriot-components.json),
[component catalogue](exports/components.csv), [audit](exports/audit.json),
and [method](docs/METHOD.md).

Python 3.10+; no third-party packages are required for normal commands. Open a
terminal in the extracted directory:

```sh
python -m etec validate
python -m unittest discover -s tests -v
python -m etec audit
python -m etec search "IG XV 1, 7"
python -m etec frequency
python -m etec export --output my-snapshot
python -m etec verify-export my-snapshot
```

On Windows, `py` can replace `python`; on macOS/Linux, use `python3` if needed.
`python scripts/release_check.py` runs the release checks. All normal commands
work offline. `python -m etec build` reproduces derived records from saved XML.

The frequency command counts 296 conservative clear published syllabic labels
on 11 admitted entries. It excludes uncertain, Greek, damaged, supplied and
unparsed spans. These are subset descriptions, not whole-corpus sign frequencies,
verified ancient word boundaries, translations or linguistic relationship results.

## Source attribution and rights

Primary source: **Inscriptiones Graecae, BBAW / TELOTA**. Scholarly editors:
**Artemis Karnava and Massimo Perna, with Markus Egetmeyer (2020)**. Individual
source translation responsibility is retained, including Klaus Hallof where
supplied. Blank source credit remains unknown.

Raw XML and adapted IG edition content retain upstream **CC BY 4.0**, with a link to every original page. Current project-original software is **PolyForm Noncommercial 1.0.0** and project-owned documentation/annotations are **CC BY-NC 4.0**; Unicode data retain their own terms.
See [NOTICE](NOTICE). No source images, plate drawings or printed-volume scans
are bundled. Greek parallels and modern source glosses are not project-proposed
translations of Eteocypriot.

## Cross-project work

The [family register](research/family/index.json) pins native readiness reports
for the prior projects and preserves their own sampling units and gates. It
permits neither corpus pooling nor automatic transfer of phonetic values.
The [Arkalochori record](research/disputed-cretan-objects.json) keeps that bronze
axe distinct from the small Linear A axes from the same cave and records its
uncertain script classification. It is not an Eteocypriot inscription.

The next dedicated repositories are [Eteocretan](https://github.com/hawkinsnick/Eteocretan)
and [Lycian/Carian](https://github.com/hawkinsnick/Lycian-and-Carian), in that order.
See [the roadmap](docs/ROADMAP.md) and [contribution rules](CONTRIBUTING.md).


## Fleet admission

This corpus participates in the Combined Corpus Research AI fleet. Fleet admission requires the repository's component-specific licensing architecture, its individual `ai-skill` research contract and generated bundle, explicit master-registry membership, and passing member/master validation. Third-party material retains its upstream rights.
