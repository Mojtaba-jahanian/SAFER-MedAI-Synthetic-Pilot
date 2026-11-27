"""SAFER prospective synthetic PILOT: 100 seeds x 5 worlds x 2 budgets x 7 policies.

This is a NEW synthetic pilot with preregistered registered pilot seeds ONLY.
Confirmation seeds are NEVER accessed. Execution writes all episodes + traces,
including negative results. No manuscript is altered by this runner.
All dependencies are Python standard library. Resumable per independent seed.
"""
from __future__ import annotations
import argparse, csv, dataclasses, gzip, hashlib, json, os, platform, random, sys, time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from safer_cpu import load_config,run_episode,derived_seed
CFG=ROOT/'configs'/'02B_FROZEN_DESIGN.json'
LOCK=ROOT/'qa'/'02C1_LOCKED_HASHES.json'
POLS=['P0','P1','P2','P3','P4','P5','P6']
CSV_FIELDS=['world','seed','policy','budget','final_state','raw_state','risk_lower','risk_upper',
 'structural_floor','valid_correct_resolution','invalid_certify','false_certify','invalid_high_risk',
 'total_cost','n_a1','n_a2','n_a3','unique_patient_ids','truth_after_stop','truth_inside_final_interval']


def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def check_lock():
    locked=json.loads(LOCK.read_text(encoding='utf-8'))
    paths={'config':CFG,'policy_code':ROOT/'src'/'safer_cpu.py','runner_code':Path(__file__)}
    for key,path in paths.items():
        if sha256_file(path)!=locked[key]: raise RuntimeError(f'STOP: {key} changed after code freeze: {path}')
    orig=ROOT/'configs'/'02B_SHA256.txt'
    if CFG.exists() and CFG.is_file() and orig.read_text().strip()!=locked['config']:
        raise RuntimeError('STOP: original design hash changed')
    c=load_config(CFG)
    if c['randomization']['confirmation_locked_and_unopened'] is not True:
        raise RuntimeError('STOP: confirmatory lock not active')
    if c['id']!='SAFER-J4-02B-SYNTHETIC-CRN-v1.0':raise RuntimeError('STOP: wrong design')
    return c,locked


def atomic_write_bytes(path,payload):
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_bytes(payload)
    os.replace(temp,path)


def atom_csv(path,rows,fields):
    import io
    s=io.StringIO(newline='')
    w=csv.DictWriter(s,fieldnames=fields,lineterminator='\n')
    w.writeheader();w.writerows(rows)
    atomic_write_bytes(path,s.getvalue().encode('utf-8'))


def run_seed(seed):
    c,_=check_lock()
    pilot=c['randomization']['pilot_seeds']
    conf=c['randomization']['confirmatory_seeds']
    if not pilot['start']<=seed<pilot['start']+pilot['count']:
        raise RuntimeError('STOP: only registered pilot seeds are permitted')
    if conf['start']<=seed<conf['start']+conf['count']:
        raise RuntimeError('STOP: confirmatory seed overlap')
    dest=ROOT/'pilot_02C1'/'per_seed';dest.mkdir(parents=True,exist_ok=True)
    csvfile=dest/f'{seed}.metrics.csv'
    tracefile=dest/f'{seed}.traces.jsonl.gz'
    stampfile=dest/f'{seed}.complete.json'
    if stampfile.exists():
        stamp=json.loads(stampfile.read_text(encoding='utf-8'))
        if (stamp.get('rows')==70 and stamp.get('seed')==seed and
            csvfile.exists() and tracefile.exists() and
            sha256_file(csvfile)==stamp.get('metrics_sha256') and
            sha256_file(tracefile)==stamp.get('traces_sha256')):
            return {'seed':seed,'rows':70,'cached':True}
        raise RuntimeError(f'STOP: stale or damaged previous seed output {seed}; investigate, do not silently replace')
    rows=[];trace_records=[]
    for world in c['worlds']:
        for budget in c['synthetic_budget_units']:
            for p in POLS:
                m,trace=run_episode(c,world,seed,budget,p,allow_registered_seeds=True)
                record=dataclasses.asdict(m)
                record['truth_inside_final_interval']=(m.risk_lower-1e-12<=m.truth_after_stop<=m.risk_upper+1e-12)
                if not (m.unique_patient_ids and m.total_cost<=budget):
                    raise RuntimeError(f'STOP: patient/cost violation: {seed}/{world["id"]}/{budget}/{p}')
                rows.append(record)
                trace_records.append({'world':world['id'],'seed':seed,'policy':p,'budget':budget,
                                      'actions':trace,'true_risk_evaluation_only':m.truth_after_stop})
    if len(rows)!=70 or len({(r['world'],r['budget'],r['policy']) for r in rows})!=70:
        raise RuntimeError(f'STOP: incomplete result matrix for seed={seed}')
    atom_csv(csvfile,rows,CSV_FIELDS)
    payload=('\n'.join(json.dumps(t,separators=(',',':'),ensure_ascii=False) for t in trace_records)+'\n').encode('utf-8')
    atomic_write_bytes(tracefile,gzip.compress(payload,compresslevel=6,mtime=0))
    stamp={'seed':seed,'rows':len(rows),'metrics_sha256':sha256_file(csvfile),
           'traces_sha256':sha256_file(tracefile)}
    atomic_write_bytes(stampfile,(json.dumps(stamp,indent=2)+'\n').encode('utf-8'))
    return {'seed':seed,'rows':70,'cached':False}


