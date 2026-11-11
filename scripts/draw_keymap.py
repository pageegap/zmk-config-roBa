"""Render the committed ZMK keymap using the same physical layout as Studio.

Run in an isolated environment with requirements-draw.txt installed. GitHub
Actions runs this automatically; no firmware toolchain or West checkout needed.
"""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[1]
KEYMAP = Path('config/roba_tempest_34.keymap')
LAYOUT = Path('boards/shields/roba_tempest_34/roba_tempest_34-layout.dtsi')
CONFIG = Path('keymap_drawer.config.yaml')
OUTPUT = ROOT / 'keymap-drawer'
STEM = 'roba_tempest_34'

def run(args):
    return subprocess.check_output(args, cwd=ROOT, text=True)

def flatten(items):
    return [key for item in items for key in (flatten(item) if isinstance(item, list) else [item])]

def write_svg(source, destination):
    svg = run(['keymap', '-c', str(CONFIG), 'draw', str(source)])
    node = ET.fromstring(svg)
    assert node.tag == '{http://www.w3.org/2000/svg}svg'
    assert node.attrib.get('viewBox') or node.attrib.get('width'), 'Empty SVG drawing'
    destination.write_text(svg)

run(['python3', 'scripts/generate_layout.py', '--check'])
parsed = yaml.safe_load(run(['keymap', '-c', str(CONFIG), 'parse', '-z', str(KEYMAP)]))
assert list(parsed.get('layers', {})) == ['BASE', 'NUM', 'SYM', 'NAV', 'MOUSE', 'SCROLL', 'SYS'], 'Unexpected README layer names'
for layer, keys in parsed['layers'].items():
    parsed['layers'][layer] = flatten(keys)
    assert len(parsed['layers'][layer]) == 34, f'{layer}: expected 34 keys'
for combo in parsed.get('combos', []):
    positions = combo.get('p', combo.get('key_positions', []))
    assert positions and all(0 <= i < 34 for i in positions), 'Invalid combo positions'
# Override any inferred keyboard name; use our generated Tempest geometry.
parsed['layout'] = {'dts_layout': str(LAYOUT)}
OUTPUT.mkdir(exist_ok=True)
yaml_path = OUTPUT / f'{STEM}.yaml'
yaml_path.write_text(yaml.safe_dump(parsed, sort_keys=False, allow_unicode=True))
write_svg(yaml_path, OUTPUT / f'{STEM}.svg')
outputs = [f'{STEM}.yaml', f'{STEM}.svg']
with tempfile.TemporaryDirectory(prefix='rt34-drawer-') as temporary:
    for layer, keys in parsed['layers'].items():
        assert layer.replace('_', '').isalnum(), 'Layer name must be safe for an output filename'
        single = {'layout': parsed['layout'], 'layers': {layer: keys}, 'combos': []}
        # Individual README layer views stay uncluttered. The combined drawing
        # retains every combo in separate panels via the drawing configuration.
        source = Path(temporary) / f'{layer}.yaml'
        source.write_text(yaml.safe_dump(single, sort_keys=False, allow_unicode=True))
        filename = f'{STEM}-{layer}.svg'
        write_svg(source, OUTPUT / filename)
        outputs.append(filename)
inputs = [KEYMAP, LAYOUT, CONFIG, Path('hardware/layout-points.json'),
          Path('scripts/draw_keymap.py'), Path('requirements-draw.txt')]
report = {'generator': 'keymap-drawer', 'version': importlib.metadata.version('keymap-drawer'),
          'layers': list(parsed['layers']), 'keys_per_layer': 34,
          'combos': len(parsed.get('combos', [])), 'outputs': outputs,
          'source_sha256': {str(p): hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in inputs}}
(OUTPUT / f'{STEM}.render.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
