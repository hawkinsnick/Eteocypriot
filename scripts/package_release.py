"""Create a deterministic ZIP from tracked release files, never arbitrary local files."""
import hashlib
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    version = (ROOT / 'VERSION').read_text().strip()
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    name = f'Eteocypriot-{version}'
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    destination = output / (name + '.zip')
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in sorted(p for p in paths if p):
            path = ROOT / relative
            if not path.is_file() or path.is_symlink():
                raise ValueError('Invalid release file: ' + relative)
            info = zipfile.ZipInfo(name + '/' + relative, date_time=(2026, 10, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    (output / 'SHA256SUMS').write_text(f'{digest}  {destination.name}\n')
    print(f'{destination.name}: {digest}')

if __name__ == '__main__':
    main()
