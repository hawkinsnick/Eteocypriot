"""Offline Eteocypriot corpus commands; no third-party packages required."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import shutil
import sys

from .core import ROOT, audit, build, read_json, sha256, validate, write_json

def frequencies(records):
    counts = Counter()
    entries = set()
    contributing = []
    for record in records:
        for c in record['components']:
            if not c['language']['analysis_eligible'] or c['language']['code'] != 'eteocypriot':
                continue
            clear = [t for t in c['tokens'] if t['status'] == 'conservative_clear']
            if clear:
                entries.add(record['id'])
                contributing.append(c['id'])
            counts.update(label for t in clear for label in t['syllabic_labels'])
    return {'scope': 'Conservative clear published syllabic labels in source-attributed Eteocypriot components only; not whole-corpus or object-deduplicated counts.',
            'sampling_unit': 'source_component_within_digital_edition_entry',
            'contributing_entries': len(entries), 'contributing_components': contributing,
            'syllabic_label_tokens': sum(counts.values()), 'counts': dict(sorted(counts.items())),
            'linguistic_interpretation': 'None; no meanings, sound reconstructions or decipherment inferred'}

def export(records, output):
    output = Path(output)
    if output.resolve() == ROOT.resolve() or ROOT.resolve().is_relative_to(output.resolve()):
        raise ValueError('Export directory must not contain the repository')
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / 'corpus.json', {'version': (ROOT / 'VERSION').read_text().strip(), 'records': records})
    subset = [{'entry_id': r['id'], 'source_id': r['source_id'], 'source': r['source'], 'component': c}
              for r in records for c in r['components'] if c['language']['code'] == 'eteocypriot' and c['language']['analysis_eligible']]
    write_json(output / 'eteocypriot-components.json', subset)
    write_json(output / 'audit.json', audit())
    write_json(output / 'frequency.json', frequencies(records))
    write_json(output / 'signs.json', read_json(ROOT / 'data/signs.json'))
    fields = ['entry_id', 'source_id', 'component_id', 'source_part', 'language', 'status', 'analysis_eligible', 'site', 'title', 'source_url', 'license']
    with (output / 'components.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for r in records:
            for c in r['components']:
                writer.writerow({'entry_id': r['id'], 'source_id': r['source_id'], 'component_id': c['id'],
                                 'source_part': c['source_part'], 'language': c['language']['code'],
                                 'status': c['language']['status'], 'analysis_eligible': c['language']['analysis_eligible'],
                                 'site': r['site'], 'title': r['title'], 'source_url': r['source']['url'], 'license': r['source']['license']})
    tei = output / 'tei'
    tei.mkdir(exist_ok=True)
    names = set()
    for r in records:
        name = r['id'] + '.xml'
        names.add(name)
        shutil.copyfile(ROOT / r['source']['raw_path'], tei / name)
    for path in tei.glob('*.xml'):
        if path.name not in names:
            path.unlink()
    write_json(output / 'source-defects.json', read_json(ROOT / 'data/source-defects.json'))
    for r in read_json(ROOT / 'data/acquisition.json'):
        if r['status'] == 'quarantined':
            path = output / 'quarantine' / Path(r['path']).name
            path.parent.mkdir(exist_ok=True)
            shutil.copyfile(ROOT / r['path'], path)
    (output / 'ATTRIBUTION.md').write_text((ROOT / 'NOTICE').read_text(), encoding='utf-8')
    files = sorted(p for p in output.rglob('*') if p.is_file() and p.name != 'manifest.json')
    write_json(output / 'manifest.json', {'version': (ROOT / 'VERSION').read_text().strip(), 'files': {p.relative_to(output).as_posix(): sha256(p) for p in files}})

def verify_export(directory):
    directory = Path(directory)
    errors = []
    try:
        manifest = read_json(directory / 'manifest.json')['files']
        actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file() and p.name != 'manifest.json'}
        if actual != set(manifest):
            errors.append('Export membership mismatch')
        for name, digest in manifest.items():
            path = (directory / name).resolve()
            if not path.is_relative_to(directory.resolve()) or not path.is_file():
                errors.append('Unsafe or missing export path: ' + name)
            elif sha256(path) != digest:
                errors.append('Export hash mismatch: ' + name)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ['build', 'validate', 'audit', 'frequency']:
        sub.add_parser(command)
    search = sub.add_parser('search')
    search.add_argument('query')
    ex = sub.add_parser('export')
    ex.add_argument('--output', default='exports')
    ver = sub.add_parser('verify-export')
    ver.add_argument('directory')
    args = parser.parse_args()
    if args.command == 'build':
        print(f'Built {len(build())} entries. Component admission remains source-attributed.')
        return 0
    if args.command in {'validate', 'verify-export'}:
        errors = validate() if args.command == 'validate' else verify_export(args.directory)
        print(json.dumps({'valid': not errors, 'errors': errors}, indent=2))
        return int(bool(errors))
    errors = validate()
    if errors:
        print(json.dumps({'valid': False, 'errors': errors}, indent=2))
        return 1
    records = read_json(ROOT / 'data/records.json')
    if args.command == 'audit':
        result = audit()
    elif args.command == 'frequency':
        result = frequencies(records)
    elif args.command == 'search':
        result = [r for r in records if args.query.casefold() in json.dumps(r, ensure_ascii=False).casefold()]
    elif args.command == 'export':
        export(records, args.output)
        print(f'Exported {len(records)} entries to {args.output}')
        return 0
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    sys.exit(main())
