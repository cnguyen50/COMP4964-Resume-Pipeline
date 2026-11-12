"""Create a clean deployment artifact containing website files only."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'dist'
if OUTPUT.exists():
    shutil.rmtree(OUTPUT)
shutil.copytree(ROOT / 'site', OUTPUT)
print('Built website in dist/')
