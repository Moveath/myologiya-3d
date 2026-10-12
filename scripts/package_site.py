"""Prepare the existing atlas for static hosting without changing its source fragment."""
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
destination = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else root / 'dist'
destination.mkdir(parents=True, exist_ok=True)
for item in (root / 'site').iterdir():
    if item.is_file() and item.name not in ('index.html', 'local.html'):
        shutil.copy2(item, destination / item.name)
subprocess.run([sys.executable, str(root / 'scripts/make_local.py'),
                str(root / 'site/index.html'), str(destination / 'index.html')], check=True)
(destination / '.nojekyll').touch()
print('Static site:', destination)
