# When better candidates hurt search

Reproducibility package for an exploratory manuscript on one-step candidate replacement in differential evolution (DE), particle swarm optimization (PSO), and CMA-ES. **The result is a failure-mode study, not a new state-of-the-art optimizer.** The branch forks spend extra true objective evaluations and cannot be represented as a budget-neutral online algorithm.

## Main findings

On 24 noiseless COCO/BBOB functions at dimensions 5, 10, and 20, contraction produced an immediately lower objective candidate in 267 DE, 257 PSO, and 240 CMA-ES forks. Among those, later best-so-far objective was worse than the unchanged PASS branch in **48/267, 26/257, and 134/240**, respectively. A separate 576-checkpoint CMA-ES check on new instance IDs found delayed harm in **208/478** immediately better candidates under direct replacement and **211/478** under documented `inject()`. Injection beat direct replacement in 277 checkpoints, lost in 273, and tied in 26. The contrast across different hosts does not isolate covariance adaptation, because the hosts visit different states and generate different candidates.

| Path | Contents |
|---|---|
| `paper/main.tex`, `paper/references.bib` | Eight-page research manuscript source, including 43 cited papers. |
| `paper/main.pdf` | Compiled manuscript for inspection. |
| `paper/plos_one/` | PLOS ONE template version with manuscript PDF, two separate 300 dpi TIFF figures, Vancouver bibliography style, and submission notes. |
| `paper/figures/` | PDF figure sources used in the manuscript. |
| `code/` | Experiment, replay checks, analysis, and plotting scripts. |
| `data/processed/` | All main, cap-check and injection branch-level CSV records. |
| `results/` | Exact text analysis outputs regenerated from the released data. |
| `docs/` | Reproduction notes, prior working manuscript, and submission limitations. |

## Quick verification of released data

Python 3.12, NumPy 2.3.5, `coco-experiment` 2.8.2, `cma` 4.5.0, SciPy 1.17.0, and Matplotlib 3.10.8 were used. From the repository root:

```bash
python -m pip install -r requirements.txt
cd data/processed
python ../../code/check_forks.py
python ../../code/fork_analysis.py > ../../results/fork_analysis.txt
python ../../code/analyze_injection.py > ../../results/injection_analysis.txt
```

`check_forks.py` also creates a small deterministic COCO problem and checks cloned PASS replay, so it calls the objective in addition to checking the CSVs. Run the full experiment with the commands in [docs/REPRODUCE.md](docs/REPRODUCE.md). The full fork experiments are computationally substantial: the main study used 806,400 true calls, the cap checks 115,200, and the native-injection follow-up 539,904.

Compile the paper with:

```bash
cd paper
pdflatex -halt-on-error main.tex
bibtex main
pdflatex -halt-on-error main.tex
pdflatex -halt-on-error main.tex
```

The manuscript is a draft: the author must supply affiliation, disclosures, and the journal's template before submission. The current experiment does **not** establish superiority over GPSAF, JANUS, or optimized CMA-ES implementations. Independent audit, additional baselines and target-based/anytime analysis would strengthen a journal submission. See [docs/JOURNAL_SUBMISSION_STRATEGY.md](docs/JOURNAL_SUBMISSION_STRATEGY.md).

For PLOS ONE, use the [PLOS submission folder](paper/plos_one/): upload its `main.pdf` as the manuscript and `Fig1.tif`/`Fig2.tif` separately. The PLOS manuscript includes the required AI-tool disclosure; confirm the title-page contact email and other declarations before submission.

## Citation and integrity

Please cite the individual prior papers listed in `paper/references.bib` rather than treating this package as a peer-reviewed publication. In particular, externally injected CMA-ES points were already studied by Hansen, and generalized surrogate assistance by Blank and Deb. The 2026 preprints cited in the draft are clearly labeled as preprints. The raw CSV rows and scripts allow paired outcomes to be checked without accepting summary claims on trust.
