"""Descriptive analyses of the paired counterfactual trajectory forks."""
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest


def read(path):
    with Path(path).open(newline='') as f:return list(csv.DictReader(f))


def summarize(path,horizon):
    grouped=defaultdict(dict)
    for r in read(path):
        key=(r['host'],r['problem'],r['seed'])
        grouped[key][r['action']]=r
    sign=lambda x: int(x>1e-9)-int(x < -1e-9)
    records=[]
    for (host,problem,seed),branches in grouped.items():
        assert set(branches)=={'pass','contract','reflect'}
        base=branches['pass']
        for action in ('contract','reflect'):
            treatment=branches[action]
            records.append(dict(host=host,action=action,function=int(base['function']),
                     problem=problem,seed=seed,
                     first=sign(float(base['first_f'])-float(treatment['first_f'])),
                     early=sign(float(base['best_h1'])-float(treatment['best_h1'])),
                     late=sign(float(base[f'best_h{horizon}'])-float(treatment[f'best_h{horizon}']))))
    for host in ('de','pso','cma'):
        for action in ('contract','reflect'):
            s=[r for r in records if r['host']==host and r['action']==action]
            pos=[r for r in s if r['first']>0]
            win=sum(r['late']>0 for r in s)
            loss=sum(r['late']<0 for r in s)
            harmful=sum(r['late']<0 for r in pos)
            p=binomtest(win,win+loss,.5).pvalue if win+loss else 1
            print(Path(path).name,host,action,'n',len(s),
                  'immediate_candidate_better',len(pos),
                  'late_wins_losses_ties',win,loss,len(s)-win-loss,
                  'harm_despite_immediate_better',f'{harmful}/{len(pos)}',
                  'exploratory_sign_test_p',round(p,4))
    # Compare conditional harm within the same function across hosts. Function
    # is the resampling unit (runs within a function are dependent).
    rng=np.random.default_rng(390)
    by_func=defaultdict(list)
    for r in records:
        if r['action']=='contract' and r['first']>0:
            by_func[(r['function'],r['host'])].append(float(r['late']<0))
    functions=sorted({r['function'] for r in records})
    for left,right in (('cma','de'),('cma','pso')):
        paired=[(np.mean(by_func[(f,left)]),np.mean(by_func[(f,right)]))
                for f in functions if by_func[(f,left)] and by_func[(f,right)]]
        arr=np.asarray(paired)
        observed=float(np.mean(arr[:,0]-arr[:,1]))
        bootstrap=np.array([np.mean((arr[:,0]-arr[:,1])[rng.integers(len(arr),size=len(arr))])
                            for _ in range(4000)])
        lo,hi=np.quantile(bootstrap,[.025,.975])
        print(Path(path).name,'conditional_harm_difference',left,'minus',right,
              'functions',len(arr),'mean',round(observed,3),
              'function_cluster_bootstrap_CI',round(float(lo),3),round(float(hi),3))
    return records


if __name__=='__main__':
    summarize('trajectory_forks_all24.csv',100)
    summarize('trajectory_forks_10d.csv',200)
    summarize('trajectory_forks_20d.csv',400)
