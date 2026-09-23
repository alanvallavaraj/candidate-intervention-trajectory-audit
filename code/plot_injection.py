"""Plot function-cluster uncertainty for the fresh-instance injection audit."""
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from analyze_injection import read


def main():
    rng=np.random.default_rng(782)
    fig,ax=plt.subplots(figsize=(7.4,3.7),layout='constrained')
    colors={'direct':'#bd664a','inject':'#366e9e'}
    for i,d in enumerate((5,10,20)):
        rows=read(f'injection_{d}d.csv',20*d,d)
        for mode,offset in (('direct',-.08),('inject',.08)):
            by_function=defaultdict(lambda:np.zeros(2))
            for r in rows:
                if r['immediate']<=1e-9:continue
                entry=by_function[r['function']]
                entry[1]+=1
                entry[0]+=r[f'{mode}_late']>r['pass_late']+1e-9
            a=np.asarray(list(by_function.values()))
            rate=a[:,0].sum()/a[:,1].sum()
            draws=np.array([a[rng.integers(len(a),size=len(a))].sum(axis=0)
                            for _ in range(5000)])
            lo,hi=np.quantile(draws[:,0]/draws[:,1],[.025,.975])
            x=i+offset
            ax.errorbar(x,rate,yerr=[[rate-lo],[hi-rate]],fmt='o',markersize=9,
                        capsize=5,color=colors[mode],label=mode.upper() if i==0 else None)
            ax.text(x,hi+.02,f'{int(a[:,0].sum())}/{int(a[:,1].sum())}',
                    ha='center',fontsize=9,color=colors[mode])
    ax.set_xticks([0,1,2],['5D','10D','20D'])
    ax.set_xlim(-.48,2.48)
    ax.set_ylim(.25,.72)
    ax.set_ylabel('Fraction worse after continuation\nconditional on an immediately better candidate')
    ax.set_title('Documented injection does not consistently remove delayed harm')
    ax.legend(frameon=False,ncol=2,loc='upper left')
    ax.grid(axis='y',alpha=.2)
    ax.set_axisbelow(True)
    fig.savefig('injection_harm_comparison.pdf')
    fig.savefig('injection_harm_comparison.png',dpi=200)
    plt.close(fig)


if __name__=='__main__':main()
