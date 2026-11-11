"""Check nRF52840 UF2 structure and protect XIAO bootloader/settings regions."""
import hashlib, json, struct, sys
from pathlib import Path
p=Path(sys.argv[1]); data=p.read_bytes()
assert data and len(data)%512==0, 'UF2 must contain complete 512-byte blocks'
addresses=[]; numbers=[]; declared_counts=set()
for offset in range(0,len(data),512):
    a,b,flags,addr,size,number,count,family=struct.unpack_from('<8I',data,offset)
    assert (a,b)==(0x0A324655,0x9E5D5157), 'Wrong UF2 magic'
    assert struct.unpack_from('<I',data,offset+508)[0]==0x0AB16F30, 'Wrong UF2 end magic'
    assert flags&0x2000 and not flags&1, 'Expected main-flash family-ID blocks'
    assert family==0xADA52840, 'Wrong MCU family: expected nRF52840'
    assert 0<size<=476 and size%4==0, 'Invalid payload length'
    assert 0x27000<=addr and addr+size<=0xEC000, 'Payload overlaps reserved bootloader or settings flash'
    numbers.append(number); declared_counts.add(count); addresses.append((addr,addr+size))
assert set(numbers)==set(range(len(numbers))) and len(set(numbers))==len(numbers)
assert declared_counts=={len(numbers)}, 'Inconsistent block count'
report={'status':'PASS_UF2_STRUCTURE_AND_FLASH_BOUNDS','file':p.name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'blocks':len(numbers),'family':'nRF52840 / 0xADA52840','flash_start':hex(min(a for a,b in addresses)),'flash_end_exclusive':hex(max(b for a,b in addresses))}
print(json.dumps(report,indent=2))
