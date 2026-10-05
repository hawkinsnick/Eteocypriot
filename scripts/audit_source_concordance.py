"""Replay source metadata and audit historical candidates without object admission."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from etec.core import parse_record, validate, NS, LICENCE, text_at

PATHS = ['research/source-concordance-register.json',
         'research/historical-concordance.json',
         'research/historical-source-acquisition.json',
         'data/records.json', 'data/acquisition.json', 'data/signs.json',
         'research/coin-source-comparison.json']


def build(root=ROOT):
    root = Path(root)
    registry, historical, sources, records, acquisition, inventory, coins = [
        json.loads((root / p).read_text(encoding='utf-8')) for p in PATHS]
    if validate(root):
        raise ValueError('Native source fidelity invalid')
    acquired = [a for a in acquisition if a['status'] == 'acquired']
    if len(registry['entries']) != len(acquired) or len(records) != len(acquired):
        raise ValueError('Concordance must cover every parsed source entry')
    for row, record, source in zip(registry['entries'], records, acquired):
        raw = root / source['path']
        replay = parse_record(raw, source, inventory)
        if replay != record or hashlib.sha256(raw.read_bytes()).hexdigest() != row['source_xml_sha256']:
            raise ValueError('Concordance lost exact licensed source replay')
        if (row['record_id'], row['source_id'], row['source_xml_path'], row['source_url'], row['source_license']) != (
                record['id'], record['source_id'], source['path'], source['url'], 'CC-BY-4.0'):
            raise ValueError('Source namespace, path or rights changed')
        fields = ['title', 'site', 'date_source', 'support', 'provenance_source', 'bibliography_source']
        if row['reported_metadata'] != {k: record[k] for k in fields}:
            raise ValueError('Source-reported provenance cannot be silently reconciled')
        expected = [{'component_id': c['id'], 'source_part': c['source_part'],
            'source_locator': c['source_locator'], 'source_language_code': c['language']['code'],
            'source_language_status': c['language']['status'], 'line_labels': c['line_labels']}
            for c in record['components']]
        if row['component_targets'] != expected:
            raise ValueError('Component boundaries or source language uncertainty changed')
        if row['physical_object_id'] is not None or row['independent_witness_id'] is not None or row['museum_identity_certified']:
            raise ValueError('Source metadata cannot certify objects or independence')
    known = {r['id'] for r in records}
    inspected = {(p['source_id'], int(p['page_label'])) for p in sources['page_views']
                 if p['inspection_status'] == 'VISUALLY_INSPECTED_SELECTED_METADATA'}
    expected_joins = [('1', 3), ('2', 4), ('3', 5), ('4', 6), ('5', 7), ('8', 11), ('9 bis', 158)]
    joins = historical['candidate_joins']
    if [(j['historical_number'], j['candidate_native_record_id']) for j in joins] != [
            (h, f'ETEC-IGXV1-{n}') for h, n in expected_joins]:
        raise ValueError('Historical numbering is distinct from modern IG numbering')
    for j in joins:
        if (j['historical_source_id'], j['article_page']) not in inspected or j['candidate_native_record_id'] not in known:
            raise ValueError('Candidate lacks inspected source or native target')
        if j['status'] != 'SOURCE_CORRESPONDENCE_CANDIDATE_NOT_CERTIFIED_OBJECT' or any(
                j[k] for k in ['full_sequence_agreement_claimed', 'physical_identity_certified',
                              'independent_confirmation', 'native_object_id_changed']):
            raise ValueError('Historical candidate cannot certify sequence, object or independence')
    for kind in ['source_disagreement_targets', 'selected_critical_assertions', 'discovery_leads']:
        for row in historical[kind]:
            if (row['source_id'], row.get('page', row.get('article_page'))) not in inspected:
                raise ValueError('Historical assertion lacks visually inspected locator')
            if any(row.get(k) for k in ['adjudicated', 'canonical_change_applied', 'native_record_added', 'language_adjudicated']):
                raise ValueError('Historical question or lead cannot become native evidence')
    if [r['disposition'] for r in historical['discovery_leads']] != [
            'HISTORICALLY_ATTRIBUTED_REQUIRES_MODERN_REVIEW', 'AUTHOR_QUESTIONS_LANGUAGE_ATTRIBUTION',
            'COIN_TYPE_WITH_FOUR_REPORTED_SPECIMENS', 'POSSIBLE_OVERLAP_WITH_NATIVE_158',
            'AUTHOR_REGARDS_LANGUAGE_AS_VERY_DOUBTFUL', 'QUALIFIED_HISTORICAL_ATTRIBUTION',
            'AUTHOR_REGARDS_LANGUAGE_AS_DOUBTFUL', 'ANNOUNCEMENT_WITHOUT_ITEM_LEVEL_IDENTITIES']:
        raise ValueError('Discovery scope and historical uncertainty must remain explicit')
    anchors = historical['museum_anchors']
    if [a['inventory'] for a in anchors] != ['AM 1857', 'AM 799'] or any(a['native_identity_certified'] for a in anchors):
        raise ValueError('Museum metadata cannot certify native object joins')
    if any(historical[k] for k in ['canonical_readings_changed', 'physical_objects_certified', 'independent_reviews_added']):
        raise ValueError('Historical work cannot silently promote admission gates')
    if len(inspected) != 13 or any(p['redistributed'] for p in sources['page_views']):
        raise ValueError('Selected inspection scope or source-copy boundary changed')
    if [c['source_id'] for c in coins['entries']] != [f'IG XV 1, {n}' for n in range(85, 93)]:
        raise ValueError('Coin comparison source scope changed')
    coin_hashes = {}
    for row in coins['entries']:
        path = root / row['source_xml_path']
        if not path.resolve().is_relative_to((root / 'research/coin-source-xml').resolve()):
            raise ValueError('Unsafe comparison source path')
        raw = path.read_bytes()
        tree = ET.fromstring(raw)
        license_node = tree.find('.//t:licence', NS)
        parts = tree.findall('.//t:div[@type="edition"]//t:div[@type="textpart"]', NS)
        if hashlib.sha256(raw).hexdigest() != row['sha256'] or len(raw) != row['bytes']:
            raise ValueError('Coin source integrity changed')
        if text_at(tree, './/t:idno[@type="localId"]') != row['source_id'] or text_at(tree, './/t:title') != row['reported_title'] or [p.get('n') for p in parts] != row['source_edition_part_labels']:
            raise ValueError('Coin source metadata or part namespace changed')
        if license_node is None or license_node.get('target') != LICENCE or row['license_url'] != LICENCE or row['license'] != 'CC-BY-4.0':
            raise ValueError('Coin comparison must retain upstream rights')
        if 'eteokyprisch' in raw.decode().lower() or row['explicit_eteocypriot_label_present'] or row['native_record_added'] or row['language_adjudicated']:
            raise ValueError('Unlabelled coin comparison cannot admit language or native reading')
        if row['source_id'] in {a['id'] for a in acquisition}:
            raise ValueError('Comparison sources must remain outside native membership')
        coin_hashes[row['source_xml_path']] = row['sha256']
    candidate = coins['historical_type_candidate']
    if candidate['candidate_ig_source_id'] != 'IG XV 1, 88' or candidate['part_equals_historical_specimen_verified'] or candidate['project_language_adjudicated'] or candidate['independent_confirmation']:
        raise ValueError('Coin type correspondence cannot certify specimen or language')
    return {'format': 'eteocypriot-source-concordance-audit-v1',
        'input_hashes': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in PATHS},
        'additional_comparison_xml_hashes': coin_hashes,
        'parsed_source_entries_replayed': len(records),
        'component_targets': sum(len(r['component_targets']) for r in registry['entries']),
        'historical_candidate_joins': len(joins),
        'source_disagreement_targets': len(historical['source_disagreement_targets']),
        'selected_critical_assertions': len(historical['selected_critical_assertions']),
        'discovery_leads': len(historical['discovery_leads']),
        'museum_metadata_anchors': len(anchors),
        'historical_page_views_acquired': len(sources['page_views']),
        'historical_text_pages_visually_inspected': len(inspected),
        'licensed_coin_comparison_sources': len(coins['entries']),
        'canonical_readings_changed': 0, 'physical_objects_certified': 0,
        'independent_reviews_added': 0,
        'boundary': 'Seven source-correspondence candidates and eight leads do not add seven objects or eight inscriptions. IG, Friedrich/Masson, museum inventories, inscription labels and coin specimens remain distinct namespaces. Native count and language gates remain unchanged.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = ROOT / 'research/source-concordance-audit.json'
    content = json.dumps(build(), indent=2, ensure_ascii=False) + '\n'
    if args.check:
        if target.read_text(encoding='utf-8') != content:
            raise SystemExit('Concordance audit stale')
    else:
        target.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    main()
