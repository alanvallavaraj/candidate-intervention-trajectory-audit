"""Matched-budget audit: raw CMA replacement versus the documented inject API.

This is a diagnostic fork experiment; every branch spends real evaluations.
The first treated candidate is identical in DIRECT and INJECT branches.
The pycma injection API changes assignment of random draws to subsequent
proposals, so comparisons average over multiple independent seeds.
"""
import argparse
import copy
import csv
import math

import cocoex
import numpy as np

from trajectory_forks import Host


def state(es):
    return (float(es.sigma), float(np.linalg.norm(es.mean)),
            float(np.trace(es.C)), float(np.linalg.cond(es.C)))


def study(problem, seed, burn, horizon):
    start = Host('cma', problem, seed)
    assert burn >= start.n and burn % start.n == 0
    for _ in range(burn - start.count):
        start.step()
    assert start.count == burn
    initial = copy.deepcopy(start)
    raw = copy.deepcopy(initial)
    candidate, _, best = raw.propose()  # proposal preview, zero objective calls
    target = np.clip(candidate + .45 * (best - candidate), start.lo, start.hi)
    init_sigma, _, init_trace, init_cond = state(start.es)

    for mode in ('pass', 'direct', 'inject'):
        branch = copy.deepcopy(initial)
        if mode == 'inject':
            # API expects a genotype and must run before ask(), not after.
            genotype = branch.es.gp.geno(
                target, from_bounds=branch.es.boundary_handler.inverse)
            branch.es.inject([genotype], force=True)
        x, _, _ = branch.propose()
        if mode == 'pass':
            np.testing.assert_allclose(x, candidate, rtol=0, atol=1e-10)
        elif mode == 'direct':
            np.testing.assert_allclose(x, candidate, rtol=0, atol=1e-10)
            x = target.copy()
        else:
            np.testing.assert_allclose(x, target, rtol=0, atol=1e-9)
        first = float(problem(x))
        branch.accept(x, first)
        best_at = {1: branch.best}
        generation_state = None
        if branch.n == 1:
            generation_state = (branch.es.mean.copy(), *state(branch.es))
        for h in range(2, horizon + 1):
            branch.step()
            if h in (10, 50, horizon):
                best_at[h] = branch.best
            if h == branch.n:
                generation_state = (branch.es.mean.copy(), *state(branch.es))
        assert generation_state is not None
        mean, sigma, mean_norm, trace, condition = generation_state
        yield dict(problem=problem.id, function=problem.id_function,
                   instance=problem.id_instance, dimension=problem.dimension,
                   seed=seed, mode=mode, popsize=branch.n,
                   baseline_best=start.best, pass_proposal_f=''
                   if mode != 'pass' else first,
                   first_f=first, best_h1=best_at[1],
                   best_h10=best_at[10], best_h50=best_at[50],
                   **{f'best_h{horizon}':best_at[horizon]},
                   mean_shift_generation=float(np.linalg.norm(mean-start.es.mean)),
                   sigma_ratio_generation=sigma/init_sigma,
                   trace_ratio_generation=trace/init_trace,
                   condition_ratio_generation=condition/init_cond,
                   sigma_ratio_final=float(branch.es.sigma/init_sigma),
                   trace_ratio_final=float(np.trace(branch.es.C)/init_trace))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--functions', default='1-24')
    ap.add_argument('--instances', default='14-15')
    ap.add_argument('--dimension', type=int, default=5)
    ap.add_argument('--seeds', type=int, default=4)
    ap.add_argument('--burn', type=int, default=104)
    ap.add_argument('--horizon', type=int, default=100)
    ap.add_argument('--out', default='injection_audit.csv')
    a = ap.parse_args()
    suite = cocoex.Suite('bbob','',f'function_indices: {a.functions} '
                           f'instance_indices: {a.instances} dimensions: {a.dimension}')
    count=0
    with open(a.out,'w',newline='') as f:
        writer=None
        for problem in suite:
            for seed in range(a.seeds):
                for record in study(problem,seed,a.burn,a.horizon):
                    if writer is None:
                        writer=csv.DictWriter(f,fieldnames=list(record))
                        writer.writeheader()
                    writer.writerow(record)
                    count+=1
            f.flush()
            print(problem.id,count,flush=True)
    print('DONE',count,'branch records')


if __name__=='__main__':
    main()
