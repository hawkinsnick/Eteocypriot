"""Validate source identity and pinned native status boundaries; no pooling."""
from .core import ROOT, read_json, sha256

def validate_family(root=ROOT):
    errors = []
    try:
        index = read_json(root / 'research/family/index.json')
        names = [m['repository'] for m in index['members']]
        if len(names) != len(set(names)):
            errors.append('Duplicate family repository')
        for member in index['members']:
            path = root / member['saved_report_path']
            if not path.resolve().is_relative_to((root / 'research/family/native').resolve()):
                errors.append('Unsafe native status path')
                continue
            if sha256(path) != member['sha256']:
                errors.append('Native status hash mismatch: ' + member['repository'])
            native = read_json(path)
            gates = native.get('scientific_results', native.get('gates', {'status': native.get('status'), 'final_2_0_allowed': native.get('final_2_0_allowed')}))
            if member['native_gate_fields'] != gates:
                errors.append('Native scientific gates were changed: ' + member['repository'])
        acquisition = read_json(root / 'data/acquisition.json')
        links = read_json(root / 'research/family/shared-source-identities.json')
        if len(links) != len(acquisition) or {r['source_id'] for r in links} != {r['id'] for r in acquisition}:
            errors.append('Shared source identity membership mismatch')
        pinned = {r['id']: r for r in acquisition}
        for link in links:
            row = pinned[link['source_id']]
            n = row['id'].removeprefix('IG XV 1, ')
            expected_etec = 'ETEC-IGXV1-' + n if row['status'] == 'acquired' else None
            expected_csg = 'CSG-IGXV1-' + n if row['status'] == 'acquired' else None
            if link['raw_sha256'] != row['sha256'] or link['transport_snapshot'] != row['transport_snapshot']:
                errors.append('Shared source hash/provenance mismatch')
            if link['Eteocypriot_entry'] != expected_etec or link['Cypriot_syllabic_Greek_entry'] != expected_csg:
                errors.append('Shared source entry identity mismatch')
            if link['independent_witnesses_created'] != 0 or link['unit'] != 'same_digital_edition_source_entry':
                errors.append('Shared source was promoted to an independent witness')
        axe = read_json(root / 'research/disputed-cretan-objects.json')
        if axe['analysis_eligible'] or axe['project_transcribed_occurrences'] is not None or axe['classification_status'] != 'disputed_script_assignment':
            errors.append('Disputed axe was promoted to admitted sign evidence')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    return errors
