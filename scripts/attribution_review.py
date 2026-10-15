"""Replay a bounded attribution review against byte-pinned native evidence.

This checks documentary integrity, not truth, autopsy or scholarly adjudication.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'research/attribution-review.json'
REPORT = 'analysis/attribution-review-audit.json'
CLASSES = {'CLASSIFICATION', 'COUNT_OR_IDENTITY', 'COVERAGE_GAP',
           'SOURCE_ROLE', 'READING_COMPARISON', 'INTERPRETATION',
           'BIBLIOGRAPHY', 'METADATA_COMPARISON', 'REPRESENTATION'}
PAIRS = {'NOT_APPLICABLE', 'PARTIAL_LOCATED_COMPARISON', 'SAME_SOURCE_INTERNAL',
         'FIRST_SIDE_INDIRECT', 'SOURCE_APPARATUS_NOT_FULL_PAIR',
         'UNESTABLISHED_LEGACY_PAIR'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local(root, path):
    p = (root / path).resolve()
    if not p.is_relative_to(root.resolve()) or not p.is_file():
        raise ValueError('unsafe or missing evidence path: ' + path)
    return p


def pointer(value, ptr):
    if ptr and not ptr.startswith('/'):
        raise ValueError('invalid JSON pointer')
    for part in ptr.split('/')[1:]:
        part = part.replace('~1', '/').replace('~0', '~')
        if isinstance(value, list):
            if not part.isdigit() or str(int(part)) != part:
                raise ValueError('invalid array pointer')
            value = value[int(part)]
        else:
            value = value[part]
    return value


class Review:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        raw = local(self.root, MANIFEST).read_bytes()
        self.sha = digest(raw)
        self.manifest = json.loads(raw)
        m = self.manifest
        if m['format'] != 'corpus-attribution-review-v1' or not m['repository'].startswith('hawkinsnick/'):
            raise ValueError('invalid review identity')
        if m['consultation_this_pass'] != 'PINNED_REPOSITORY_EVIDENCE_ONLY':
            raise ValueError('unrecorded primary consultation')
        if m['new_readings_admitted'] != 0 or m['independent_reviews_added'] != 0:
            raise ValueError('review cannot grant scholarly acceptance')
        self.docs = {}
        for item in m['inputs']:
            path = item['path']
            if path in self.docs or path == MANIFEST:
                raise ValueError('duplicate or self-referential input')
            data = local(self.root, path).read_bytes()
            if digest(data) != item['sha256']:
                raise ValueError('stale evidence: ' + path)
            self.docs[path] = json.loads(data)
        self.cases = {}
        covered = set()
        for c in m['cases']:
            key = c['review_id']
            if not key or key in self.cases or c['case_class'] not in CLASSES or c['pair_attribution'] not in PAIRS:
                raise ValueError('duplicate or invalid review case')
            if not c['finding'].strip() or not c['remaining_gap'].strip() or not c['evidence']:
                raise ValueError('missing finding, gap or evidence')
            if c['new_reading_admitted'] is not False or c['independent_review_added'] is not False:
                raise ValueError('unsupported promotion')
            for r in c['evidence']:
                pointer(self.docs[r['path']], r['pointer'])
                covered.add((r['path'], r['pointer']))
            self.cases[key] = c
        for s in m['complete_selections']:
            rows = pointer(self.docs[s['path']], s['pointer'])
            if not isinstance(rows, list) or len(rows) != s['expected_rows']:
                raise ValueError('selection population changed')
            for i in range(len(rows)):
                if (s['path'], s['pointer'] + '/' + str(i)) not in covered:
                    raise ValueError('selected row lacks review')

    def case(self, key):
        c = self.cases[key]
        return {'review': c, 'consultation_this_pass': self.manifest['consultation_this_pass'],
                'evidence': [{**r, 'native_evidence': pointer(self.docs[r['path']], r['pointer'])}
                             for r in c['evidence']]}

    def report(self):
        return {'format': 'corpus-attribution-review-audit-v1',
                'repository': self.manifest['repository'],
                'status': 'PASS_PINNED_DOCUMENTARY_REVIEW_NOT_SCHOLARLY_ACCEPTANCE',
                'manifest_sha256': self.sha,
                'implementation_sha256': digest((self.root/'scripts/attribution_review.py').read_bytes()),
                'input_count': len(self.docs), 'review_case_count': len(self.cases),
                'case_classes': dict(sorted(Counter(c['case_class'] for c in self.cases.values()).items())),
                'pair_attribution_states': dict(sorted(Counter(c['pair_attribution'] for c in self.cases.values()).items())),
                'complete_selections': self.manifest['complete_selections'],
                'literature_exhaustive': False, 'alternative_pair_count': None,
                'independent_witness_count': None, 'new_readings_admitted': 0,
                'independent_reviews_added': 0,
                'consultation_this_pass': self.manifest['consultation_this_pass']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group()
    g.add_argument('--case')
    g.add_argument('--write', action='store_true')
    g.add_argument('--check', action='store_true')
    a = p.parse_args()
    review = Review()
    if a.case:
        result = review.case(a.case)
    else:
        result = review.report()
        output = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
        target = ROOT/REPORT
        if a.write:
            target.parent.mkdir(exist_ok=True)
            target.write_text(output)
        elif a.check and target.read_text() != output:
            raise SystemExit('stale attribution review audit')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
