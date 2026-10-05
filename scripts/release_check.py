"""Run offline source replay, tests and generated export integrity checks."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

# Collection interoperability contract: common epistemic safeguards with a
# corpus-specific record profile. This does not equate native evidence units.
contract = json.loads((ROOT / 'schemas' / 'interoperability-contract.json').read_text(encoding='utf-8'))
if contract.get('contract') != 'hawkinsnick-epigraphic-corpus-interoperability' or contract.get('version') != '1.1.0':
    raise SystemExit('Unsupported interoperability contract')
required = {
    'source_attribution_required': True,
    'source_integrity_hash_required': True,
    'uncertainty_preserved': True,
    'unknown_physical_object_count_is_null': True,
    'cross_language_pooling_default': False,
    'cross_project_links_create_independent_witnesses': False,
    'language_or_script_identity_inferred_from_links': False,
    'decipherment_claimed': False,
}
if contract.get('principles') != required or not contract.get('profile'):
    raise SystemExit('Interoperability contract safeguards/profile invalid')


def main():
    commands = [
        ["scripts/audit_source_concordance.py", "--check"],
        ['-c', 'from etec.family import validate_family; errors=validate_family(); print(errors); assert not errors'],
        ['-m', 'etec', 'validate'],
        ['-m', 'unittest', 'discover', '-s', 'tests', '-v'],
        ['-m', 'etec', 'verify-export', 'exports'],
    ]
    for command in commands:
        result = subprocess.run([sys.executable, *command], cwd=ROOT)
        if result.returncode:
            return result.returncode
    print('Release checks passed. Epigraphic review and exhaustive coverage remain separate gates.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