def percentile_sorted(values,q):
    """Linear interpolated q-quantile; q in [0,1]."""
    x=sorted(values);i=(len(x)-1)*q;lo=int(i);hi=min(len(x)-1,lo+1)
    return x[lo]*(1-(i-lo))+x[hi]*(i-lo)


def analyze(c):
    d=ROOT/'pilot_02C1';dest=d/'per_seed'
    seeds=list(range(c['randomization']['pilot_seeds']['start'],
                     c['randomization']['pilot_seeds']['start']+c['randomization']['pilot_seeds']['count']))
    rows=[]
    for seed in seeds:
        path=dest/f'{seed}.metrics.csv';stamp=dest/f'{seed}.complete.json'
        if not (path.exists() and stamp.exists()):raise RuntimeError(f'Incomplete pilot: missing seed {seed}')
        obj=json.loads(stamp.read_text())
        if sha256_file(path)!=obj['metrics_sha256']:
            raise RuntimeError('STOP: integrity mismatch for seed metrics')
        if sha256_file(dest/f'{seed}.traces.jsonl.gz')!=obj['traces_sha256']:
            raise RuntimeError('STOP: integrity mismatch for action traces')
        with path.open(newline='',encoding='utf-8') as f:
            rows.extend(list(csv.DictReader(f)))
    if len(rows)!=7000:raise RuntimeError(f'STOP: expected exactly 7000 rows, found {len(rows)}')
    if len({(r['world'],r['seed'],r['budget'],r['policy']) for r in rows})!=7000:
        raise RuntimeError('STOP: duplicate or missing unique pilot combinations')
    groups=defaultdict(list)
    for r in rows:groups[(r['world'],int(r['budget']),r['policy'])].append(r)
    summary=[]
    for (world,budget,policy),rr in sorted(groups.items()):
        assert len(rr)==100
        r={'world':world,'budget':budget,'policy':policy,'episodes':len(rr)}
        for field in ('valid_correct_resolution','invalid_certify','false_certify','invalid_high_risk', 'truth_inside_final_interval'):
            r[field+'_rate']=sum(x[field]=='True' for x in rr)/len(rr)
            r[field+'_count']=sum(x[field]=='True' for x in rr)
        for field in ('total_cost','n_a1','n_a2','n_a3'):
            r['mean_'+field]=sum(float(x[field]) for x in rr)/len(rr)
        summary.append(r)
    sumfields=['world','budget','policy','episodes'] + [fld+s for fld in 
        ('valid_correct_resolution','invalid_certify','false_certify','invalid_high_risk','truth_inside_final_interval')
        for s in ('_rate','_count')] + ['mean_'+f for f in ('total_cost','n_a1','n_a2','n_a3')]
    atom_csv(d/'PILOT_ALL70GROUPS.csv',summary,sumfields)
    pri=c['primary_comparison']
    assert pri['worlds']==['W3_reference_gap','W4_support_gap'] and pri['budget']==2600
    bykey={(r['world'],int(r['seed']),int(r['budget']),r['policy']):r for r in rows}
    pairs=[];per_world=[]
    for world in pri['worlds']:
        effects=[]
        for seed in seeds:
            a=bykey[(world,seed,2600,'P4')]['valid_correct_resolution']=='True'
            b=bykey[(world,seed,2600,'P5')]['valid_correct_resolution']=='True'
            diff=int(a)-int(b)
            pairs.append({'world':world,'seed':seed,'P4':int(a),'P5':int(b),'diff_P4_minus_P5':diff})
            effects.append(diff)
        per_world.append({'world':world,'N':len(effects),'mean_difference':sum(effects)/len(effects),
                          'P4_resolved':sum(p['P4'] for p in pairs if p['world']==world),
                          'P5_resolved':sum(p['P5'] for p in pairs if p['world']==world)})
    atom_csv(d/'PILOT_PRIMARY_PAIRED.csv',pairs,['world','seed','P4','P5','diff_P4_minus_P5'])
    observed=sum(r['diff_P4_minus_P5'] for r in pairs)/len(pairs)
    # Independent seed bootstrap within world, 2000 draws. RNG fixed by frozen design id,
    # and no RNG or bootstrap tuning based on observed effect.
    rng=random.Random(derived_seed(293001,c['id'],'pilot_bootstrap'))
    effects={w:[x['diff_P4_minus_P5'] for x in pairs if x['world']==w] for w in pri['worlds']}
    samples=[]
    for _ in range(2000):
        means=[]
        for w in pri['worlds']:
            v=effects[w];means.append(sum(v[rng.randrange(len(v))] for __ in range(len(v)))/len(v))
        samples.append(sum(means)/len(means))
    lower=percentile_sorted(samples,0.05);upper=percentile_sorted(samples,0.95)
    # No peeking/splitting or post-selection; pilot GO threshold predeclared.
    invalid=sum(r['invalid_certify']=='True' for r in rows)
    uniq_fail=sum(r['unique_patient_ids']!='True' for r in rows)
    over=sum(int(r['total_cost'])>int(r['budget']) for r in rows)
    falsec=sum(r['false_certify']=='True' for r in rows)
    falseh=sum(r['invalid_high_risk']=='True' for r in rows)
    coverage=sum(r['truth_inside_final_interval']=='True' for r in rows)/len(rows)
    operational_ok=(invalid==0 and uniq_fail==0 and over==0)
    go=operational_ok and observed>=pri['pilot_min_effect'] and lower>0
    decision='GO_TO_LOCKED_CONFIRMATION' if go else ('STOP_INTEGRITY' if not operational_ok else 'REPOSITION_NEGATIVE_OR_INCONCLUSIVE_PILOT')
    report={'stage':'02C-1_PROSPECTIVE_SYNTHETIC_PILOT','design_id':c['id'],
            'episodes':len(rows),'independent_pilot_seeds':len(seeds),
            'primary':{'worlds':pri['worlds'],'budget':2600,'candidate':'P4','baseline':'P5',
                       'effect_P4_minus_P5':observed,'pilot_90pct_two_sided_bootstrap_CI':[lower,upper],
                       'bootstrap_draws':2000,'bootstrap_resample':'independent seeds within each primary world',
                       'per_world':per_world,'go_threshold_effect':pri['pilot_min_effect']},
            'safety':{'structurally_invalid_certify_count':invalid,
                      'false_certify_vs_synthetic_truth_count':falsec,
                      'invalid_high_risk_vs_synthetic_truth_count':falseh,
                      'patient_uniqueness_violations':uniq_fail,'budget_violations':over,
                      'overall_final_interval_truth_coverage_descriptive':coverage},
            'decision':decision,
            'limits':'Synthetic, newly coded prospective policy, not independent hospital validation or clinical adjudication; positive pilot alone is not confirmatory evidence.',
            'manuscript_updated':False,'confirmatory_seeds_touched':False,
            'code_sha256':sha256_file(ROOT/'src'/'safer_cpu.py'),
            'config_sha256':sha256_file(CFG),'runner_sha256':sha256_file(Path(__file__)),
            'analysis_date_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    atomic_write_bytes(d/'PILOT_DECISION.json',(json.dumps(report,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
    manifest=[]
    for x in sorted(d.rglob('*')):
        if x.is_file() and x.name!='SHA256_MANIFEST.csv':
            manifest.append({'relative_path':x.relative_to(ROOT).as_posix(),'bytes':x.stat().st_size,'sha256':sha256_file(x)})
    atom_csv(d/'SHA256_MANIFEST.csv',manifest,['relative_path','bytes','sha256'])
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['pilot','audit'],default='pilot')
    parser.add_argument('--workers',type=int,default=1)
    args=parser.parse_args()
    c,locked=check_lock()
    if args.mode=='audit':
        # Do not open any registered seed during audit.
        print(json.dumps({'status':'LOCKS_PASS','config_hash':locked['config'],
                          'policy_hash':locked['policy_code'],'runner_hash':locked['runner_code'],
                          'confirmatory_range':'SEALED','pilot_range':'NOT_OPENED'}))
        return
    if not 1<=args.workers<=4: raise RuntimeError('workers must be between 1 and 4')
    seeds=range(c['randomization']['pilot_seeds']['start'],
                c['randomization']['pilot_seeds']['start']+c['randomization']['pilot_seeds']['count'])
    start=time.monotonic();done=0
    print(f'02C1 START: {len(seeds)} seeds / 7000 episodes; workers={args.workers}',flush=True)
    if args.workers==1:
        result_iter=(run_seed(s) for s in seeds)
        for x in result_iter:
            done+=1
            if done%5==0 or done==len(seeds):
                print(f'PROGRESS {done}/100 independent seeds; elapsed={time.monotonic()-start:.1f}s',flush=True)
            if time.monotonic()-start>4*3600:raise RuntimeError('STOP: frozen pilot CPU wall-clock cap exceeded')
    else:
        # Use independent seed-level workers; identical results irrespective of scheduling.
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs=[ex.submit(run_seed,s) for s in seeds]
            for fut in as_completed(futs):
                x=fut.result();done+=1
                if done%5==0 or done==len(seeds):
                    print(f'PROGRESS {done}/100 independent seeds; elapsed={time.monotonic()-start:.1f}s',flush=True)
                if time.monotonic()-start>4*3600:raise RuntimeError('STOP: frozen pilot CPU wall-clock cap exceeded')
    report=analyze(c)
    print('PILOT_COMPLETE',json.dumps({'elapsed_sec':round(time.monotonic()-start,2),'decision':report['decision'],
      'effect':report['primary']['effect_P4_minus_P5'],'pilot_ci':report['primary']['pilot_90pct_two_sided_bootstrap_CI'],
      'episodes':report['episodes'],'invalid_certify':report['safety']['structurally_invalid_certify_count']},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
