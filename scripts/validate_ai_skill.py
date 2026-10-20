#!/usr/bin/env python3
"""Exercise the repository-bound AI skill; no network or scholarly adjudication."""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def safe_file(root, relative):
    root = Path(root).resolve()
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('unsafe skill input: ' + relative)
    target = (root / p).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError('missing skill input: ' + relative)
    return target


def checked_artifacts(root, entries):
    checked = {}
    for entry in entries:
        path = entry['path']
        raw = safe_file(root, path).read_bytes()
        if entry.get('sha256') != digest(raw):
            raise ValueError('unbound or changed skill input: ' + path)
        if 'bytes' in entry and entry['bytes'] != len(raw):
            raise ValueError('skill input size differs: ' + path)
        if path in checked and checked[path] != entry['sha256']:
            raise ValueError('conflicting skill input: ' + path)
        checked[path] = entry['sha256']
    if not checked:
        raise ValueError('empty skill artifact index')
    return checked


def load_module(root, path, name):
    spec = importlib.util.spec_from_file_location(name, safe_file(root, path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_value(root, provenance):
    """Resolve returned provenance independently of the query adapter."""
    raw = safe_file(root, provenance['path']).read_bytes()
    if digest(raw) != provenance['sha256']:
        raise ValueError('dossier source hash mismatch')
    encoding = provenance['encoding']
    text = raw.decode('utf-8')
    if encoding == 'json':
        value = json.loads(text)
    elif encoding == 'jsonl':
        value = [json.loads(line) for line in text.splitlines() if line.strip()]
    elif encoding == 'csv':
        value = list(csv.DictReader(io.StringIO(text)))
    elif encoding == 'text':
        value = text
    else:
        raise ValueError('unsupported source encoding')
    pointer = provenance['pointer']
    if pointer:
        if not pointer.startswith('/'):
            raise ValueError('invalid source pointer')
        for part in pointer[1:].split('/'):
            part = part.replace('~1', '/').replace('~0', '~')
            value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def audit(root=ROOT):
    root = Path(root).resolve()
    skill = safe_file(root, 'ai-skill/SKILL.md').read_text()
    match = re.match(r'\A---\n(.*?)\n---(?:\n|$)', skill, re.S)
    if not match:
        raise ValueError('missing skill frontmatter')
    fields = {}
    for key in ('name', 'description', 'version'):
        m = re.search(r'^' + key + r':\s*(.+)$', match[1], re.M)
        if not m:
            raise ValueError('missing skill metadata: ' + key)
        fields[key] = m[1].strip().strip('"\'')
    if not re.fullmatch(r'[a-z0-9-]{1,64}', fields['name']):
        raise ValueError('invalid skill name')
    manifest = json.loads(safe_file(root, 'ai-skill/manifest.json').read_bytes())
    repository = manifest.get('canonical_project') or manifest.get('repository')
    if not repository or not re.fullmatch(r'hawkinsnick/[A-Za-z0-9-]+', repository):
        raise ValueError('invalid corpus repository identity')
    profile_path = 'research/evidence-query-profile.json'
    if (root / profile_path).exists():
        expected = json.loads((root / profile_path).read_bytes())['repository']
        if expected != repository:
            raise ValueError('skill/native repository identity mismatch')
    else:
        # Egyptian is an independent acquisition corpus, not a factory member.
        if repository != 'hawkinsnick/Egyptian-Hieroglyphic-Corpus':
            raise ValueError('no native evidence profile')
    version = manifest.get('skill_version') or manifest.get('version')
    if fields['version'] != version:
        raise ValueError('skill/manifest version mismatch')
    bundle = json.loads(safe_file(root, 'ai-skill/generated/research-bundle-index.json').read_bytes())
    if manifest.get('master_contract_0_3_1') == 'IMPLEMENTED':
        # These members preserve a native schema/version separate from the fleet skill.
        adapter = json.loads(safe_file(root, 'ai-skill/generated/fleet-contract-index.json').read_bytes())
        if adapter.get('schema_version') != version or adapter.get('repository') != repository:
            raise ValueError('skill/fleet adapter version or identity mismatch')
        checked_artifacts(root, adapter.get('artifacts', []))
    elif bundle.get('skill_version') != version:
        raise ValueError('skill/bundle version mismatch')
    if not re.fullmatch(r'[a-f0-9]{40}', bundle.get('source_commit', '')):
        raise ValueError('missing bundle source commit')
    indexed = checked_artifacts(root, bundle.get('artifacts', []))
    for path in ('ai-skill/SKILL.md', 'ai-skill/manifest.json', 'scripts/validate_ai_skill.py', 'docs/AI-SKILL-VALIDATION.md'):
        if path not in indexed:
            raise ValueError('skill operational input not fingerprinted: ' + path)
    # Run the native contract as well as the independent complete hash check.
    result = subprocess.run([sys.executable, 'ai-skill/scripts/validate_bundle.py'], cwd=root,
                            capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise ValueError('native bundle validation failed: ' + result.stdout + result.stderr)
    examples = []
    missing = '__AI_SKILL_MISSING_RECORD_20261020__'
    if (root / profile_path).exists():
        module = load_module(root, 'scripts/evidence_query.py', 'skill_native_evidence')
        evidence = module.Evidence(root)
        if evidence.profile['repository'] != repository:
            raise ValueError('wrong native repository')
        # Check one actual record from EVERY nonempty declared collection.
        for name, collection in evidence.collections.items():
            if not collection['records']:
                continue
            row = collection['records'][0]
            dossier = evidence.dossier(row['id'], name)
            if dossier['native_record'] != source_value(root, dossier['provenance']):
                raise ValueError('dossier differs from exact source: ' + name)
            if not dossier.get('scholarly_limits') or not dossier.get('boundary'):
                raise ValueError('dossier lost scholarly limits')
            examples.append({'collection': name, 'id': row['id'], 'native_unit': dossier['native_unit'],
                             'provenance': dossier['provenance']})
        if not examples:
            raise ValueError('no retrievable native evidence')
        try:
            evidence.dossier(missing)
        except ValueError:
            pass
        else:
            raise ValueError('missing ID admitted as evidence')
        result = subprocess.run([sys.executable, 'scripts/evidence_query.py', '--record', missing],
                                cwd=root, capture_output=True, text=True, timeout=60)
        if result.returncode != 2 or result.stdout.strip() or 'exact native ID absent' not in result.stderr:
            raise ValueError('missing-ID CLI did not return explicit absence')
        for path in ('scripts/evidence_query.py', 'scripts/research_delivery.py'):
            replay = subprocess.run([sys.executable, path, '--check'], cwd=root,
                                    capture_output=True, text=True, timeout=120)
            if replay.returncode:
                raise ValueError('native replay failed: ' + path + ': ' + replay.stderr)
        scope = 'NATIVE_EVIDENCE_RETRIEVAL'
    else:
        corpus = json.loads(safe_file(root, 'data/manifest.json').read_bytes())
        ids = [r['object_id'] for r in corpus['objects']]
        if not ids or len(ids) != len(set(ids)) or missing in ids:
            raise ValueError('invalid acquisition identity inventory')
        for row in corpus['objects']:
            museum, number = row['object_id'].split(':')
            path = 'data/' + museum + '/' + number + '/record.json'
            raw = safe_file(root, path).read_bytes()
            if json.loads(raw) != row:
                raise ValueError('object lookup differs from manifest')
            if any(row.get(f) is not None for f in ('transcription', 'transliteration', 'translation')):
                raise ValueError('unchecked Egyptian reading admitted')
            examples.append({'collection': 'museum-object-acquisition', 'id': row['object_id'],
                             'native_unit': 'museum object metadata record',
                             'provenance': {'path': path, 'sha256': digest(raw), 'pointer': ''}})
        check = subprocess.run([sys.executable, 'scripts/validate.py'], cwd=root,
                               capture_output=True, text=True, timeout=60)
        if check.returncode:
            raise ValueError('acquisition validation failed: ' + check.stderr)
        scope = 'OBJECT_METADATA_LOOKUP_ONLY_NO_VERIFIED_READINGS'
    return {'format': 'corpus-ai-skill-function-check-v1', 'repository': repository,
            'status': 'PASS_SCOPED_FUNCTIONAL_CHECKS', 'scope': scope,
            'skill_name': fields['name'], 'skill_version': version,
            'skill_sha256': digest(skill.encode()), 'bundle_source_commit': bundle['source_commit'],
            'bundle_sha256': digest(safe_file(root, 'ai-skill/generated/research-bundle-index.json').read_bytes()),
            'indexed_artifact_entries_checked': len(bundle['artifacts']),
            'unique_indexed_paths_checked': len(indexed), 'lookups': examples,
            'missing_id_rejected': True, 'scholarly_acceptance_granted': False,
            'empirical_model_accuracy_established': False,
            'limits': 'Deterministic workflow checks only. Independent model usage exercises are recorded separately; no cross-platform accuracy or scholarly acceptance is inferred.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = audit()
    except (ValueError, OSError, KeyError, subprocess.TimeoutExpired) as error:
        parser.exit(2, str(error) + '\n')
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
