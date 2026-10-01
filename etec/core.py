from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {'t': 'http://www.tei-c.org/ns/1.0'}
LANG = '{http://www.w3.org/XML/1998/namespace}lang'
LICENCE = 'https://creativecommons.org/licenses/by/4.0/legalcode'

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def local(tag):
    return tag.rsplit('}', 1)[-1]

def render(element):
    """Readable source view; original XML is authoritative for markup semantics."""
    if element is None:
        return ''
    pieces = []
    def visit(node):
        if local(node.tag) == 'lb':
            pieces.append('\n')
        if node.text:
            pieces.append(node.text)
        for child in node:
            visit(child)
            if child.tail:
                pieces.append(child.tail)
    visit(element)
    return '\n'.join(' '.join(line.split()) for line in ''.join(pieces).splitlines() if line.strip())

def text_at(root, xpath):
    el = root.find(xpath, NS)
    return ' '.join(''.join(el.itertext()).split()) if el is not None else None

def source_parts(edition):
    if edition is None:
        raise ValueError('Missing source edition')
    parts = edition.findall('.//t:div[@type="textpart"]', NS)
    if not parts:
        return [('body', edition)]
    labels = [p.get('n') for p in parts]
    if any(n is None for n in labels) or len(labels) != len(set(labels)):
        raise ValueError('Ambiguous source component labels')
    return list(zip(labels, parts))

def language_decision(title, source_label, part, bilingual=False):
    """Language questions outrank entry/type questions and parallel translations."""
    uncertain = bool(re.search(r'eteokyprisch\s*(?:\?|oder)', title.lower()) or
                     re.search(r'eteokyprisch\s*\?', source_label.lower()))
    if 'eteokyprisch' in source_label.lower():
        return {'code': 'uncertain' if uncertain else 'eteocypriot',
                'status': 'source_attributed_uncertain' if uncertain else 'source_attributed',
                'basis': 'Source title and matched translation component label',
                'analysis_eligible': not uncertain}
    if bilingual and 'griechisch' in title.lower():
        if not any(0x370 <= ord(c) <= 0x3ff or 0x1f00 <= ord(c) <= 0x1fff for c in render(part)):
            raise ValueError('Claimed Greek parallel lacks alphabetic Greek source text')
        return {'code': 'grc', 'status': 'source_attributed_parallel',
                'basis': 'Bilingual source title; matched non-Eteocypriot Greek alphabetic component',
                'analysis_eligible': False}
    return {'code': 'und', 'status': 'unassigned', 'basis': 'No admitted component language label', 'analysis_eligible': False}

def tokens(part, text, inventory):
    vocabulary = {s['value']: s['id'] for s in inventory['signs']}
    semantics = any(local(el.tag) in {'supplied', 'unclear', 'gap', 'choice', 'app', 'del', 'add'} for el in part.iter())
    result = []
    for match in re.finditer(r'\S+', text):
        raw = match.group()
        if not re.search('[a-z]', raw) or re.search('[\u0370-\u03ff\u1f00-\u1fff]', raw):
            continue
        candidate = raw[:-1] if raw.endswith(('.', ',', ';', ':')) else raw
        values = candidate.split('-')
        left = text.rfind('\n', 0, match.start()) + 1
        right = text.find('\n', match.end())
        line = text[left:right if right != -1 else len(text)]
        metadata = bool(re.search(r'\b(?:tit|linea|vacat|latus|supra|infra)\b', line))
        clear = bool(values) and all(v in vocabulary for v in values) and not semantics and not metadata
        result.append({'raw': raw, 'start': match.start(), 'end': match.end(),
                       'status': 'conservative_clear' if clear else 'excluded_editorial_or_unparsed',
                       'syllabic_labels': values if clear else [],
                       'unicode_interop_ids': [vocabulary[v] for v in values] if clear else []})
    return result

