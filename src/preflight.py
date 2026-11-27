"""Reproducibility, conformance and speed preflight only. NO registered experimental seeds.

From folder root: python src/preflight.py
Uses only Python standard library. Does not modify the canonical article.
"""
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from safer_cpu import load_config,run_episode


def hashfile(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    output=ROOT/'logs'
    output.mkdir(exist_ok=True)
    config_path=ROOT/'configs'/'02B_FROZEN_DESIGN.json'
    ref_path=ROOT/'reference'/'02B_PROTOCOL_EN.md'
    config=load_config(config_path)
    expected=(ROOT/'configs'/'02B_SHA256.txt').read_text().strip()
    actual=hashfile(config_path)
    if expected != actual:
        raise SystemExit('STOP: ORIGINAL 02B CONFIG HASH CHANGED')
    if config['randomization']['confirmation_locked_and_unopened'] is not True:
        raise SystemExit('STOP: CONFIRMATORY LOCK NOT PRESENT')
    # Functional smoke uses seed OUTSIDE both registered ranges, never published as results.
    smoke_seed=52026
    for r in ('pilot_seeds','confirmatory_seeds'):
        x=config['randomization'][r]
        if x['start']<=smoke_seed<x['start']+x['count']:
            raise SystemExit('STOP: preflight seed falls inside registered experimental seeds')
    tracemalloc.start()
    started=time.perf_counter()
    episode_count=0
    action_count=0
    a2_seen=a3_seen=False
    for world in config['worlds']:
        for budget in config['synthetic_budget_units']:
            for p in ('P0','P1','P2','P3','P4','P5','P6'):
                m,trace=run_episode(config,world,smoke_seed,budget,p)
                if not (m.unique_patient_ids and m.total_cost<=budget and
                        m.n_a2<=len(world['target_masses']) and
                        m.n_a3<=len(world['target_masses'])):
                    raise AssertionError('Smoke integrity failure')
                action_count+=len(trace)
                episode_count+=1
                a2_seen |= m.n_a2>0
                a3_seen |= m.n_a3>0
    elapsed=time.perf_counter()-started
    _,mem_peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    if not (a2_seen and a3_seen and episode_count==70):
        raise AssertionError('Incomplete smoke coverage of action branches')
    report={
        'stage':'02C-0_LOCAL_IMPLEMENTATION_PREFLIGHT',
        'scientific_status':'TESTS_ONLY__NO_PILOT_NO_CONFIRMED_RESULTS_NO_MANUSCRIPT_INSERTION',
        'design_id':config['id'],
        'frozen_design_sha256':actual,
        'reference_protocol_sha256':hashfile(ref_path),
        'code_sha256':hashfile(ROOT/'src'/'safer_cpu.py'),
        'seed_access':{'preflight_seed':smoke_seed,'pilot_seed_range':'SEALED_UNTOUCHED','confirmatory_seed_range':'SEALED_UNTOUCHED'},
        'cpu_only':True,'gpu_required':False,'python':sys.version.split()[0],
        'platform':platform.platform(),'logical_cpus':os.cpu_count(),
        'smoke_episodes':episode_count,'smoke_actions_including_warmstarts':action_count,
        'a2_branch_exercised':a2_seen,'a3_branch_exercised':a3_seen,
        'smoke_total_walltime_seconds':round(elapsed,4),
        'smoke_seconds_per_episode':round(elapsed/episode_count,5),
        'python_tracemalloc_peak_mib':round(mem_peak/1024**2,3),
        'interpretation':'Timing for preflight only; not measured pilot/confirmation runtime nor scientific efficacy.'
    }
    (output/'02C0_PREFLIGHT_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
