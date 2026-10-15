"""Read corpus-native evidence through an explicit, checksum-pinned local profile."""
import argparse
import copy
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'research/evidence-query-profile.json'
REPORT = 'analysis/evidence-query-coverage.json'
BOUNDARY = ('These are views of existing source records, not new witnesses or adjudications. '
            'Counts retain their declared native units and must not be summed as unique objects. '
            'Registers may contain project hypotheses or untraced alternatives. '
            'Only explicitly attributed, aligned readings can support an editorial comparison; '
            'no alternative-pair or independent-witness count is inferred by this tool.')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def local(root, relative):
    root = Path(root).resolve()
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('unsafe evidence path: ' + relative)
    target = (root / p).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError('missing or unsafe evidence path: ' + relative)
    return target


def pointer(value, path):
    if path == '':
        return value
    if not isinstance(path, str) or not path.startswith('/'):
        raise ValueError('JSON pointer must be empty or start with /')
    for token in path[1:].split('/'):
        # Reject invalid escapes rather than ambiguously interpreting a locator.
        import re
        if re.search(r'~(?![01])', token):
            raise ValueError('invalid JSON pointer escape')
        token = token.replace('~1', '/').replace('~0', '~')
        if isinstance(value, list):
            if not token.isdigit() or str(int(token)) != token:
                raise ValueError('invalid array pointer')
            value = value[int(token)]
        elif isinstance(value, dict):
            value = value[token]
        else:
            raise ValueError('pointer traverses a scalar')
    return value


def parse(raw, kind):
    text = raw.decode('utf-8')
    if kind == 'text':
        return text
    if kind == 'json':
        return json.loads(text)
    if kind == 'jsonl':
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    if kind == 'csv':
        return list(csv.DictReader(io.StringIO(text)))
    raise ValueError('unsupported artifact format: ' + kind)