def parse_record(path, acquisition, inventory):
    raw = path.read_bytes()
    root = ET.fromstring(raw)
    if root.tag != '{http://www.tei-c.org/ns/1.0}TEI':
        raise ValueError('Not a TEI source')
    identifier = text_at(root, './/t:idno[@type="localId"]')
    if identifier != acquisition['id']:
        raise ValueError('Source identifier mismatch')
    licence = root.find('.//t:licence', NS)
    if licence is None or licence.get('target') != LICENCE:
        raise ValueError('Source licence not admitted')
    title = text_at(root, './/t:title') or ''
    if 'eteokyprisch' not in title.lower():
        raise ValueError('Source no longer matches candidate scope')
    edition = root.find('.//t:div[@type="edition"]', NS)
    components = []
    translations = []
    interpretation = []
    tdivs = root.findall('.//t:div[@type="translation"]', NS)
    for t in tdivs:
        payload = {'language': t.get(LANG, '').lower(), 'responsibility': (t.get('resp') or '').strip() or None,
                   'text': render(t), 'xml': ET.tostring(t, encoding='unicode')}
        (interpretation if payload['language'] == 'grc' else translations).append(payload)
    source_id = 'ETEC-IGXV1-' + identifier.removeprefix('IG XV 1, ')
    for label, part in source_parts(edition):
        locator = "div[@type='edition']" + (f"//div[@type='textpart'][@n='{label}']" if label != 'body' else '')
        labels = []
        evidence = []
        for div in tdivs:
            if div.get(LANG, '').lower() == 'grc':
                continue
            candidates = div.findall(f".//t:div[@type='textpart'][@n='{label}']", NS) if label != 'body' else [div]
            for candidate in candidates:
                labels.append(render(candidate))
                evidence.append({'locator': "div[@type='translation']" + (f"//div[@type='textpart'][@n='{label}']" if label != 'body' else ''),
                                 'language': div.get(LANG, '').lower(), 'text': render(candidate)})
        source_label = '\n'.join(labels)
        decision = language_decision(title, source_label, part, 'griechisch' in title.lower())
        readable = render(part)
        components.append({
            'id': source_id + '-' + label, 'source_part': label, 'source_locator': locator,
            'language': decision, 'source_language_evidence': evidence,
            'script': 'Grek' if decision['code'] == 'grc' else 'Cprt',
            'representation': 'published_alphabetic_greek' if decision['code'] == 'grc' else 'published_syllabic_transliteration',
            'text': readable, 'xml': ET.tostring(part, encoding='unicode'),
            'line_labels': [e.get('n') for e in part.iter() if local(e.tag) == 'lb'],
            'direction_markers': sorted(set(c for c in readable if c in '←→')),
            'tokens': tokens(part, readable, inventory) if decision['code'] != 'grc' else [],
            'independent_epigraphic_review': False,
        })
    return {
        'id': source_id, 'source_id': identifier, 'record_unit': 'digital_edition_entry',
        'object_id': None, 'independent_witness_id': None,
        'title': title, 'site': text_at(root, './/t:origPlace'),
        'date_source': text_at(root, './/t:origDate'), 'date_normalized': None,
        'support': text_at(root, './/t:support'), 'provenance_source': text_at(root, './/t:provenance[@type="found"]'),
        'bibliography_source': text_at(root, './/t:div[@type="bibliography"]'),
        'components': components, 'modern_source_translations': translations,
        'greek_source_interpretations': interpretation,
        'source': {'authority': 'Inscriptiones Graecae, BBAW / TELOTA',
                   'url': 'https://telota.bbaw.de/ig/digitale-edition/inschrift/' + urllib.parse.quote(identifier, safe=''),
                   'xml_url': acquisition['url'], 'raw_path': acquisition['path'],
                   'sha256': hashlib.sha256(raw).hexdigest(), 'accessed': acquisition['accessed'],
                   'license': 'CC-BY-4.0', 'license_url': LICENCE,
                   'transport_snapshot': acquisition['transport_snapshot'],
                   'modifications': 'Unchanged raw XML parsed into attributed entry/components; readable whitespace normalized; source language assertions and conservative token index added. No translation proposed.'},
        'review': {'source_fidelity': 'automated_replay', 'independent_epigraphic_review': False},
    }

def build(root=ROOT):
    rows = read_json(root / 'data/acquisition.json')
    inventory = read_json(root / 'data/signs.json')
    records = [parse_record(root / r['path'], r, inventory) for r in rows if r['status'] == 'acquired']
    write_json(root / 'data/records.json', records)
    return records

