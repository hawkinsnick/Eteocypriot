# Method and scientific limits

## Source scope

The snapshot selects 26 candidates from BBAW / TELOTA IG XV 1, acquired via the
immutable Cypriot syllabic Greek v1.0.0 raw-source mirror. The acquisition ledger
preserves both primary-source URLs and transport commit/path references. All
source bytes are hashed and remain unchanged. This source selection is a bounded
starting set, not an exhaustive inventory of Eteocypriot evidence.

25 entries parse into 29 source components. One source response (IG XV 1, 150)
is malformed and remains quarantined without an invented repair. Its valid
header establishes identity and licence; its body is not admitted as parsed data.
The source's printed critical edition, apparatus and objects still need to be
consulted for epigraphic assessment. Digital source fidelity is a software gate,
not proof of the correct ancient reading.

## Component admission

Each source edition's named textpart becomes a component. If no textpart is
present, the component is labelled body. Fragment labels are retained as source
labels, not assumed to be physical faces or independent inscriptions. Components
match translation labels by source part name, never by textual resemblance.

An Eteocypriot label in the matched source translation, supported by the source
title, admits a component as source-attributed Eteocypriot. A question mark next
to that language or an alternative-language title makes it uncertain and excluded
from analytical admission. Questions about object/text type alone do not change
the language status. IG XV 1, 110 is uncertain: the earlier acquisition preparation
misclassified its alternative-language title; this release records the correction.

Bilingual entries IG XV 1, 1, 2 and 7 have Eteocypriot part I and Greek part II,
based on source part labels, the bilingual title and the alphabetic Greek parallel.
Greek parallels are preserved and excluded from Eteocypriot syllabic counts.
The two source parts A and B in IG XV 1, 16 remain two components of one entry.

Source-attributed does not mean independently reviewed or certain in every
epigraphic detail. Eight uncertain components remain visible and excluded.
No language affiliation or translation is inferred from syllabic readability.

## Representations and units

Source syllabic transliteration, Greek alphabetic parallels, modern source
translations and project metadata remain separate. Raw XML is authoritative.
Serialized component XML retains markup; readable text preserves underdots,
brackets, arrows and source line breaks. The readable view is not a diplomatic
rendering engine. No Unicode ancient-sign strings or new linguistic glosses are
manufactured from transliteration.

The native unit is a digital edition entry, containing source components.
object_id and independent_witness_id remain null. Copies of an entry in the
Greek and Eteocypriot projects share source identity and SHA-256; they do not
become independent witnesses. Version numbers measure software milestones,
not completeness, scholarly agreement or decipherment progress.

## Conservative token analysis

Only complete, unannotated source display spans whose hyphen-separated syllabic
labels match the pinned Unicode inventory enter descriptive counts. Brackets,
underdots, incomplete labels, doubled dots and metadata lines remain excluded.
Semantic TEI editorial elements conservatively exclude the whole component's
tokens. This policy can omit surviving signs; it does not establish a census of
ancient sign occurrences, phonetic forms, words or morphemes.

Frequency output applies only to the admitted source subset, with contributing
entry/component IDs and explicit sampling units. Whole-corpus statistics,
translation, linguistic gold and cross-script phonetic inference remain blocked.

## Verification

Validation reconciles membership with the pinned acquisition ledger, verifies
identity/licence/hashes, rejects unknown quarantines and unsafe paths, and replays
all component extraction. Export manifests check file membership and hashes.
Tests exercise bilingual exclusions, uncertainty, source defects and tampering.
Well-formed XML is not automatically validated EpiDoc; no external EpiDoc schema
conformance is claimed by this toolkit.
