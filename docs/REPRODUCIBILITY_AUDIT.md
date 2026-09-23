# Reproducibility audit for the PLOS ONE manuscript

The repository contains the main experiment's three CSVs, two capped-step CSVs, and the fresh-instance CMA-ES injection experiment's three CSVs, along with experiment code, pinned Python dependencies, analysis scripts, figure generators and exact command lines in `docs/REPRODUCE.md`. The raw CSVs record branch-level first objective values and best-so-far values at horizons 1, 10, 50 and the final horizon. They **do not** record every intermediate proposal or every objective evaluation.

Checks performed for this revision:

1. `code/check_forks.py` verified 864 rows per main-dimension file, 288 rows per capped-step file, expected function/instance/seed IDs, complete action sets, finite non-increasing best-so-far values, common baselines, and deterministic PASS replay (identical first 60 evaluations) for DE, PSO and CMA-ES.
2. `code/fork_analysis.py` and `code/analyze_injection.py` were rerun and their complete text outputs matched the released files in `results/` byte for byte. Injection analysis also checks the 576 three-way checkpoint groups, equal first treated fitness within tolerance, and matched baselines.
3. Freshly executed one-problem, one-seed 5D replays of both the main fork protocol (9 branches) and injection protocol (3 branches) matched the released records for every field, exactly or to a numerical tolerance of `1e-12` relative and `1e-8` absolute for floating-point values.
4. The PLOS manuscript PDF compiled with the attached `plos2025.bst`; it retains figure captions while the two plots are separately supplied as RGB, LZW TIFFs at 300 dpi.

The complete approximately 1.46 million-evaluation suite was **not rerun independently** in this audit; the small deterministic replay and the published analysis checks do not substitute for a separate implementation of all hosts. Full reproduction commands and their computational cost are documented in `docs/REPRODUCE.md`. In particular, all 24 functions and the fresh instance IDs come from the same BBOB family.
