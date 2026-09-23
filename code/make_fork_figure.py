"""Publication-style plot of paired-fork conditional harm rates."""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


DATA=((5,'trajectory_forks_all24.csv',100),
      (10,'trajectory_forks_10d.csv',200),
      (20,'trajectory_forks_20d.csv',400))
HOSTS=('de','pso','cma')
COLORS=('#4363a5','#40a78b','#c65a4a')


def main(plos=False):
    rng=np.random.default_rng(534)
    fig,ax=plt.subplots(figsize=(7.4,4.5) if plos else (8.3,4.7),layout='constrained')
    for j,(dimension,path,horizon) in enumerate(DATA):
        grouped=defaultdict(dict)
        for row in csv.DictReader(open(path,newline='')):
            grouped[(row['host'],row['problem'],row['seed'])][row['action']]=row
        for k,host in enumerate(HOSTS):
            by_function=defaultdict(lambda:[0,0])
            for (h,problem,seed),traces in grouped.items():
                if h!=host:continue
                p,t=traces['pass'],traces['contract']
                if float(p['first_f'])-float(t['first_f'])<=1e-9:continue
                f=int(p['function'])
                by_function[f][1]+=1
                by_function[f][0]+=(float(p[f'best_h{horizon}'])-
                                    float(t[f'best_h{horizon}']) < -1e-9)
            counts=np.asarray(list(by_function.values()))
            rate=counts[:,0].sum()/counts[:,1].sum()
            draws=np.array([counts[rng.integers(len(counts),size=len(counts))]
                            for _ in range(4000)])
            rates=draws[:,:,0].sum(axis=1)/draws[:,:,1].sum(axis=1)
            lo,hi=np.quantile(rates,[.025,.975])
            xpos=j+(k-1)*.24
            ax.bar(xpos,rate,.205,color=COLORS[k],label=host.upper() if j==0 else None)
            ax.errorbar(xpos,rate,yerr=[[rate-lo],[hi-rate]],fmt='none',
                        ecolor='#20242a',capsize=3,lw=1)
            ax.text(xpos,hi+.014,f"{counts[:,0].sum()}/{counts[:,1].sum()}",
                    ha='center',va='bottom',fontsize=8)
    ax.set_xticks(range(3),[f'{d} dimensions' for d,_,_ in DATA])
    ax.set_ylim(0,.84)
    ax.set_ylabel('Worse best-so-far after continuation\nconditional on better immediate candidate')
    if not plos:
        ax.set_title('Candidate improvement does not ensure trajectory improvement')
    ax.legend(ncol=3,loc='upper left',frameon=False)
    ax.grid(axis='y',alpha=.2)
    ax.set_axisbelow(True)
    if plos:
        out=Path(__file__).resolve().parents[1]/'paper'/'plos_one'/'Fig1.tif'
        fig.savefig(out,dpi=300,pil_kwargs={'compression':'tiff_lzw'})
        with Image.open(out) as im:
            im.convert('RGB').save(out,format='TIFF',compression='tiff_lzw',dpi=(300,300))
    else:
        fig.savefig('fork_conditional_harm.pdf')
        fig.savefig('fork_conditional_harm.png',dpi=200)
    plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--plos',action='store_true',help='Write PLOS ONE figure TIFF without title')
    main(parser.parse_args().plos)
