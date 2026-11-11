"""Pre-build checks tying the firmware to the PCB, not just to text snapshots."""
import argparse, json, re, subprocess, sys
from pathlib import Path
from generate_layout import layout, rendered
ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(); parser.add_argument('--pcb-root', type=Path); args = parser.parse_args()
e = json.loads((ROOT/'hardware/pcb-pinout.json').read_text())
if args.pcb_root:
    original = json.loads((args.pcb_root/'electrical.json').read_text())
    for name in ['gpio', 'diode_direction', 'sensor_connector', 'reset_connector']:
        assert e[name] == original[name], f'Firmware hardware snapshot differs from PCB: {name}'
    proc = subprocess.run(['node', '-e', '''const fs=require('fs'),yaml=require('js-yaml');const ps=yaml.safeLoad(fs.readFileSync('output/points/points.yaml','utf8'));process.stdout.write(JSON.stringify(Object.fromEntries(Object.entries(ps).filter(([,v])=>v.meta.tags.includes('switch')).map(([n,v])=>[n,{x:v.x,y:v.y,r:v.r,row:v.meta.row_net,column:v.meta.column_net}]))));'''],cwd=args.pcb_root,check=True,capture_output=True,text=True)
    assert json.loads(proc.stdout)==json.loads((ROOT/'hardware/layout-points.json').read_text()), 'Physical layout differs from PCB points'
assert (ROOT/'boards/shields/roba_tempest_34/roba_tempest_34-layout.dtsi').read_text()==rendered()
assert len(layout())==34
text=(ROOT/'boards/shields/roba_tempest_34/roba_tempest_34.dtsi').read_text()
text=re.sub(r'//[^\n]*','',text)
coords=[tuple(map(int,m)) for m in re.findall(r'RC\((\d+),(\d+)\)',text)]
expected=[(row,col) for row in range(3) for col in list(range(5))+list(range(9,4,-1))]+[(3,3),(3,4),(3,9),(3,8)]
assert coords==expected and len(set(coords))==34
for side in ['left','right']:
    columns=[c-(5 if side=='right' else 0) for _,c in coords if (c>=5)==(side=='right')]
    assert len(columns)==17 and min(columns)==0 and max(columns)==4

def gpios(prop):
    body=re.search(r'\b'+prop+r'\s*=\s*(.*?);',text,re.S).group(1)
    return [(int(a),int(b)) for a,b in re.findall(r'&gpio(\d)\s+(\d+)',body)]
def pin(net):
    p=next(v for v in e['gpio'].values() if v['net']==net);return p['port'],p['pin']
assert gpios('row-gpios')==[pin(n) for n in ['row_top','row_home','row_bottom','row_thumb']]
assert gpios('col-gpios')==[pin('col_'+n) for n in ['pinky','ring','middle','index','inner']]
assert gpios('cs-gpios')==[pin('CS')]
assert gpios('irq-gpios')==[pin('MOTION')]
assert set(re.findall(r'NRF_PSEL\(SPIM_SCK, (\d), (\d+)\)',text))=={tuple(map(str,pin('SCLK')))}
for function in ['MOSI','MISO']:
    assert set(re.findall(r'NRF_PSEL\(SPIM_'+function+r', (\d), (\d+)\)',text))=={tuple(map(str,pin('SDIO')))}
assert 'output-ohms = <499000>' in text and 'full-ohms = <1499000>' in text
assert not re.search(r'&gpio0\s+(9|10)\s',text), 'NFC pads must remain unused'
assert set(pin(v['net']) for v in e['gpio'].values()).isdisjoint({(0,14),(0,31)}), 'Battery ADC/control conflicts with matrix'
k=(ROOT/'config/roba_tempest_34.keymap').read_text()
layers=re.findall(r'\b([A-Z]+)\s*\{\s*bindings\s*=\s*<(.*?)>;',k,re.S)
assert [name for name,_ in layers]==['BASE','NUM','SYM','NAV','MOUSE','SCROLL','SYS']
for name,bindings in layers:
    assert len(re.findall(r'&\w+',bindings))==34, f'{name}: expected 34 bindings'
for target in re.findall(r'&(?:lt|mo|to)\s+(\d+)',k): assert int(target)<len(layers)
macros=dict(re.findall(r'^#define (KEYS_L|KEYS_R|THUMBS) +([^\n]+)',k,re.M))
for seq in re.findall(r'key-positions\s*=\s*<([^>]+)>',k):
    for name,value in macros.items(): seq=seq.replace(name,value)
    assert all(0<=int(v)<34 for v in seq.split())
assert 'sensor-bindings' not in k
assert (ROOT/'config/roBa.keymap').exists(), 'Original user keymap must be retained'
manifest=(ROOT/'config/west.yml').read_text()
assert 'revision: v0.3.0' in manifest
assert 'revision: 5e04553ab803d24405bd45621a41310ea3050e59' in manifest
assert not re.search(r'revision: (main|v0.3-branch)',manifest)
print('PASS: PCB GPIOs, battery divider, mirrored 17+17 matrix, 34 physical keys, 7 keymap layers, combo/layer ranges, dependency pins.')
