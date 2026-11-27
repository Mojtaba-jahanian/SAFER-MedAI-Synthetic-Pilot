#!/usr/bin/env python3
"""Read-only verification of frozen Stage 02C-1 *archived* synthetic evidence."""
from pathlib import Path
from collections import defaultdict
import csv, hashlib, json, gzip, sys
BASE=Path(__file__).resolve().parent

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

lock=json.loads((BASE/'qa/02C1_LOCKED_HASHES.json').read_text())
for key,loc in [('config','configs/02B_FROZEN_DESIGN.json'),('policy_code','src/safer_cpu.py'),('runner_code','src/pilot_02C1.py')]:
    actual=digest(BASE/loc)
    assert actual==lock[key],f'LOCK_MISMATCH: {loc}'
assert (BASE/'configs/02B_SHA256.txt').read_text().strip()==lock['config']
manifest=list(csv.DictReader((BASE/'pilot_02C1/SHA256_MANIFEST.csv').open(newline='')))
assert manifest, 'EMPTY_MANIFEST'
print('Manifest columns:',list(manifest[0]))
for row in manifest:
    # Historical schemas can include path/sha256 or file/hash forms.
    k=next((x for x in ['relative_path','path','file','filename','name'] if x in row),None)
    h=next((x for x in ['sha256','hash','digest'] if x in row),None)
    if not k or not h:
        raise RuntimeError('UNKNOWN_MANIFEST_SCHEMA: '+str(list(row)))
    rel=Path(row[k]);assert not rel.is_absolute() and '..' not in rel.parts
    p=BASE/'pilot_02C1'/rel
    if not p.is_file():p=BASE/rel
    assert p.is_file(),f'MISSING {rel}'
    assert digest(p).lower()==row[h].lower(),f'MISMATCH {rel}'
print('Manifest SHA256 PASS:',len(manifest))

pairs=defaultdict(dict)
rows=0
for seed in range(600000,600100):
    stem=BASE/'pilot_02C1/per_seed'/str(seed)
    met=stem.with_suffix('.metrics.csv');tr=stem.with_suffix('.traces.jsonl.gz');comp=stem.with_suffix('.complete.json')
    assert met.exists() and tr.exists() and comp.exists(),f'MISSING_SEED {seed}'
    complete=json.loads(comp.read_text())
    assert complete['seed']==seed and complete['rows']==70
    assert digest(met)==complete['metrics_sha256'] and digest(tr)==complete['traces_sha256'],f'COMPLETE_HASH_MISMATCH {seed}'
    with gzip.open(tr,'rt',encoding='utf8') as f:
        assert sum(1 for _ in f)==70,f'TRACE_COUNT {seed}'
    with met.open(newline='') as f:
        batch=list(csv.DictReader(f))
    assert len(batch)==70
    rows+=len(batch)
    for r in batch:
        if r['world'] in ('W3_reference_gap','W4_support_gap') and r['policy'] in ('P4','P5') and int(r['budget'])==2600:
            pairs[(r['world'],seed)][r['policy']]=int(r['valid_correct_resolution'].lower()=='true')
assert rows==7000 and len(pairs)==200
assert all(set(v)=={'P4','P5'} for v in pairs.values())
for w,a,b in [('W3_reference_gap',100,100),('W4_support_gap',0,100)]:
    vals=[v for (world,_),v in pairs.items() if world==w]
    assert sum(x['P4'] for x in vals)==a and sum(x['P5'] for x in vals)==b
assert sum(v['P4']-v['P5'] for v in pairs.values())/len(pairs)==-0.5
print('100 seed files, 7000 recorded episodes, W3/W4 primary = -0.50: PASS')
print('This is an archive integrity check, NOT a new simulation or clinical validation.')
