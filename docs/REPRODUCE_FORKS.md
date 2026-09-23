# Reproducing the candidate-intervention audit

Run from this directory with Python 3.12. The experiment used NumPy 2.3.5,
`coco-experiment` 2.8.2, and `cma` 4.5.0. Analysis and figures also need
SciPy and Matplotlib; the cluster bootstrap uses NumPy. COCO/BBOB is deterministic
in this experiment. Installing the exact package versions is recommended.

```bash
python -m pip install numpy==2.3.5 coco-experiment==2.8.2 cma==4.5.0 scipy matplotlib
```

Reproduce the main experiment. Each command uses 24 functions, two *COCO*
instance IDs, seeds 0 and 1, and all three hosts. The main runs have 864
branch rows apiece. They are computationally substantial; outputs are already
included in the package.

```bash
python trajectory_forks.py --functions 1-24 --instances 6-7 --dimensions 5 --seeds 2 --burn 100 --horizon 100 --out trajectory_forks_all24.csv
python trajectory_forks.py --functions 1-24 --instances 8-9 --dimensions 10 --seeds 2 --burn 200 --horizon 200 --out trajectory_forks_10d.csv
python trajectory_forks.py --functions 1-24 --instances 12-13 --dimensions 20 --seeds 2 --burn 400 --horizon 400 --out trajectory_forks_20d.csv
```

Reproduce the independent cap checks, using 96 checkpoints per dimension.
The cap is applied only to the displacement from an original CMA-ES candidate
to a contracted candidate. It is **not** Hansen's full injection procedure.

```bash
python trajectory_forks.py --functions 1-24 --instances 10-11 --dimensions 5 --seeds 2 --burn 100 --horizon 100 --hosts cma --actions pass,contract,contract_clip --out clip_5d.csv
python trajectory_forks.py --functions 1-24 --instances 10-11 --dimensions 10 --seeds 2 --burn 200 --horizon 200 --hosts cma --actions pass,contract,contract_clip --out clip_10d.csv
```

Recreate the analysis and plot:

```bash
python check_forks.py
python fork_analysis.py > fork_analysis.txt
python make_fork_figure.py
```

`trajectory_forks.py` clones a host *before* it proposes a candidate, copies
the host's random generator state and internal adaptation state, and then
executes PASS, contraction and reflection branches. Every branch evaluates one
candidate at its first step, followed by unchanged host proposals for
`horizon - 1` steps. Separate branches genuinely spend additional evaluations.
The PASS and intervention branches start at the same objective value and use
identical random streams until their trajectories diverge. A cloned PASS
replay test is in `check_forks.py`.

Each CSV row records host, function, instance, seed, action, baseline best,
first candidate objective, and best-so-far values after 1, 10, 50, and H
continuation evaluations. The PASS row is paired to the treated row using
`function,dimension,instance,seed,host`. The code never uses the paired PASS
evaluation as information for an online treatment decision.

The primary experiment uses `24 * 2 * 2 * 3 = 288` checkpoint states per
dimension, and `20D` baseline plus `3 * 20D` branch evaluations per state:
806,400 true calls over dimensions 5, 10 and 20. The two cap checks add
another 115,200 calls. These counts include all baseline and diagnostic
calls and exclude Python overhead.

**COCO index mapping:** the `--instances` option is a suite-index range, not
the instance ID displayed in the output. Indices 6–7 correspond to IDs 71–72;
8–9 to 73–74; 10–11 to 75–76; 12–13 to 77–78; and 14–15 to 79–80.
Passing the printed IDs as indices makes COCO ignore the requested filter.

## Native injection follow-up

The follow-up uses **unused instance IDs 79–80** (suite indices 14–15), seeds
0–3, and a complete CMA generation at each checkpoint. `direct` substitutes
the transformed first proposal in `tell`; `inject` supplies the same target
through the documented CMA-ES API, converting the bounded phenotype back to
genotype with the inverse boundary transform. `inject` changes which random
variates generate subsequent proposals; no further interventions occur.

```bash
python cma_injection_audit.py --instances 14-15 --dimension 5 --seeds 4 --burn 104 --horizon 100 --out injection_5d.csv
python cma_injection_audit.py --instances 14-15 --dimension 10 --seeds 4 --burn 200 --horizon 200 --out injection_10d.csv
python cma_injection_audit.py --instances 14-15 --dimension 20 --seeds 4 --burn 408 --horizon 400 --out injection_20d.csv
python analyze_injection.py > injection_analysis.txt
python plot_injection.py
```

`analyze_injection.py` checks the three complete branch rows for each of
576 checkpoint states, checks that the direct and injected candidates have
the same first objective value within floating-point tolerance, and reports
descriptive outcomes and bootstrap intervals resampled by function. The
three runs spent a total of 539,904 true evaluations: 192 checkpoint states
per dimension, each consuming `burn + 3 * horizon` calls. Reported summary
metrics for a single generation of CMA adaptation are descriptive, not a
controlled causal isolation of the adaptation mechanism.