class Evidence:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        profile_raw = local(root, PROFILE).read_bytes()
        self.profile_hash = sha(profile_raw)
        self.profile = json.loads(profile_raw)
        if self.profile['format'] != 'corpus-native-evidence-query-v1':
            raise ValueError('unsupported profile format')
        self.artifacts = {}
        for item in self.profile['artifacts']:
            path = item['path']
            if path in self.artifacts:
                raise ValueError('duplicate artifact: ' + path)
            raw = local(root, path).read_bytes()
            if sha(raw) != item['sha256']:
                raise ValueError('source pin mismatch: ' + path)
            self.artifacts[path] = {'spec': item, 'value': parse(raw, item['encoding'])}
        self.collections = {}
        for spec in self.profile['collections']:
            name = spec['name']
            if name in self.collections:
                raise ValueError('duplicate collection: ' + name)
            artifact = self.artifacts[spec['path']]
            selected = pointer(artifact['value'], spec['pointer'])
            if spec.get('singleton', False):
                rows = [selected]
                locations = [spec['pointer']]
            else:
                if not isinstance(selected, list):
                    raise ValueError('collection is not an array: ' + name)
                rows = selected
                locations = [spec['pointer'] + '/' + str(i) for i in range(len(rows))]
            seen = set()
            records = []
            for row, location in zip(rows, locations):
                identity = pointer(row, spec['id_pointer'])
                if isinstance(identity, bool) or not isinstance(identity, (str, int)) or str(identity) == '':
                    raise ValueError('missing/scalar ID: ' + name)
                key = str(identity)
                if key in seen:
                    raise ValueError('duplicate ID within collection: ' + name + ':' + key)
                seen.add(key)
                records.append({'id': key, 'pointer': location, 'value': row})
            self.collections[name] = {'spec': spec, 'records': records}
        for relation in self.profile.get('relations', []):
            if relation['from'] not in self.collections or relation['to'] not in self.collections:
                raise ValueError('relation references unknown collection')

    def provenance(self, path, location=''):
        spec = self.artifacts[path]['spec']
        return {'path': path, 'sha256': spec['sha256'], 'pointer': location,
                'native_artifacts_snapshot_commit': self.profile.get('native_artifacts_snapshot_commit'),
                'role': spec['role'], 'encoding': spec['encoding']}

    def inventory(self, name):
        if name not in self.collections:
            raise ValueError('unknown collection: ' + name)
        collection = self.collections[name]
        return {'collection': name, 'native_unit': collection['spec']['unit'],
                'records': [{'id': r['id'], 'pointer': r['pointer']} for r in collection['records']],
                'provenance': self.provenance(collection['spec']['path'], collection['spec']['pointer'])}

    def coverage(self):
        rows = []
        for name, collection in self.collections.items():
            spec = collection['spec']
            rows.append({'name': name, 'native_unit': spec['unit'], 'record_count': len(collection['records']),
                         'scope': spec['scope'], 'example_ids': [r['id'] for r in collection['records'][:3]],
                         'provenance': self.provenance(spec['path'], spec['pointer'])})
        return {'format': 'corpus-native-evidence-query-coverage-v1', 'repository': self.profile['repository'],
                'profile_sha256': self.profile_hash,
                'implementation_sha256': sha(local(self.root, 'scripts/evidence_query.py').read_bytes()),
                'collections': rows, 'context_resources': [self.provenance(p) for p in self.artifacts],
                'scholarly_limits': self.profile['scholarly_limits'],
                'alternative_pair_count': None, 'independent_witness_count': None,
                'boundary': BOUNDARY}

    def dossier(self, identity, collection_name=None):
        names = [collection_name] if collection_name else list(self.collections)
        if any(name not in self.collections for name in names):
            raise ValueError('unknown collection')
        found = [(name, row) for name in names for row in self.collections[name]['records'] if row['id'] == identity]
        if not found:
            raise ValueError('exact native ID absent from selected views: ' + identity)
        if len(found) != 1:
            raise ValueError('ambiguous ID; supply --collection: ' + identity)
        name, row = found[0]
        spec = self.collections[name]['spec']
        # Context is the collection envelope, not a second source witness.
        doc = self.artifacts[spec['path']]['value']
        context = {k: v for k, v in doc.items() if not isinstance(v, list)} if isinstance(doc, dict) else None
        linked = []
        for relation in self.profile.get('relations', []):
            if relation['from'] != name:
                continue
            source_key = pointer(row['value'], relation['from_pointer'])
            if source_key is None or source_key == '':
                continue
            target = self.collections[relation['to']]
            for other in target['records']:
                if relation['to'] == name and other['pointer'] == row['pointer']:
                    continue
                if source_key == pointer(other['value'], relation['to_pointer']):
                    linked.append({'collection': relation['to'], 'relation': relation['label'],
                                   'join_value': source_key,
                                   'provenance': self.provenance(target['spec']['path'], other['pointer']),
                                   'native_record': copy.deepcopy(other['value'])})
        return {'format': 'corpus-native-evidence-dossier-v1', 'repository': self.profile['repository'],
                'collection': name, 'native_unit': spec['unit'], 'scope': spec['scope'],
                'provenance': self.provenance(spec['path'], row['pointer']),
                'profile_sha256': self.profile_hash, 'native_record': copy.deepcopy(row['value']),
                'collection_context': copy.deepcopy(context), 'explicitly_linked_records': linked,
                'context_resources': [self.provenance(p) for p in self.artifacts],
                'context_resource_scope': 'Corpus-level discovery pointers only; not all resources assert facts about this record.',
                'scholarly_limits': self.profile['scholarly_limits'], 'boundary': BOUNDARY}

    def artifact(self, path, location=''):
        if path not in self.artifacts:
            raise ValueError('artifact is not registered: ' + path)
        return {'provenance': self.provenance(path, location),
                'native_evidence': copy.deepcopy(pointer(self.artifacts[path]['value'], location)),
                'boundary': BOUNDARY}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--coverage', action='store_true')
    mode.add_argument('--record')
    mode.add_argument('--list', metavar='COLLECTION')
    mode.add_argument('--artifact', metavar='REGISTERED_PATH')
    mode.add_argument('--check', action='store_true')
    parser.add_argument('--collection')
    parser.add_argument('--pointer', default='')
    args = parser.parse_args()
    if args.collection and not args.record:
        parser.error('--collection requires --record')
    if args.pointer and not args.artifact:
        parser.error('--pointer requires --artifact')
    try:
        evidence = Evidence()
        if args.check:
            if json.loads(local(ROOT, REPORT).read_bytes()) != evidence.coverage():
                raise ValueError('coverage report replay drift')
            result = {'status': 'PASS_NATIVE_EVIDENCE_REPLAY', 'repository': evidence.profile['repository']}
        elif args.coverage:
            result = evidence.coverage()
        elif args.record:
            result = evidence.dossier(args.record, args.collection)
        elif args.list:
            result = evidence.inventory(args.list)
        else:
            result = evidence.artifact(args.artifact, args.pointer)
    except (ValueError, KeyError, IndexError, OSError) as error:
        parser.exit(2, str(error) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
