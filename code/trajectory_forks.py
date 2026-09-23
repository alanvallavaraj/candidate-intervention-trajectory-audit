"""Paired state-clone audit of candidate replacement in three optimisers.

Every fork is diagnostic: PASS and intervention each spend their own true
objective evaluations. This tests causal effects under common random numbers,
not a budget-neutral online learning algorithm.
"""
import argparse
import copy
import csv
import math

import cma
import cocoex
import numpy as np


class Host:
    def __deepcopy__(self, memo):
        other=object.__new__(Host)
        memo[id(self)]=other
        for key,value in self.__dict__.items():
            setattr(other,key,value if key=='problem' else copy.deepcopy(value,memo))
        return other

    def __init__(self, kind, problem, seed):
        self.kind, self.problem = kind, problem
        self.lo, self.hi = np.asarray(problem.lower_bounds), np.asarray(problem.upper_bounds)
        self.d = problem.dimension
        self.rng = np.random.default_rng(seed)
        self.n = max(8,5*self.d) if kind!='cma' else max(8,int(4+3*math.log(self.d)))
        self.es = None
        if kind=='cma':
            self.es=cma.CMAEvolutionStrategy((self.lo+self.hi)/2,
                        .3*float(np.mean(self.hi-self.lo)),
                        {'bounds':[self.lo.tolist(),self.hi.tolist()],
                         'popsize':self.n,'seed':seed+1,'verbose':-9})
            self.np_state=np.random.get_state()
            self.pop=np.asarray(self._ask_cma())
        else:
            self.pop=self.rng.uniform(self.lo,self.hi,size=(self.n,self.d))
        self.vals=np.array([float(problem(x)) for x in self.pop])
        self.best=float(min(self.vals))
        if kind=='cma':self.es.tell(self.pop.tolist(),self.vals.tolist())
        self.pbest,self.pvals=self.pop.copy(),self.vals.copy()
        self.vel=np.zeros_like(self.pop)
        self.count=self.n

    def _ask_cma(self):
        np.random.set_state(self.np_state)
        proposals=self.es.ask()
        self.np_state=np.random.get_state()
        return proposals

    def propose(self):
        i=(self.count-self.n)%self.n
        self.i=i
        if self.kind=='de':
            parent=self.pop[i].copy()
            others=np.delete(np.arange(self.n),i)
            a,b,c=self.rng.choice(others,3,replace=False)
            donor=self.pop[a]+.7*(self.pop[b]-self.pop[c])
            mask=self.rng.random(self.d)<.9
            mask[int(self.rng.integers(self.d))]=True
            x=np.clip(np.where(mask,donor,parent),self.lo,self.hi)
        elif self.kind=='pso':
            parent=self.pop[i].copy()
            g=self.pbest[int(np.argmin(self.pvals))]
            self.vel[i]=(.7*self.vel[i]+1.4*self.rng.random(self.d)*(self.pbest[i]-parent)
                         +1.4*self.rng.random(self.d)*(g-parent))
            x=np.clip(parent+self.vel[i],self.lo,self.hi)
        else:
            if i==0:
                self.proposals=np.asarray(self._ask_cma())
                self.next_x,self.next_f=[],[]
            x=np.clip(self.proposals[i],self.lo,self.hi)
            parent=self.pop[int(np.argmin(np.linalg.norm(self.pop-x,axis=1)))].copy()
        return x,parent,self.pop[int(np.argmin(self.vals))].copy()

    def accept(self,x,f):
        i=self.i
        if self.kind=='de':
            if f<=self.vals[i]:self.pop[i],self.vals[i]=x,f
        elif self.kind=='pso':
            self.vel[i]=x-self.pop[i]
            self.pop[i],self.vals[i]=x,f
            if f<=self.pvals[i]:self.pbest[i],self.pvals[i]=x,f
        else:
            self.next_x.append(x.copy())
            self.next_f.append(f)
            if i==self.n-1:
                self.es.tell([v.tolist() for v in self.next_x],self.next_f)
                self.pop,self.vals=np.asarray(self.next_x),np.asarray(self.next_f)
        self.best=min(self.best,f)
        self.count+=1

    def step(self,action='pass'):
        x,parent,best=self.propose()
        if action=='contract':x=np.clip(x+.45*(best-x),self.lo,self.hi)
        if action=='contract_clip':
            assert self.kind=='cma'
            proposed=x.copy()
            target=np.clip(x+.45*(best-x),self.lo,self.hi)
            # Bound *intervention displacement* in CMA's native Mahalanobis
            # coordinates. This is a simple fixed-radius safeguard, not a
            # reimplementation of Hansen's full injection procedure.
            diff=self.es.gp.geno(target)-self.es.gp.geno(proposed)
            length=self.es.mahalanobis_norm(diff)
            limit=.5*math.sqrt(self.d)
            x=np.clip(proposed+min(1.,limit/max(1e-12,length))*(target-proposed),
                      self.lo,self.hi)
        if action=='reflect':x=np.clip(parent-.75*(x-parent),self.lo,self.hi)
        f=float(self.problem(x))
        self.accept(x,f)
        return f


def one_problem(problem,seed,burn,horizon,hosts,actions):
    for host_kind in hosts:
        host=Host(host_kind,problem,seed)
        for _ in range(max(0,burn-host.count)):
            host.step()
        assert host.count==burn
        # Clone *before* generation of the treated proposal. The objective is
        # shared and evaluations in all branches are diagnostic.
        initial=copy.deepcopy(host)
        for action in actions:
            branch=copy.deepcopy(initial)
            branch.problem=problem
            first=None
            trajectory={}
            for h in range(1,horizon+1):
                val=branch.step(action if h==1 else 'pass')
                if h==1:first=val
                if h in (1,10,50,horizon):trajectory[h]=branch.best
            yield dict(host=host_kind,problem=problem.id,
                       function=problem.id_function,dimension=problem.dimension,
                       instance=problem.id_instance,seed=seed,action=action,
                       baseline_best=host.best,first_f=first,
                       **{f'best_h{h}':trajectory[h] for h in (1,10,50,horizon)})


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--functions',default='1,3,6,10,15,20')
    ap.add_argument('--instances',default='6-7')
    ap.add_argument('--dimensions',default='5')
    ap.add_argument('--seeds',type=int,default=2)
    ap.add_argument('--burn',type=int,default=100)
    ap.add_argument('--horizon',type=int,default=100)
    ap.add_argument('--out',default='trajectory_forks.csv')
    ap.add_argument('--hosts',default='de,pso,cma')
    ap.add_argument('--actions',default='pass,contract,reflect')
    args=ap.parse_args()
    suite=cocoex.Suite('bbob','',f'function_indices: {args.functions} '
                      f'instance_indices: {args.instances} dimensions: {args.dimensions}')
    rows=[]
    for p in suite:
        for seed in range(args.seeds):
            rows+=list(one_problem(p,seed,args.burn,args.horizon,
                                   args.hosts.split(','),args.actions.split(',')))
        print(p.id,len(rows),flush=True)
    with open(args.out,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0])
        w.writeheader();w.writerows(rows)
    print('DONE',len(rows),'branches',flush=True)


if __name__=='__main__':main()
