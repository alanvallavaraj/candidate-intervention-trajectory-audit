# Reproduction protocol

The experiment used Python 3.12 and the pinned packages in `requirements.txt`. Run commands **from the `data/processed` directory**, so data filenames resolve without editing source code. Install packages from the repository root, then `cd data/processed`.

The `--instances` argument selects **COCO suite indices**, not the printed instance IDs. The main indices 6--7, 8--9, and 12--13 correspond to printed IDs 71--72, 73--74, and 77--78. The capped-check indices 10--11 map to IDs 75--76, and native-injection indices 14--15 to IDs 79--80. Passing printed IDs as indices silently changes the experiment.

## Main paired forks

Each dimension combines 24 BBOB functions, two instances, seeds 0 and 1, and three hosts. Each CSV has 864 branch rows. These commands overwrite the released files, so copy them first if preserving the package is important.

```bash
python ../../code/trajectory_forks.py --functions 1-24 --instances 6-7 --dimensions 5 --seeds 2 --burn 100 --horizon 100 --out trajectory_forks_all24.csv
python ../../code/trajectory_forks.py --functions 1-24 --instances 8-9 --dimensions 10 --seeds 2 --burn 200 --horizon 200 --out trajectory_forks_10d.csv
python ../../code/trajectory_forks.py --functions 1-24 --instances 12-13 --dimensions 20 --seeds 2 --burn 400 --horizon 400 --out trajectory_forks_20d.csv
```

The experiment clones the full host state before it proposes one candidate, including host adaptation and random-generator state. PASS, contraction and reflection each evaluate a first proposal and continue for `horizon - 1` more ordinary objective calls. A baseline consumes `20D` evaluations and the three branches another `3*20D` each checkpoint; total 806,400 calls over the three dimensions. The extra branches are *diagnostic* calls.

## Fixed cap sensitivity check

```bash
python ../../code/trajectory_forks.py --functions 1-24 --instances 10-11 --dimensions 5 --seeds 2 --burn 100 --horizon 100 --hosts cma --actions pass,contract,contract_clip --out clip_5d.csv
python ../../code/trajectory_forks.py --functions 1-24 --instances 10-11 --dimensions 10 --seeds 2 --burn 200 --horizon 200 --hosts cma --actions pass,contract,contract_clip --out clip_10d.csv
```

These add 115,200 true calls. The cap applies only to contraction displacement and should not be confused with Hansen's full native injection method.

## Fresh-instance native injection audit

```bash
python ../../code/cma_injection_audit.py --instances 14-15 --dimension 5 --seeds 4 --burn 104 --horizon 100 --out injection_5d.csv
python ../../code/cma_injection_audit.py --instances 14-15 --dimension 10 --seeds 4 --burn 200 --horizon 200 --out injection_10d.csv
python ../../code/cma_injection_audit.py --instances 14-15 --dimension 20 --seeds 4 --burn 408 --horizon 400 --out injection_20d.csv
```

Each checkpoint has PASS, direct substitution into `tell()`, and the same contracted first target inserted with the documented `inject()` API before `ask()`. The bounded phenotype is converted to genotype with the boundary inverse. No additional interventions follow. The audit adds 539,904 true calls including baselines and branches. Injection alters later random variate assignment; the two treated branches should not be treated as identical later proposals.

## Validate outputs and regenerate summaries

```bash
python ../../code/check_forks.py
python ../../code/fork_analysis.py > ../../results/fork_analysis.txt
python ../../code/analyze_injection.py > ../../results/injection_analysis.txt
python ../../code/make_fork_figure.py
python ../../code/plot_injection.py
```

The last two scripts write figures to the current working directory. Copy their PDFs into `paper/figures/` if rebuilding the paper. The original figure PDFs are already present there. The analysis checks complete rows, cohort sizes, paired first candidate equality in the injection audit and monotonicity of best-so-far values. Bootstrap resampling uses functions as clusters and fixed RNG seeds. Pooled rates are descriptive for the specified 24 functions and are not independent-instance generalization estimates.
