"""Inspect compiled devicetree/Kconfig, including actual inherited board settings."""
import json, pickle, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
west=Path(sys.argv[1]);shield=sys.argv[2];artifact=sys.argv[3]
sys.path.insert(0,str(west/'zephyr/scripts/dts/python-devicetree/src'))
with (west/'build/zephyr/edt.pickle').open('rb') as f: edt=pickle.load(f)
config={}
for line in (west/'build/zephyr/.config').read_text().splitlines():
    if line.startswith('CONFIG_') and '=' in line:
        key,value=line.split('=',1);config[key]=value
pinout=json.loads((root/'hardware/pcb-pinout.json').read_text())
def pin(net):
    p=next(v for v in pinout['gpio'].values() if v['net']==net);return p['port'],p['pin']
def gpio(p):
    labels=p.controller.labels
    port=0 if 'gpio0' in labels else 1 if 'gpio1' in labels else None
    assert port is not None, labels
    return port,p.data['pin']
scan=edt.label2node['rt34_scan'];transform=edt.label2node['rt34_transform'];physical=edt.label2node['rt34_layout']
assert [gpio(v) for v in scan.props['row-gpios'].val]==[pin(n) for n in ['row_top','row_home','row_bottom','row_thumb']]
assert [gpio(v) for v in scan.props['col-gpios'].val]==[pin('col_'+n) for n in ['pinky','ring','middle','index','inner']]
assert len(transform.props['map'].val)==34 and len(set(transform.props['map'].val))==34
assert len(physical.props['keys'].val)==34
for name in ['BASE','NUM','SYM','NAV','MOUSE','SCROLL','SYS']:
    assert len(edt.get_node('/keymap/'+name).props['bindings'].val)==34
central=shield.endswith('_right');trackball=artifact.endswith('-trackball')
assert (config.get('CONFIG_ZMK_SPLIT_ROLE_CENTRAL')=='y')==central
assert transform.props['col-offset'].val==(5 if central else 0)
assert config.get('CONFIG_ZMK_SPLIT')=='y'
assert config.get('CONFIG_ZMK_BATTERY_REPORTING')=='y'
assert config.get('CONFIG_EC11')!='y'
assert config.get('CONFIG_NFCT_PINS_AS_GPIOS')!='y'
assert edt.label2node['qspi'].status=='disabled'
assert edt.label2node['i2c0'].status=='disabled'
assert edt.label2node['spi2'].status=='disabled'
vbatt=edt.label2node['vbatt']
assert vbatt.props['output-ohms'].val==499000 and vbatt.props['full-ohms'].val==1499000
assert gpio(vbatt.props['power-gpios'].val[0])==(0,14)
assert vbatt.props['io-channels'].val[0].data['input']==7
sensor=edt.label2node['trackball'];spi=edt.label2node['spi0'];split=edt.label2node['trackball_split']
assert (sensor.status=='okay')==trackball
assert (config.get('CONFIG_PMW3610')=='y')==trackball
assert gpio(spi.props['cs-gpios'].val[0])==pin('CS')
assert gpio(sensor.props['irq-gpios'].val[0])==pin('MOTION')
assert sensor.props['automouse-layer'].val in [-1,4294967295]
if central:
    assert config.get('CONFIG_ZMK_STUDIO')=='y' and config.get('CONFIG_ZMK_STUDIO_LOCKING')=='y'
    assert split.status=='okay'
    assert edt.label2node['remote_trackball_listener'].status=='okay'
    assert (edt.label2node['trackball_listener'].status=='okay')==trackball
elif trackball:
    assert split.status=='okay' and split.props['device'].val is sensor
    assert edt.label2node['trackball_listener'].status=='disabled'
    assert edt.label2node['remote_trackball_listener'].status=='disabled'
else:
    assert split.status=='disabled'
report={'status':'PASS_COMPILED_CONFIGURATION','artifact':artifact,'central':central,'trackball':trackball,'keys':34,'battery_divider_ohms':[499000,1499000],'matrix_rows':[pin(n) for n in ['row_top','row_home','row_bottom','row_thumb']],'matrix_columns':[pin('col_'+n) for n in ['pinky','ring','middle','index','inner']],'limitations':'Build verification only; USB/bootloader, BLE, trackball direction and battery voltage require hardware tests.'}
(root/'artifacts').mkdir(exist_ok=True)
(root/'artifacts'/'configuration-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
