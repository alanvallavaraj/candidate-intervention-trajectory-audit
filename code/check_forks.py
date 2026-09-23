"""Sanity checks for clone replay and the released branch CSV files."""
import copy
import csv
from collections import Counter, defaultdict

import cocoex
import numpy as np

from trajectory_forks import Host


def check_replay():
    suite = cocoex.Suite('bbob', '',
                         'function_indices: 1 instance_indices: 6 dimensions: 5')
    problem = next(iter(suite))
    for kind in ('de', 'pso', 'cma'):
        host = Host(kind, problem, 0)
        for _ in range(100 - host.count):
            host.step()
        one, two = copy.deepcopy(host), copy.deepcopy(host)
        first = [one.step() for _ in range(60)]
        second = [two.step() for _ in range(60)]
        np.testing.assert_array_equal(first, second)
        assert one.best == two.best
    print('Clone replay: identical first 60 objective values for DE/PSO/CMA.')


def check_csv(path, dimension, instances, horizon, actions, hosts):
    with open(path, newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 24 * 2 * 2 * len(hosts) * len(actions), path
    assert {int(r['function']) for r in rows} == set(range(1, 25))
    assert {int(r['dimension']) for r in rows} == {dimension}
    assert {int(r['instance']) for r in rows} == set(instances)
    assert {int(r['seed']) for r in rows} == {0, 1}
    assert {r['host'] for r in rows} == set(hosts)
    grouped = defaultdict(dict)
    for row in rows:
        key = (row['host'], row['problem'], row['seed'])
        assert row['action'] not in grouped[key]
        grouped[key][row['action']] = row
        best = [float(row[f'best_h{h}']) for h in (1, 10, 50, horizon)]
        assert all(np.isfinite(v) for v in best)
        assert all(a >= b - 1e-9 for a, b in zip(best, best[1:]))
        assert float(row['baseline_best']) >= best[0] - 1e-9
    assert len(grouped) == 24 * 2 * 2 * len(hosts)
    assert Counter(tuple(sorted(v)) for v in grouped.values()) == {
        tuple(sorted(actions)): len(grouped)
    }
    for branches in grouped.values():
        first_baseline = float(branches['pass']['baseline_best'])
        assert all(float(v['baseline_best']) == first_baseline
                   for v in branches.values())
    print(f'{path}: {len(rows)} complete finite branch records checked.')


if __name__ == '__main__':
    check_replay()
    check_csv('trajectory_forks_all24.csv', 5, (71, 72), 100,
              ('pass', 'contract', 'reflect'), ('de', 'pso', 'cma'))
    check_csv('trajectory_forks_10d.csv', 10, (73, 74), 200,
              ('pass', 'contract', 'reflect'), ('de', 'pso', 'cma'))
    check_csv('trajectory_forks_20d.csv', 20, (77, 78), 400,
              ('pass', 'contract', 'reflect'), ('de', 'pso', 'cma'))
    for d in (5, 10):
        check_csv(f'clip_{d}d.csv', d, (75, 76), 20 * d,
                  ('pass', 'contract', 'contract_clip'), ('cma',))