def audit(root=ROOT):
    records = read_json(root / 'data/records.json')
    acquisition = read_json(root / 'data/acquisition.json')
    components = [c for r in records for c in r['components']]
    return {'version': (root / 'VERSION').read_text().strip(),
            'scope': '26 candidate entries from the frozen IG XV 1 snapshot, not the entire Eteocypriot corpus',
            'candidate_entries': len(acquisition), 'parsed_entries': len(records),
            'quarantined_entries': [r['id'] for r in acquisition if r['status'] == 'quarantined'],
            'source_attributed_eteocypriot_entries': sum(any(c['language']['code'] == 'eteocypriot' for c in r['components']) for r in records),
            'source_attributed_eteocypriot_components': sum(c['language']['code'] == 'eteocypriot' for c in components),
            'uncertain_components': sum(c['language']['code'] == 'uncertain' for c in components),
            'greek_parallel_components': sum(c['language']['code'] == 'grc' for c in components),
            'unassigned_components': sum(c['language']['code'] == 'und' for c in components),
            'component_records': len(components), 'independently_reviewed_records': 0,
            'distinct_objects': None, 'independent_witnesses': None, 'whole_corpus_coverage_fraction': None,
            'gates': {'source_snapshot': 'READY_WITH_QUARANTINE', 'source_attributed_component_subset': 'READY_SCOPED',
                      'whole_corpus_frequency': 'BLOCKED', 'translation_or_decipherment': 'BLOCKED',
                      'linguistic_gold': 'BLOCKED', 'cross_script_phonetic_inference': 'BLOCKED',
                      'exhaustive_critical_edition': 'BLOCKED'}}

def validate(root=ROOT):
    errors = []
    try:
        acquisition = read_json(root / 'data/acquisition.json')
        upstream = read_json(root / 'data/upstream-candidates.json')['candidates']
        inventory = read_json(root / 'data/signs.json')
        records = read_json(root / 'data/records.json')
        if {r['id'] for r in acquisition} != {r['shared_source_identity']['source_id'] for r in upstream} or len(acquisition) != len(upstream):
            errors.append('Candidate membership does not reconcile with pinned upstream ledger')
        if len({r['id'] for r in acquisition}) != len(acquisition):
            errors.append('Duplicate acquisition identifiers')
        pinned = {r['shared_source_identity']['source_id']: r['raw_sha256'] for r in upstream}
        defects = read_json(root / 'data/source-defects.json')
        expected = []
        for row in acquisition:
            path = root / row['path']
            if not path.resolve().is_relative_to((root / 'data/raw').resolve()):
                errors.append('Unsafe source path: ' + row['id'])
                continue
            if sha256(path) != row['sha256'] or row['sha256'] != pinned[row['id']]:
                errors.append('Source hash differs from pinned primary evidence: ' + row['id'])
            if row['status'] == 'quarantined':
                defect = next((d for d in defects if d['id'] == row['id']), None)
                if defect is None or defect['sha256'] != row['sha256'] or defect['parse_error'] != row.get('parse_error'):
                    errors.append('Unregistered source quarantine: ' + row['id'])
                raw = path.read_bytes()
                try:
                    ET.fromstring(raw)
                    errors.append('Quarantined source unexpectedly well formed')
                except ET.ParseError as exc:
                    if str(exc) != row.get('parse_error'):
                        errors.append('Quarantine parse error mismatch')
                end = raw.index(b'</teiHeader>') + len(b'</teiHeader>')
                header = ET.fromstring(raw[:end] + b'</TEI>')
                licence = header.find('.//t:licence', NS)
                if text_at(header, './/t:idno[@type="localId"]') != row['id'] or licence is None or licence.get('target') != LICENCE:
                    errors.append('Quarantine identity/licence mismatch')
            elif row['status'] == 'acquired':
                expected.append(parse_record(path, row, inventory))
            else:
                errors.append('Unadmitted acquisition status: ' + row['id'])
        if records != expected:
            errors.append('Records differ from deterministic source replay')
        ids = [c['id'] for r in records for c in r['components']]
        if len(ids) != len(set(ids)):
            errors.append('Duplicate component IDs')
        ucd = read_json(root / 'data/unicode-evidence.json')
        if [{'codepoint': s['codepoint'], 'name': s['unicode_name']} for s in inventory['signs']] != ucd['characters'] or len(inventory['signs']) != 55:
            errors.append('Unicode inventory differs from pinned source')
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as exc:
        errors.append(str(exc))
    return errors
