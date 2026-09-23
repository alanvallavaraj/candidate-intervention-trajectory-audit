"""Paired and function-cluster analysis of the injection follow-up study."""
import csv
from collections import defaultdict

import numpy as np


def read(path, horizon, d):
    with open(path,newline='') as stream:
        rows=list(csv.DictReader(stream))
    assert len(rows)==24*2*4*3, (path,len(rows))
    assert {int(r['function']) for r in rows}==set(range(1,25))
    assert {int(r['instance']) for r in rows}=={79,80}
    assert {int(r['dimension']) for r in rows}=={d}
    grouped=defaultdict(dict)
    for row in rows:
        key=(row['problem'],int(row['seed']))
        assert row['mode'] not in grouped[key]
        grouped[key][row['mode']]=row
        values=[float(row[f'best_h{h}']) for h in (1,10,50,horizon)]
        assert all(a>=b-1e-9 for a,b in zip(values,values[1:]))
    assert len(grouped)==24*2*4
    result=[]
    for (problem,seed),branches in grouped.items():
        assert set(branches)=={'pass','direct','inject'}
        p,a,b=[branches[k] for k in ('pass','direct','inject')]
        assert np.isclose(float(a['first_f']),float(b['first_f']),rtol=1e-12,atol=1e-9),problem
        assert all(float(r['baseline_best'])==float(p['baseline_best']) for r in (a,b))
        r=dict(function=int(p['function']),seed=seed,problem=problem,
               immediate=float(p['first_f'])-float(a['first_f']),
               initial_best=float(p['baseline_best']),
               treated_first=float(a['first_f']),
               pass_late=float(p[f'best_h{horizon}']),
               direct_late=float(a[f'best_h{horizon}']),
               inject_late=float(b[f'best_h{horizon}']))
        for mode,row in (('pass',p),('direct',a),('inject',b)):
            for metric in ('mean_shift_generation','sigma_ratio_generation',
                           'trace_ratio_generation','condition_ratio_generation',
                           'sigma_ratio_final','trace_ratio_final'):
                r[f'{mode}_{metric}']=float(row[metric])
        result.append(r)
    return result


def rate_ci(rows, criterion, outcome, rng):
    by_function=defaultdict(lambda:np.zeros(2))
    for r in rows:
        if criterion(r):
            f=r['function']
            by_function[f][0]+=outcome(r)
            by_function[f][1]+=1
    values=np.asarray(list(by_function.values()))
    numerator=int(values[:,0].sum())
    denom=int(values[:,1].sum())
    draws=np.asarray([values[rng.integers(len(values),size=len(values))].sum(axis=0)
                      for _ in range(5000)])
    intervals=np.quantile(draws[:,0]/draws[:,1],[.025,.975])
    return numerator,denom,intervals


def analyze(rows,label):
    rng=np.random.default_rng(1701)
    selected=lambda r:r['immediate']>1e-9
    subset=[r for r in rows if selected(r)]
    print(label,'states',len(rows),'immediately_better',len(subset))
    new_incumbent=[r for r in subset if r['treated_first']<r['initial_best']-1e-9]
    print('exploratory: new incumbent as well',len(new_incumbent))
    for mode in ('direct','inject'):
        harm=lambda r: r[f'{mode}_late']-r['pass_late']>1e-9
        numerator,denom,intervals=rate_ci(rows,selected,harm,rng)
        print(mode,'harm conditional on better immediate candidate',
              f'{numerator}/{denom}',round(numerator/denom,3),
              'cluster CI',np.round(intervals,3))
        wins=sum(r[f'{mode}_late'] < r['pass_late']-1e-9 for r in rows)
        losses=sum(r[f'{mode}_late'] > r['pass_late']+1e-9 for r in rows)
        print(mode,'PASS paired wins/losses/ties',wins,losses,len(rows)-wins-losses)
        if new_incumbent:
            harmful=sum(harm(r) for r in new_incumbent)
            print(mode,'exploratory harm after new incumbent',
                  f'{harmful}/{len(new_incumbent)}')
    wins=sum(r['inject_late']<r['direct_late']-1e-9 for r in rows)
    losses=sum(r['inject_late']>r['direct_late']+1e-9 for r in rows)
    print('inject vs direct wins/losses/ties',wins,losses,len(rows)-wins-losses)
    rescued=sum(r['direct_late']>r['pass_late']+1e-9 and
                r['inject_late']<=r['pass_late']+1e-9 for r in subset)
    degraded=sum(r['inject_late']>r['pass_late']+1e-9 and
                 r['direct_late']<=r['pass_late']+1e-9 for r in subset)
    print('among immediately better: direct harm rescued / new harm by inject',
          rescued,degraded)
    for metric in ('mean_shift_generation','sigma_ratio_generation',
                   'trace_ratio_generation','condition_ratio_generation',
                   'sigma_ratio_final','trace_ratio_final'):
        medians=[np.median([r[f'{mode}_{metric}'] for r in rows])
                 for mode in ('pass','direct','inject')]
        print('median',metric,'PASS DIRECT INJECT',np.round(medians,3))
    # Paired function bootstrap for absolute differences in conditional harm.
    functions=sorted({r['function'] for r in rows})
    pairs=[]
    for f in functions:
        selected_f=[r for r in subset if r['function']==f]
        if not selected_f:continue
        diff=np.mean([(r['direct_late']>r['pass_late']+1e-9)-
                      (r['inject_late']>r['pass_late']+1e-9)
                      for r in selected_f])
        pairs.append(diff)
    a=np.asarray(pairs)
    draws=np.array([np.mean(a[rng.integers(len(a),size=len(a))]) for _ in range(5000)])
    print('equal-function mean conditional harm DIRECT minus INJECT',
          round(float(a.mean()),3),'cluster CI',np.round(np.quantile(draws,[.025,.975]),3))


if __name__=='__main__':
    entire=[]
    for d in (5,10,20):
        one=read(f'injection_{d}d.csv',20*d,d)
        analyze(one,f'{d}D')
        entire.extend(one)
    analyze(entire,'pooled descriptive')
