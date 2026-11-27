#!/usr/bin/env python3
"""Recalculate recorded prospective pilot P4-vs-P5 contrast without rerunning experiments."""
import csv,collections,pathlib,json
base=pathlib.Path(__file__).resolve().parent
p=base/'pilot_02C1'/'per_seed'
rows=[]
for f in sorted(p.glob('*.metrics.csv')):
    with f.open(newline='',encoding='utf8') as h: rows.extend(csv.DictReader(h))
assert len(rows)==7000, len(rows)
# The CSV labels correspond to the archived Frozen Design; do not treat these as clinical results.
print('Recorded pilot episodes:',len(rows))
pairs=collections.defaultdict(dict)
for r in rows:
    if r['world'] not in ('W3_reference_gap','W4_support_gap') or int(r['budget'])!=2600:continue
    if r['policy'] in ('P4','P5'):
        pairs[(r['world'],int(r['seed']))][r['policy']]=float(r['valid_correct_resolution'].lower()=='true')
assert len(pairs)==200,len(pairs)
for w in ['W3_reference_gap','W4_support_gap']:
    l=[v for (world,seed),v in pairs.items() if world==w]
    assert len(l)==100
    print(w,'P4:',sum(x['P4'] for x in l)/100,'P5:',sum(x['P5'] for x in l)/100)
mean=sum(v['P4']-v['P5'] for v in pairs.values())/200
print('Equal-world average paired effect P4-P5:',mean)
assert abs(mean+0.5)<1e-12
